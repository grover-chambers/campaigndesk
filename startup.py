"""
Run this once after Railway deployment to set up DB.
Railway runs this via: python startup.py
"""
import os
import bcrypt
from app import create_app
from app.extensions import db
from app.models import User, Campaign, Subscription
from datetime import datetime, timedelta

app = create_app('production')

with app.app_context():
    print("Creating tables...")
    db.create_all()
    print("Tables created.")

    # Create superadmin if not exists
    admin = User.query.filter_by(email='brayo@squarerootinc.com').first()
    if not admin:
        pw = bcrypt.hashpw('Admin@2025!'.encode(), bcrypt.gensalt()).decode()
        admin = User(
            username='brayo',
            email='brayo@squarerootinc.com',
            password_hash=pw,
            role='superadmin',
            is_superadmin=True,
            is_active=True
        )
        db.session.add(admin)
        db.session.commit()
        print("Superadmin created: brayo@squarerootinc.com / Admin@2025!")
    else:
        print("Superadmin already exists.")

    print("Startup complete.")
