import os
import sys
from getpass import getpass

from dotenv import load_dotenv
from pymongo import MongoClient
from werkzeug.security import generate_password_hash


def main():
    load_dotenv()

    mongo_uri = os.getenv("MONGO_URI")
    if not mongo_uri:
        raise ValueError("Set MONGO_URI in the environment or in .env.")

    role = os.getenv("ACCOUNT_ROLE", "admin").strip().lower()
    if role not in {"admin", "student"}:
        raise ValueError("ACCOUNT_ROLE must be either 'admin' or 'student'.")

    email = os.getenv("ACCOUNT_EMAIL", "").strip().lower()
    username = os.getenv("ACCOUNT_USERNAME", "").strip()
    name = os.getenv("ACCOUNT_NAME", "").strip()

    missing = [
        variable
        for variable, value in (
            ("ACCOUNT_EMAIL", email),
            ("ACCOUNT_USERNAME", username),
            ("ACCOUNT_NAME", name),
        )
        if not value
    ]
    if missing:
        raise ValueError(f"Set the following environment variables: {', '.join(missing)}")

    roll_no = os.getenv("STUDENT_ROLL_NO", "").strip()
    room = os.getenv("STUDENT_ROOM", "").strip()
    if role == "student" and not roll_no:
        raise ValueError("Set STUDENT_ROLL_NO when ACCOUNT_ROLE is 'student'.")

    password = os.getenv("ACCOUNT_PASSWORD")
    if not password:
        password = getpass(f"{role.capitalize()} password: ")
        if password != getpass("Confirm password: "):
            raise ValueError("The passwords do not match.")
    if len(password) < 12:
        raise ValueError("The password must be at least 12 characters long.")

    with MongoClient(mongo_uri, serverSelectionTimeoutMS=10000) as client:
        users = client["mess_db"].users
        existing = users.find_one({"$or": [{"email": email}, {"username": username}]})
        if existing:
            raise ValueError("A user with that email or username already exists; no account was changed.")

        account = {
            "name": name,
            "email": email,
            "username": username,
            "role": role,
            "password": generate_password_hash(password),
        }
        if role == "student":
            account.update({"roll_no": roll_no, "room": room})
        users.insert_one(account)

    print(f"Created {role} account for {email}.")


if __name__ == "__main__":
    try:
        main()
    except ValueError as error:
        print(error, file=sys.stderr)
        raise SystemExit(1) from error
