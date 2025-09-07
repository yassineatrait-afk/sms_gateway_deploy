# routes/sms.py

from flask import Blueprint, request, render_template, jsonify, abort
from routes.auth_decorator import manager_required
from services.sms_parser import parse_csv_numbers
from database.models import Message, SimPort, User, db

sms_bp = Blueprint('sms', __name__, url_prefix='/sms')


@sms_bp.route('/send_single', methods=['GET', 'POST'])
@manager_required
def send_single():
    # Fetch all SIM ports from the DB for the dropdown
    sim_ports = SimPort.query.order_by(SimPort.port_number.asc()).all()

    if request.method == 'POST':
        number  = request.form.get('number')
        message = request.form.get('message')
        port    = request.form.get('port', type=int)

        if number and message and port is not None:
            msg = Message(
                direction='OUT',
                sim_port=port,
                phone_number=number,
                message=message
            )
            db.session.add(msg)
            db.session.commit()

            return render_template(
                "sms_send_single.html",
                sim_ports=sim_ports,
                success="SMS envoyé avec succès."
            )

        # missing field(s)
        return render_template(
            "sms_send_single.html",
            sim_ports=sim_ports,
            error="Veuillez remplir tous les champs."
        )

    # GET request
    return render_template("sms_send_single.html", sim_ports=sim_ports)


@sms_bp.route('/send_campaign', methods=['GET', 'POST'])
@manager_required
def send_campaign():
    if request.method == 'POST':
        file    = request.files.get('file')
        message = request.form.get('message')
        if file and message:
            filepath = f'/tmp/{file.filename}'
            file.save(filepath)
            numbers = parse_csv_numbers(filepath)
            for number in numbers:
                msg = Message(
                    direction='OUT',
                    sim_port=1,
                    phone_number=number,
                    message=message
                )
                db.session.add(msg)
            db.session.commit()
            return render_template(
                "sms_send_campaign.html",
                success=f"{len(numbers)} SMS planifiés."
            )
        return render_template(
            "sms_send_campaign.html",
            error="Fichier ou message manquant."
        )
    return render_template("sms_send_campaign.html")


# ─── New REST API endpoint for external alert systems ────────────────────

@sms_bp.route('/api/send_single', methods=['POST'])
def api_send_single():
    """
    POST /sms/api/send_single
    Headers:
      X-API-KEY: <user’s API key>
    JSON body:
      {
        "phone_number": "+2126xxxxxxx",
        "message":      "ALERT: disk usage > 90%",
        "port":         2              # optional, defaults to 1
      }
    Returns JSON:
      { "status": "queued", "message_id": 123 }
    """
    # 1) Authenticate via per-user API key
    key = request.headers.get('X-API-KEY', '')
    user = User.query.filter_by(api_key=key, api_enabled=True).first()
    if not user:
        return abort(401, description="Clé API invalide ou non activée")

    # 2) Parse JSON payload
    data = request.get_json(silent=True)
    if not data:
        return jsonify(error="Invalid JSON body"), 400

    number = data.get('phone_number')
    text   = data.get('message')
    port   = data.get('port', 1)

    # 3) Validate required fields
    if not number or not text:
        return jsonify(error="'phone_number' et 'message' sont requis"), 400

    try:
        port = int(port)
    except (ValueError, TypeError):
        return jsonify(error="'port' doit être un entier"), 400

    # 4) Queue the message
    msg = Message(
        direction='OUT',
        sim_port=port,
        phone_number=number,
        message=text
    )
    db.session.add(msg)
    db.session.commit()

    return jsonify(status="queued", message_id=msg.id), 201

