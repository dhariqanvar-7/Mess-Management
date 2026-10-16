import os
from datetime import datetime
from functools import wraps
from flask import Flask, render_template, request, redirect, url_for, session
from pymongo import MongoClient
from bson import ObjectId
from dotenv import load_dotenv
from werkzeug.security import check_password_hash

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "messflow-2026")
db = MongoClient(os.getenv("MONGO_URI", "mongodb://localhost:27017"))["mess_db"]
DAYS = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
DAY_ORDER = {day: i for i, day in enumerate(DAYS)}
MEAL_HOURS = {"breakfast": 8, "lunch": 13, "snacks": 17, "dinner": 20}

def get_user():
    return db.users.find_one({"_id": ObjectId(session["uid"])}) if "uid" in session else None

def require_role(role=None):
    def deco(f):
        @wraps(f)
        def wrap(*a, **k):
            u = get_user()
            return redirect(url_for("login")) if (not u or (role and u.get("role") != role)) else f(*a, **k)
        return wrap
    return deco

def get_special_timing(sp):
    """Simple dictionary helper: checks 1-day prior ordering & 12-hour cancel deadline."""
    now = datetime.now()
    today_idx = now.weekday()
    target_idx = DAY_ORDER.get(sp.get("day"), today_idx)
    
    days_ahead = (target_idx - today_idx) % 7
    meal_hour = MEAL_HOURS.get(sp.get("meal", "lunch"), 13)
    hours_left = (days_ahead * 24) + (meal_hour - now.hour)

    return {
        "days_ahead": days_ahead,
        "hours_left": hours_left,
        "can_accept": days_ahead >= 1,       # Must accept at least 1 day prior
        "can_cancel": hours_left > 12        # Can only cancel if > 12 hours remaining
    }

@app.context_processor
def inject_context():
    return {"me": get_user(), "today_name": datetime.now().strftime("%A"), "today_date": datetime.now(), "DAYS": DAYS}

@app.route("/")
def index():
    u = get_user()
    return redirect(url_for("admin_menu" if u.get("role") == "admin" else "student_menu")) if u else redirect(url_for("login"))

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        uid = request.form.get("email", "").strip()
        u = db.users.find_one({"$or": [{"email": uid}, {"username": uid}]})
        if u and check_password_hash(u["password"], request.form.get("password", "")):
            session["uid"] = str(u["_id"])
            return redirect(url_for("index"))
    return render_template("auth.html")

@app.route("/logout")
def logout(): session.clear(); return redirect(url_for("login"))

@app.route("/admin/menu", methods=["GET", "POST"])
@require_role("admin")
def admin_menu():
    if request.method == "POST":
        db.menu.update_one({"day": request.form["day"]}, {"$set": dict(request.form, cost_veg=float(request.form.get("cost_veg", 95)))}, upsert=True)
        return redirect(url_for("admin_menu"))
    m = {d["day"]: d for d in db.menu.find()}
    return render_template("admin_menu.html", rows=[m.get(d, {"day": d, "breakfast": "-", "lunch": "-", "snacks": "-", "dinner": "-", "cost_veg": 95}) for d in DAYS])

@app.route("/student/menu")
@require_role("student")
def student_menu():
    m, today = {d["day"]: d for d in db.menu.find()}, datetime.now().strftime("%A")
    rows = [{"day": d, "is_today": d == today, "cost": m.get(d, {}).get("cost_veg", 95), "breakfast": m.get(d, {}).get("breakfast", "-"),
             "lunch": m.get(d, {}).get("lunch", "-"), "snacks": m.get(d, {}).get("snacks", "-"), "dinner": m.get(d, {}).get("dinner", "-")} for d in DAYS]
    return render_template("student_menu.html", rows=rows, projected=sum(r["cost"] for r in rows) * 4)

@app.route("/admin/specials", methods=["GET", "POST"])
@require_role("admin")
def admin_specials():
    if request.method == "POST":
        data = request.form.to_dict()
        data["price"] = float(data.get("price", 0))
        db.specials.insert_one(data)
        return redirect(url_for("admin_specials"))
    specials = list(db.specials.find())
    for s in specials:
        s["order_count"] = db.special_orders.count_documents({"special_id": s["_id"], "status": {"$ne": "Cancelled"}})
    return render_template("admin_specials.html", specials=specials, total_specials=len(specials), cancel_reqs=list(db.special_orders.find({"status": "Cancel Requested"})))

@app.route("/admin/specials/delete/<sid>", methods=["POST"])
@require_role("admin")
def delete_special(sid):
    db.specials.delete_one({"_id": ObjectId(sid)})
    db.special_orders.delete_many({"special_id": ObjectId(sid)})
    return redirect(url_for("admin_specials"))

