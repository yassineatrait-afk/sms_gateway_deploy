# scripts/seed_demo.py

import sys
import os
# Ensure project root is on Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import random
from datetime import datetime, timedelta

from app import app
from database.models import db, Message, SimPort, ScheduledTask, SignalLog


def seed():
    with app.app_context():
        # 1) Clear old demo data
        SignalLog.query.delete()
        Message.query.delete()
        SimPort.query.delete()
        ScheduledTask.query.delete()
        db.session.commit()

        # 2) Create 5 SIM ports
        ports = []
        for i in range(1, 21):
            status = random.choice(['ONLINE', 'ONLINE'])
            quality = random.randint(5, 30) if status == 'ONLINE' else 0
            sim = SimPort(
                port_number=i,
                sim_number=f'21260000{1000 + i}',
                status=status,
                signal_quality=quality,
                operator_name=random.choice(['Orange','Inwi','IAM']),
                last_update=datetime.utcnow() - timedelta(minutes=random.randint(0,10))
            )
            db.session.add(sim)
            ports.append(sim)
        db.session.commit()

        # 3) Seed SignalLog: 12 samples, 5 min apart
        now = datetime.utcnow().replace(second=0, microsecond=0)
        for n in range(12):
            ts = now - timedelta(minutes=5 * (11 - n))
            avg = (sum(s.signal_quality for s in ports if s.status=='ONLINE') /
                   max(1, sum(1 for s in ports if s.status=='ONLINE')))
            log = SignalLog(timestamp=ts, avg_quality=round(avg + random.uniform(-2,2),1))
            db.session.add(log)
        db.session.commit()

        # 4) Seed SMS volume: random messages past 24h
        for hour_offset in range(24):
            count = random.randint(0, 5)
            for _ in range(count):
                send_time = now - timedelta(hours=hour_offset, minutes=random.randint(0,59))
                msg = Message(
                    direction='OUT',
                    sim_port=random.choice(ports).port_number,
                    phone_number=f'+2126{random.randint(10000000,99999999)}',
                    message='Demo SMS',
                    status='SENT',
                    encoding='GSM',
                    send_time=send_time
                )
                db.session.add(msg)
        db.session.commit()

        # 5) Seed upcoming tasks
        for i in range(1, 4):
            st = ScheduledTask(
                task_type=random.choice(['SINGLE','CAMPAIGN']),
                target_id=random.randint(1,10),
                scheduled_at=now + timedelta(hours=i),
                status='QUEUED'
            )
            db.session.add(st)
        db.session.commit()

        print("✅ Demo data seeded!")

if __name__ == '__main__':
    seed()
