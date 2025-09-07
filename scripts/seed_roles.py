# scripts/seed_roles.py
import os, sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from app import app
from database.models import db, Role

for name in ['admin', 'manager', 'viewer']:
    with app.app_context():
        if not Role.query.filter_by(name=name).first():
            db.session.add(Role(name=name))
            print(f"Created role: {name}")
        else:
            print(f"Role '{name}' already exists")
        db.session.commit()

