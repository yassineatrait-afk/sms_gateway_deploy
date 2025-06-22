# routes/dashboard.py

from flask import Blueprint, jsonify
from routes.auth_decorator import login_required
from datetime import datetime, date, timedelta
from database.models import Message, SimPort, ScheduledTask, SignalLog

dashboard_bp = Blueprint('dashboard_api', __name__)

@dashboard_bp.route('/api/dashboard/summary')
@login_required
def summary():
    today_start   = datetime.combine(date.today(), datetime.min.time())
    sms_sent      = Message.query.filter(Message.send_time >= today_start).count()
    sim_active    = SimPort.query.filter_by(status='ONLINE').count()
    now           = datetime.utcnow()
    tasks_pending = ScheduledTask.query.filter(ScheduledTask.scheduled_at > now).count()

    return jsonify({
        'smsSent':     sms_sent,
        'simActive':   sim_active,
        'tasksPending': tasks_pending
    })

@dashboard_bp.route('/api/dashboard/charts')
@login_required
def charts():
    now = datetime.utcnow()

    # Signal history
    logs = (SignalLog.query
            .order_by(SignalLog.timestamp.desc())
            .limit(12)
            .all()[::-1])
    signal_labels = [log.timestamp.strftime('%H:%M') for log in logs]
    signal_data   = [log.avg_quality for log in logs]

    # SMS volume per hour, past 24h
    sms_labels = []
    sms_data   = []
    for i in range(24):
        hr_start = (now - timedelta(hours=23-i)).replace(minute=0, second=0, microsecond=0)
        hr_end   = hr_start + timedelta(hours=1)
        cnt = (Message.query
               .filter(Message.send_time >= hr_start, Message.send_time < hr_end)
               .count())
        sms_labels.append(hr_start.strftime('%Hh'))
        sms_data.append(cnt)

    return jsonify({
        'signalHistory': {'labels': signal_labels, 'data': signal_data},
        'smsVolume':     {'labels': sms_labels,   'data': sms_data}
    })

