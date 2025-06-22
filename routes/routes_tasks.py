from flask import Blueprint, render_template
from routes.auth_decorator import login_required
from database.models import ScheduledTask

tasks_bp = Blueprint('tasks', __name__, url_prefix='/tasks')

@tasks_bp.route('/scheduled')
@login_required
def scheduled_tasks():
    tasks = ScheduledTask.query.order_by(ScheduledTask.scheduled_at.desc()).all()
    return render_template('scheduled_tasks.html', tasks=tasks)
