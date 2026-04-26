import os
import sys

# Add current path to sys.path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.database import SessionLocal
from app.models import User

db = SessionLocal()
users = db.query(User).all()
for u in users:
    print(f"User: {u.username}, Email: {u.email}, Role: {u.role}")

