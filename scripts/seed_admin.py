#!/usr/bin/env python3
import os, sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
# scripts/seed_admin.py

import os
import sys
# Ensure the project root (parent of this scripts/ folder) is on the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import app
from database.models import db, Role, User
from werkzeug.security import generate_password_hash

ADMIN_USERNAME = 'admin'
ADMIN_PASSWORD = 'Remedy212al@'  # or pick a new strong password

with app.app_context():
    # 1) ensure the admin role exists
    admin_role = Role.query.filter_by(name='admin').first()
    if not admin_role:
        admin_role = Role(name='admin')
        db.session.add(admin_role)
        db.session.commit()
        print("Created Role: admin")
    else:
        print(f"Role 'admin' already exists (id={admin_role.id})")

    # 2) ensure the admin user exists
    if not User.query.filter_by(username=ADMIN_USERNAME).first():
        user = User(
            username=ADMIN_USERNAME,
            password_hash=generate_password_hash(ADMIN_PASSWORD),
            role_id=admin_role.id
        )
        db.session.add(user)
        db.session.commit()
        print(f"Created User: {ADMIN_USERNAME}")
    else:
        print(f"User '{ADMIN_USERNAME}' already exists.")

