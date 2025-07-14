# /root/sms_gateway/routes/sms_campaign.py

import os
from flask import Blueprint, render_template, request, redirect, url_for, flash
from routes.auth_decorator import manager_required
from database.models import db, Campaign, Message, ScheduledTask, SimPort
from services.sms_parser import parse_csv_numbers
from werkzeug.utils import secure_filename
from datetime import datetime

sms_campaign_bp = Blueprint('sms_campaign', __name__, url_prefix='/sms')

# Directory for uploaded CSVs
UPLOAD_FOLDER = '/tmp/sms_uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)


@sms_campaign_bp.route('/send_campaign', methods=['GET'])
@manager_required
def send_campaign():
    # Show the initial import form
    sim_ports = SimPort.query.order_by(SimPort.port_number).all()
    return render_template('sms_send_campaign.html', sim_ports=sim_ports)


@sms_campaign_bp.route('/import_campaign', methods=['POST'])
@manager_required
def import_campaign():
    file          = request.files.get('file')
    unit          = request.form.get('unit', '').strip()
    campaign_name = request.form.get('campaign_name', '').strip()

    if not file or file.filename == '':
        flash('Aucun fichier sélectionné.', 'danger')
        return redirect(url_for('sms_campaign.send_campaign'))

    filename = secure_filename(file.filename)
    filepath = os.path.join(UPLOAD_FOLDER, filename)
    file.save(filepath)

    numbers = parse_csv_numbers(filepath)
    count = len(numbers)

    sim_ports = SimPort.query.order_by(SimPort.port_number).all()
    return render_template(
        'sms_send_campaign.html',
        imported=True,
        filename=filename,
        rows=count,
        campaign_name=campaign_name,
        unit=unit,
        sim_ports=sim_ports
    )


@sms_campaign_bp.route('/validate_campaign', methods=['POST'])
@manager_required
def validate_campaign():
    action        = request.form.get('action')
    filename      = request.form.get('filename')
    campaign_name = request.form.get('campaign_name')
    unit          = request.form.get('unit')
    message_text  = request.form.get('message', '').strip()
    port          = request.form.get('port', type=int)
    schedule_type = request.form.get('schedule_type')
    scheduled_at  = request.form.get('scheduled_at')
    test_number   = request.form.get('test_number')

    # --- Test SMS only ---
    if action == 'test':
        if not test_number or not message_text:
            flash('Numéro de test et message requis.', 'warning')
        else:
            test_msg = Message(
                direction='OUT',
                sim_port=port or 1,
                phone_number=test_number,
                message=message_text
            )
            db.session.add(test_msg)
            db.session.commit()
            flash(f"SMS de test envoyé à {test_number}.", 'info')
        return redirect(url_for('sms_campaign.send_campaign'))

    # --- Validate & schedule campaign ---
    if action == 'validate':
        if not filename or not campaign_name or not message_text or not port:
            flash('Veuillez remplir tous les champs du formulaire.', 'warning')
            return redirect(url_for('sms_campaign.send_campaign'))

        # Parse scheduled datetime (Python 3.6 compatible)
        if schedule_type == 'scheduled' and scheduled_at:
            try:
                sched_dt = datetime.strptime(scheduled_at, "%Y-%m-%dT%H:%M")
            except ValueError:
                sched_dt = datetime.utcnow()
        else:
            sched_dt = datetime.utcnow()

        # 1) Create the Campaign row
        campaign = Campaign(
            name=campaign_name,
            message=message_text,
            filename=filename,
            scheduled_at=sched_dt
        )
        db.session.add(campaign)
        db.session.commit()

        # 2) Read CSV and queue Messages
        filepath = os.path.join(UPLOAD_FOLDER, filename)
        numbers = parse_csv_numbers(filepath)
        for num in numbers:
            m = Message(
                direction='OUT',
                sim_port=port,
                phone_number=num,
                message=message_text,
                campaign_id=campaign.id,
                # Set send_time to the scheduled date for programmed sends
                send_time=sched_dt if schedule_type=='scheduled' else None
            )
            db.session.add(m)
        db.session.commit()

        # 3) Create the ScheduledTask so the scheduler will pick it up
        task = ScheduledTask(
            task_type='CAMPAIGN',
            target_id=campaign.id,
            scheduled_at=campaign.scheduled_at
        )
        db.session.add(task)

        # 4) Mark campaign as pending
        campaign.status = 'PENDING'
        db.session.commit()

        when = 'programmé' if schedule_type=='scheduled' else 'immédiat'
        flash(f"Campagne « {campaign_name} » {when}, {len(numbers)} SMS planifiés.", 'success')
        return redirect(url_for('sms_campaign.send_campaign'))

    # Unknown action
    flash("Action non reconnue.", 'danger')
    return redirect(url_for('sms_campaign.send_campaign'))