@app.route("/admin/specials/cancel-req/<oid>/<dec>", methods=["POST"])
@require_role("admin")
def admin_cancel_decision(oid, dec):
    db.special_orders.update_one({"_id": ObjectId(oid)}, {"$set": {"status": "Cancelled" if dec == "accept" else "Accepted", "cancel_reason": "" if dec != "accept" else None}})
    return redirect(url_for("admin_specials"))

@app.route("/student/specials")
@require_role("student")
def student_specials():
    u = get_user()
    orders = {str(o["special_id"]): o for o in db.special_orders.find({"student_id": u["_id"]})}
    specials = list(db.specials.find())
    for s in specials:
        s["order"] = orders.get(str(s["_id"]))
        s["is_accepted"] = bool(s["order"] and s["order"].get("status") != "Cancelled")
        timing = get_special_timing(s)
        s["can_accept"] = timing["can_accept"]
        s["can_cancel"] = timing["can_cancel"]
    active = [o for o in orders.values() if o.get("status") != "Cancelled"]
    return render_template("student_specials.html", specials=specials, accepted_count=len(active), accepted_total=sum(o.get("price", 0) for o in active))

@app.route("/student/specials/accept/<sid>", methods=["POST"])
@require_role("student")
def accept_special(sid):
    u, sp = get_user(), db.specials.find_one({"_id": ObjectId(sid)})
    if sp and get_special_timing(sp)["can_accept"]:
        db.special_orders.update_one(
            {"student_id": u["_id"], "special_id": sp["_id"]},
            {"$set": {
                "student_id": u["_id"],
                "special_id": sp["_id"],
                "student_name": u.get("name", "Student"),
                "roll_no": u.get("roll_no", ""),
                "dish_name": sp["dish_name"],
                "day": sp.get("day", ""),
                "meal": sp.get("meal", ""),
                "price": sp["price"],
                "status": "Accepted",
                "accepted_at": datetime.now()
            }},
            upsert=True
        )
    return redirect(url_for("student_specials"))

@app.route("/student/specials/cancel/<sid>", methods=["POST"])
@require_role("student")
def cancel_special(sid):
    u, sp = get_user(), db.specials.find_one({"_id": ObjectId(sid)})
    if sp and get_special_timing(sp)["can_cancel"]:
        reason = request.form.get("reason", "").strip()
        if reason:
            db.special_orders.update_one(
                {"student_id": u["_id"], "special_id": sp["_id"]},
                {"$set": {"status": "Cancel Requested", "cancel_reason": reason}}
            )
    return redirect(url_for("student_specials"))

@app.route("/student/fees")
@require_role("student")
def student_fees():
    u, menus = get_user(), list(db.menu.find())
    standard_fee = sum(float(m.get("cost_veg", 95)) for m in menus) * 4 if menus else 2660.0
    orders = list(db.special_orders.find({"student_id": u["_id"], "status": {"$in": ["Accepted", "Cancel Requested"]}}))
    add_fee = sum(float(o.get("price", 0)) for o in orders)
    return render_template("student_fees.html", standard_fee=standard_fee, additional_fee=add_fee, total_fee=standard_fee + add_fee, orders=orders)

@app.route("/student/complaints", methods=["GET", "POST"])
@require_role("student")
def student_complaints():
    u = get_user()
    if request.method == "POST":
        db.complaints.insert_one({"student_id": u["_id"], "name": u["name"], "roll_no": u.get("roll_no", ""), "type": request.form.get("type", "General"),
                                  "text": request.form.get("text", ""), "status": "Open", "reply": "", "created": datetime.now()})
        return redirect(url_for("student_complaints"))
    return render_template("student_complaints.html", items=list(db.complaints.find({"student_id": u["_id"]}).sort("created", -1)))

@app.route("/admin/complaints")
@require_role("admin")
def admin_complaints():
    st = request.args.get("status")
    return render_template("admin_complaints.html", items=list(db.complaints.find({"status": st} if st else {}).sort("created", -1)),
                           status_filter=st, total_count=db.complaints.count_documents({}),
                           open_count=db.complaints.count_documents({"status": "Open"}), resolved_count=db.complaints.count_documents({"status": "Resolved"}))

@app.route("/admin/complaints/resolve/<cid>", methods=["POST"])
@require_role("admin")
def resolve(cid):
    db.complaints.update_one({"_id": ObjectId(cid)}, {"$set": {"reply": request.form.get("reply", ""), "status": "Resolved"}}); return redirect(url_for("admin_complaints"))

if __name__ == "__main__":
    app.run(debug=True, port=5000)
