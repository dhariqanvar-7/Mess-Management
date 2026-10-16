# 🍽️ MessFlow — Hostel Mess Management System

A full-stack hostel mess management web application built with **Flask** and **MongoDB**, featuring a modern, clean, responsive UI, dynamic weekly menu planning with flexible Non-Veg meal allocation on any day and meal, numeric inventory adjustments, weekly kitchen inventory consumption engine for calculating authentic average daily dining costs, student self-payment portal (UPI QR, Card, Net Banking), complaints desk, and a billing ledger with automated late fee calculation and multi-sheet Excel export.

---

## 🌟 What's New & Core Capabilities

### 👨‍🍳 1. Admin Management
- **Dynamic Weekly Menu & Meal Allocation (`/admin/menu`)**:
  - Configure 7-day cyclical dining menu (Breakfast, Lunch, Evening Snacks, Dinner).
  - **Flexible Non-Veg Scheduling**: Not restricted to fixed days! Admin can designate **any day** and **any meal** (Lunch, Dinner, Breakfast, Snacks) as having a Non-Veg special dish (e.g. *Hyderabadi Chicken Biryani*, *Chettinad Chicken Gravy*, *Butter Chicken*), along with a customized extra surcharge (₹).
  - Changes persist across future cycles and automatically drive monthly billing calculations.
- **Pantry & Inventory Stock Management (`/admin/inventory`)**:
  - Tracks raw grocery provisions (Grains, Pulses, Dairy, Meat, Poultry, Eggs, Vegetables, Cooking Oils, Spices, Beverages).
  - **Numeric Stock Adjustments**: Enter any exact number to add incoming purchases (`+`) or deduct kitchen usage/wastage (`-`) with reason logging.
  - Complete Item Editing modal for exact stock quantities, reorder thresholds, units, and rates.
  - Valuation metrics & Low Stock threshold warning badges.
- **Weekly Food Consumption & Daily Cost Engine (`/admin/consumption`)**:
  - Log grocery provisions used directly from active inventory across **Week 1 (Days 1–7)**, **Week 2 (Days 8–14)**, **Week 3 (Days 15–21)**, and **Week 4 (Days 22–End)**.
  - Automatically calculates item expense (`qty_used × unit_price`) and optional inventory stock deduction.
  - Computes:
    - **Total Monthly Kitchen Expenditure** (Sum of Weeks 1 to 4)
    - **Total Days in Month** (calendar based, 30 or 31 days)
    - **Authentic Average Mess Cost Per Day** (`Total Monthly Cost ÷ Days in Month`)
    - **Average Daily Cost Per Student**
    - **Calculated Monthly Base Fee Per Student**
  - One-click **"Apply Calculated Costs to Student Bills"** to sync consumption figures to student invoices.
- **Student Fees & Billing Ledger (`/admin/fees`)**:
  - Displays all student bills, status (*Paid*, *Pending*, *Overdue*), and student payment records.
  - Audits student self-payments including **Transaction ID**, **Date Paid**, and **Payment Method** (UPI, Card, Net Banking).
  - **Counter Cash Desk Mode**: For students paying physical cash at the office, admin registers an official receipt number (`RCP-XXXX`) and remarks.
- **Multi-Sheet Excel Ledger Export (`/admin/export`)**:
  - Generates professional `.xlsx` workbooks with custom styles and gridlines:
    - **Sheet 1**: Student fee ledger with Roll No, Name, Diet Plan, Due Date, Status, Late Fee, Total Payable, and Transaction IDs.
    - **Sheet 2**: Monthly kitchen inventory consumption breakdown (Weeks 1–4) and average daily metrics.
    - **Sheet 3**: 7-day menu schedule with veg and non-veg specifications.
- **Complaints & Grievances Desk (`/admin/complaints`)**:
  - Filter feedback by status (*Open* vs *Resolved*).
  - Submit official responses and corrective actions back to students.

### 🎓 2. Student Portal
- **Weekly Dining Menu (`/menu`)**:
  - Highlights today's active menu card.
  - **Diet Plan Visualization**:
    - Students on the **Non-Veg Plan** see their special non-veg dish prominently tagged on the scheduled meal (e.g. Lunch or Dinner) alongside the regular veg alternative.
    - Pure vegetarian students see wholesome 100% veg meals with a clear plate indicator.
  - Instant one-click toggle to switch between Non-Veg and Pure Vegetarian plans.
  - Transparency widget displaying current month's weekly consumption and daily average rates.
- **Mess Fees & Self-Payment Portal (`/fees`)**:
  - Interactive payment portal where **students settle their own bills** (not arbitrarily marked by admin).
  - Enforces the **15th of following month** deadline with automatic late surcharge (**₹10/day** after the 15th).
  - **Payment Options**:
    - ⚡ **Instant UPI**: Simulated QR code scanner, UPI handles (GPay, PhonePe, Paytm), and custom UPI ID entry.
    - 💳 **Credit / Debit Card**: Simulated card number, expiry date, and CVV.
    - 🏦 **Net Banking**: Instant bank selection.
  - Generates real Transaction IDs (`TXN-...`) and instant **Printable / Downloadable Digital Receipts**.
- **Complaints & Feedback Desk (`/complaints`)**:
  - Raise concerns across categories (*Food Quality*, *Menu Recommendations*, *Hygiene*, *Portion / Timings*).
  - Track live resolution status and read administrator responses.

---

## 🔑 Demo Quick-Login Credentials

| Role | Email | Password | Access Details |
|---|---|---|---|
| **👑 Admin** | `admin@mess.com` | `admin123` | Full administrative mess dashboard |
| **🍗 Student (Non-Veg Plan)** | `arun@college.edu` | `student123` | Roll: 23CS101 (Non-veg plan enrolled) |
| **🥗 Student (Pure Veg Plan)** | `priya@college.edu` | `student123` | Roll: 23CS102 (Pure vegetarian plan) |
| **🍗 Student (Non-Veg Plan)** | `rahul@college.edu` | `student123` | Roll: 23EC205 (Non-veg plan enrolled) |

---

## 🚀 Running Locally

### 1. Prerequisites
- Python 3.10+
- MongoDB running on `mongodb://localhost:27017`

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Seed Database
```bash
python seed_data.py
```

### 4. Run Application
```bash
python app.py
```
Open **[http://127.0.0.1:5000](http://127.0.0.1:5000)** in your browser.

### 5. Run Integration Tests
```bash
python test_app.py
```

---

## 💡 Recommended Next Features to Add
1. **QR Code Digital Meal Pass & Counter Scanner**:
   - Generate a daily dynamic QR token on the student's mobile screen that kitchen staff scan at the service counter to verify active diet opt-in and prevent double-serving.
2. **Student Mess Rebate & Leave Application**:
   - Allow students going home for weekends or vacations to submit a leave request (e.g. 4+ days). The system automatically deducts those days from their monthly mess bill.
3. **Daily Star Rating & Meal Sentiment Analytics**:
   - Students can rate each meal (1 to 5 stars) immediately after eating. Admin sees a visual rating trend chart for each chef and dish.
4. **Automated Purchase Orders & Reorder Alerts**:
   - Automatically generate supplier Purchase Orders (PO) via PDF when inventory levels drop below minimum alert thresholds.
