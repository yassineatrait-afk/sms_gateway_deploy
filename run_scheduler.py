from app import app
from database.models import ScheduledTask, Message, USSDSession
from services.scheduler import get_pending_tasks, mark_task_executed
from services.serial_handler import send_ussd
from time import sleep
from datetime import datetime

print("[Scheduler] Started")

while True:
    with app.app_context():
        # -- handle existing SMS ScheduledTask --
        tasks = get_pending_tasks()
        for task in tasks:
            print(f"[Scheduler] Executing Task ID: {task.id} ({task.task_type})")
            if task.task_type == 'SINGLE':
                msg = Message.query.get(task.target_id)
                if msg:
                    print(f"→ Send to {msg.phone_number}: {msg.message}")
            else:  # CAMPAIGN
                for msg in Message.query.filter_by(campaign_id=task.target_id):
                    print(f"→ Campaign SMS to {msg.phone_number}: {msg.message}")
            mark_task_executed(task.id)

        # -- new: handle pending USSD sessions --
        pending = USSDSession.query.filter_by(status='PENDING').all()
        for sess in pending:
            print(f"[Scheduler] Executing USSDSession ID: {sess.id} Code: {sess.code}")
            # adjust mapping if needed (port 1 → ttyUSB0)
            port_path = f'/dev/ttyUSB{sess.port_number - 1}'
            try:
                lines = send_ussd(port_path, sess.code)
                sess.response     = "\n".join(lines)
                sess.status       = 'DONE'
                sess.completed_at = datetime.utcnow()
                print(f"→ USSD response:\n{sess.response}")
            except Exception as e:
                sess.response     = str(e)
                sess.status       = 'FAILED'
                sess.completed_at = datetime.utcnow()
                print(f"!! USSDSession {sess.id} failed: {e}")
            db.session.commit()

    sleep(60)

