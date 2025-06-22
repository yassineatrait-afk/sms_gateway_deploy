# routes/at.py

from flask import Blueprint, render_template, request, flash, redirect, url_for, jsonify
from routes.auth_decorator import login_required
from database.models import db, ATCommand
from datetime import datetime

at_bp = Blueprint('at_bp', __name__, url_prefix='/at')


@at_bp.route('/command', methods=['GET', 'POST'])
@login_required
def at_command():
    if request.method == 'POST':
        port     = request.form['port']
        cmd_text = request.form['command']

        # Enqueue
        new_cmd = ATCommand(port_number=port, command_text=cmd_text)
        db.session.add(new_cmd)
        db.session.commit()

        flash(f"Commande AT mise en file d'attente : Port {port}, '{cmd_text}'")
        return redirect(url_for('at_bp.at_command'))

    # initial page load
    return render_template('at_command.html')


@at_bp.route('/api/commands')
@login_required
def at_commands_api():
    # return last 20 commands, newest first
    cmds = (ATCommand.query
            .order_by(ATCommand.created_at.desc())
            .limit(20)
            .all())
    data = []
    for c in cmds:
        data.append({
            'id':           c.id,
            'port_number':  c.port_number,
            'command_text': c.command_text,
            'status':       c.status,
            'result':       c.result or '',
            'created_at':   c.created_at.strftime('%d/%m %H:%M'),
            'executed_at':  c.executed_at.strftime('%d/%m %H:%M') if c.executed_at else ''
        })
    return jsonify(data)

