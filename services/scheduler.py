from database.models import ScheduledTask, db
from datetime import datetime

def get_pending_tasks():
    now = datetime.utcnow()
    return ScheduledTask.query.filter(ScheduledTask.scheduled_at <= now, ScheduledTask.status == 'QUEUED').all()

def mark_task_executed(task_id):
    task = ScheduledTask.query.get(task_id)
    if task:
        task.status = 'SENT'
        task.executed_at = datetime.utcnow()
        db.session.commit()
