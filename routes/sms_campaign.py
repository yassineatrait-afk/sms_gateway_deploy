# /opt/sms_gateway/routes/sms_campaign.py

import os
from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app
from routes.auth_decorator import manager_required
from database.models import db, Campaign, Message, ScheduledTask
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
    # Simple form: only import + message, no unit/port/test
    return render_template('sms_send_campaign.html')


@sms_campaign_bp.route('/import_campaign', methods=['POST'])
@manager_required
def import_campaign():
    file = request.files.get('file')
    campaign_name = request.form.get('campaign_name', '').strip()

    if not file or file.filename == '':
        flash('Aucun fichier sélectionné.', 'danger')
        return redirect(url_for('sms_campaign.send_campaign'))

    try:
        filename = secure_filename(file.filename)
        filepath = os.path.join(UPLOAD_FOLDER, filename)

        # Remove existing file if present
        if os.path.exists(filepath):
            try:
                os.remove(filepath)
            except Exception as e:
                current_app.logger.error(
                    f"❌ Impossible de supprimer l'ancien fichier {filepath} : {e}",
                    exc_info=True
                )
                flash("Erreur lors de l'écrasement de l'ancien fichier.", 'danger')
                return redirect(url_for('sms_campaign.send_campaign'))

        file.save(filepath)

        numbers = parse_csv_numbers(filepath)
        count = len(numbers)

        if count == 0:
            flash("Le fichier ne contient aucun numéro valide.", 'warning')
            return redirect(url_for('sms_campaign.send_campaign'))

        return render_template(
            'sms_send_campaign.html',
            imported=True,
            filename=filename,
            rows=count,
            campaign_name=campaign_name
        )

    except Exception as e:
        current_app.logger.error(f"❌ Erreur pendant l'import de campagne : {e}", exc_info=True)
        flash("Une erreur est survenue lors de l'import du fichier. Consultez les logs.", 'danger')
        return redirect(url_for('sms_campaign.send_campaign'))


@sms_campaign_bp.route('/validate_campaign', methods=['POST'])
@manager_required
def validate_campaign():
    action        = request.form.get('action')
    filename      = request.form.get('filename')
    campaign_name = request.form.get('campaign_name', '').strip()
    message_text  = request.form.get('message', '').strip()
    schedule_type = request.form.get('schedule_type')
    scheduled_at  = request.form.get('scheduled_at')

    if action != 'validate':
        flash("Action non reconnue.", 'danger')
        return redirect(url_for('sms_campaign.send_campaign'))

    if not filename or not campaign_name or not message_text:
        flash('Veuillez remplir tous les champs du formulaire.', 'warning')
        return redirect(url_for('sms_campaign.send_campaign'))

    # Parse scheduled datetime
    if schedule_type == 'scheduled' and scheduled_at:
        try:
            sched_dt = datetime.strptime(scheduled_at, "%Y-%m-%dT%H:%M")
        except ValueError:
            sched_dt = datetime.utcnow()
    else:
        sched_dt = datetime.utcnow()

    # 1) Create Campaign row
    campaign = Campaign(
        name=campaign_name,
        message=message_text,
        filename=filename,
        scheduled_at=sched_dt
    )
    db.session.add(campaign)
    db.session.commit()

    # 2) Queue messages with sim_port=0 (AUTO load-balance by worker)
    filepath = os.path.join(UPLOAD_FOLDER, filename)
    numbers = parse_csv_numbers(filepath)
    if not numbers:
        flash("Le fichier ne contient aucun numéro valide.", 'warning')
        return redirect(url_for('sms_campaign.send_campaign'))

    for num in numbers:
        m = Message(
            direction='OUT',
            sim_port=0,  # AUTO: worker will pick ONLINE SIM
            phone_number=num,
            message=message_text,
            campaign_id=campaign.id,
            send_time=sched_dt if schedule_type == 'scheduled' else None
        )
        db.session.add(m)
    db.session.commit()

    # 3) Schedule the campaign
    task = ScheduledTask(
        task_type='CAMPAIGN',
        target_id=campaign.id,
        scheduled_at=campaign.scheduled_at
    )
    db.session.add(task)

    # 4) Mark campaign as pending
    campaign.status = 'PENDING'
    db.session.commit()

    when = 'programmé' if schedule_type == 'scheduled' else 'immédiat'
    flash(f"Campagne « {campaign_name} » {when}, {len(numbers)} SMS planifiés.", 'success')
    return redirect(url_for('sms_campaign.send_campaign'))

