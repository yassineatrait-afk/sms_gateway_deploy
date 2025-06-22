from app import app
from database.models import db, ScheduledTask, Message
from services.scheduler import get_pending_tasks, mark_task_executed
from time import sleep
from datetime import datetime

print("[Scheduler] Started")

while True:
    with app.app_context():
        tasks = get_pending_tasks()
        for task in tasks:
            print(f"[Scheduler] Executing Task ID: {task.id} ({task.task_type})")
            if task.task_type == 'SINGLE':
                msg = Message.query.get(task.target_id)
                if msg:
                    # Ici tu peux intégrer le vrai envoi SMS
                    print(f"→ Send to {msg.phone_number}: {msg.message}")
            elif task.task_type == 'CAMPAIGN':
                messages = Message.query.filter_by(campaign_id=task.target_id).all()
                for msg in messages:
                    print(f"→ Campaign SMS to {msg.phone_number}: {msg.message}")
            mark_task_executed(task.id)
    
    sleep(60)  # attends 60 secondes avant de relancer
