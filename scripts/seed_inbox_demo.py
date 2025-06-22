#!/usr/bin/env python3
# scripts/seed_inbox_demo.py

import sys
import os
import random
from datetime import datetime, timedelta

# Make sure we can import your app package
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import app
from database.models import db, Inbox, SimPort

def seed_inbox(num_messages=10):
    with app.app_context():
        # Optional: clear out old demo inbox messages
        #=====================================================================Inbox.query.delete()
        #=====================================================================db.session.commit()

        # If you want messages tied to actual ports, fetch them
        sim_ports = [p.port_number for p in SimPort.query.all()]
        if not sim_ports:
            print("No SimPorts found! Run your sim_monitor or seed_demo first.")
            return

        for i in range(num_messages):
            port = random.choice(sim_ports)
            sender = f"+2126{random.randint(10000000,99999999)}"
            content = random.choice([
                "Hello World!",
                "Test SMS reception",
                "Ping from demo",
                "This is a sample inbound message.",
                "Votre code est 123456"
            ])
            # Spread the messages over the last hour
            recv_at = datetime.utcnow() - timedelta(
                minutes=random.randint(0,60),
                seconds=random.randint(0,59)
            )
            msg = Inbox(
                port=port,
                sender=sender,
                content=content,
                received_at=recv_at,
                processed=False
            )
            db.session.add(msg)

        db.session.commit()
        print(f"✅ Seeded {num_messages} demo inbox messages.")

if __name__ == "__main__":
    seed_inbox()

