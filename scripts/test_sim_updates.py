# scripts/test_sim_updates.py
import os, sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

"""
Simulate periodic signal quality updates for all SimPort entries
using SQLAlchemy within Flask context.
"""
import sys
import os
import time
import random
from datetime import datetime

# Ensure project root is on Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import app
from database.models import db, SimPort

UPDATE_INTERVAL = 2  # seconds


def update_sim_ports():
    with app.app_context():
        sims = SimPort.query.all()
        for sim in sims:
            # random signal for online sims, 0 for offline
            if sim.status == 'ONLINE':
                sim.signal_quality = random.randint(15, 31)
            else:
                sim.signal_quality = 0
            sim.last_update = datetime.utcnow()
        db.session.commit()
        print(f"[{datetime.now().strftime('%H:%M:%S')}] Signals updated.")


if __name__ == '__main__':
    try:
        while True:
            update_sim_ports()
            time.sleep(UPDATE_INTERVAL)
    except KeyboardInterrupt:
        print("Stopped by user.")
