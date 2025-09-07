#!/usr/bin/env python3
import os, sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import app
from database.models import db

with app.app_context():
    db.create_all()
    print("✅ Toutes les tables ont été créées.")
