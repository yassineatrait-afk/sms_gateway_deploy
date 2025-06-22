from flask import Blueprint, render_template, request, redirect, url_for, flash
import csv, os
from werkzeug.utils import secure_filename

sms_campaign_bp = Blueprint('sms_campaign', __name__, url_prefix='/sms')

UPLOAD_FOLDER = '/tmp/sms_uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@sms_campaign_bp.route('/send_campaign', methods=['GET'])
def send_campaign():
    return render_template('sms_send_campaign.html')

@sms_campaign_bp.route('/import_campaign', methods=['POST'])
def import_campaign():
    file = request.files.get('file')
    unit = request.form.get('unit')
    campaign_name = request.form.get('campaign_name')

    if not file or file.filename == '':
        return render_template('sms_send_campaign.html', error="Aucun fichier sélectionné.")

    filename = secure_filename(file.filename)
    filepath = os.path.join(UPLOAD_FOLDER, filename)
    file.save(filepath)

    with open(filepath, newline='', encoding='utf-8') as f:
        reader = list(csv.reader(f))
        rows = len(reader)
        cols = len(reader[0]) if rows > 0 else 0

    return render_template(
        'sms_send_campaign.html',
        imported=True,
        filename=filename,
        cols=cols,
        rows=rows,
        unit=unit,
        campaign_name=campaign_name
    )

@sms_campaign_bp.route('/validate_campaign', methods=['POST'])
def validate_campaign():
    message = request.form.get('message')
    lang = request.form.get('lang')
    label = request.form.get('label')
    test_number = request.form.get('test_number')
    action = request.form.get('action')
    schedule_type = request.form.get('schedule_type')
    scheduled_at = request.form.get('scheduled_at')

    if action == 'test':
        print(f"[TEST SMS] To: {test_number} | Msg: {message} | Lang: {lang}")
        flash("SMS de test envoyé avec succès.", "info")
        return redirect(url_for('sms_campaign.send_campaign'))

    if action == 'validate':
        if schedule_type == 'scheduled' and scheduled_at:
            print(f"[PLANIFIÉ] Envoi prévu pour {scheduled_at}")
        else:
            print("[IMMÉDIAT] Envoi en cours...")
        flash("Campagne soumise avec succès.", "success")
        return redirect(url_for('sms_campaign.send_campaign'))

    flash("Action non reconnue.", "warning")
    return redirect(url_for('sms_campaign.send_campaign'))

