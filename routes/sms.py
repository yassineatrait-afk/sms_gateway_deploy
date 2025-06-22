from flask import Blueprint, request, render_template
from routes.auth_decorator import login_required
from services.sms_parser import parse_csv_numbers
from database.models import Message, db

sms_bp = Blueprint('sms', __name__, url_prefix='/sms')

@sms_bp.route('/send_single', methods=['GET', 'POST'])
@login_required
def send_single():
    if request.method == 'POST':
        number = request.form.get('number')
        message = request.form.get('message')
        port = request.form.get('port', type=int)
        if number and message and port is not None:
            msg = Message(direction='OUT', sim_port=port, phone_number=number, message=message)
            db.session.add(msg)
            db.session.commit()
            return render_template("sms_send_single.html", success="SMS envoyé avec succès.")
        return render_template("sms_send_single.html", error="Veuillez remplir tous les champs.")
    return render_template("sms_send_single.html")

@sms_bp.route('/send_campaign', methods=['GET', 'POST'])
@login_required
def send_campaign():
    if request.method == 'POST':
        file = request.files.get('file')
        message = request.form.get('message')
        if file and message:
            filepath = f'/tmp/{file.filename}'
            file.save(filepath)
            numbers = parse_csv_numbers(filepath)
            for number in numbers:
                msg = Message(direction='OUT', sim_port=1, phone_number=number, message=message)
                db.session.add(msg)
            db.session.commit()
            return render_template("sms_send_campaign.html", success=f"{len(numbers)} SMS planifiés.")
        return render_template("sms_send_campaign.html", error="Fichier ou message manquant.")
    return render_template("sms_send_campaign.html")
