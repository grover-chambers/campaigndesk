import os
import bcrypt
from app import create_app
from app.extensions import db
from app.models import User, Campaign, Subscription

app = create_app('production')

with app.app_context():
    print("Creating all tables...", flush=True)
    db.create_all()
    print("Tables created.", flush=True)

    # Superadmin
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
        print("Superadmin created.", flush=True)
    else:
        print("Superadmin already exists.", flush=True)

    print("Startup complete.", flush=True)
