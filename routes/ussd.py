# routes/ussd.py

from flask import Blueprint, render_template, request, flash, redirect, url_for, jsonify
from datetime import datetime
from routes.auth_decorator import manager_required
from database.models import USSDSession, SimPort, db

ussd_bp = Blueprint('ussd', __name__, url_prefix='/ussd')

@ussd_bp.route('/command', methods=['GET', 'POST'])
@manager_required
def ussd_command():
    # Load ports for the dropdown
    sims = SimPort.query.order_by(SimPort.port_number.asc()).all()

    if request.method == 'POST':
        port = request.form.get('port', type=int)
        code = request.form.get('code', '').strip()

        if port is None or not code:
            flash('Veuillez sélectionner un port et un code USSD.', 'warning')
            return redirect(url_for('ussd.ussd_command'))

        # Queue the USSD session
        sess = USSDSession(
            port_number=port,
            code=code,
            status='PENDING',
            created_at=datetime.utcnow()
        )
        db.session.add(sess)
        db.session.commit()

        flash('Session USSD mise en file d’ attente.', 'info')
        return redirect(url_for('ussd.ussd_command'))

    return render_template('ussd_command.html', sims=sims)

@ussd_bp.route('/api/sessions')
@manager_required
def ussd_sessions_api():
    # Return last 20 sessions, newest first
    sessions = (
        USSDSession.query
        .order_by(USSDSession.created_at.desc())
        .limit(20)
        .all()
    )
    data = []
    for s in sessions:
        data.append({
            'id':            s.id,
            'port_number':   s.port_number,
            'code':          s.code,
            'status':        s.status,
            'response':      s.response or '',
            'created_at':    s.created_at.strftime('%Y-%m-%d %H:%M:%S'),
            'completed_at':  s.completed_at.strftime('%Y-%m-%d %H:%M:%S') if s.completed_at else ''
        })
    return jsonify(data)
