# routes/sim_status.py

from flask import Blueprint, render_template, jsonify
from database.models import SimPort
from routes.auth_decorator import viewer_required

sim_bp = Blueprint('sim', __name__, url_prefix='/sim')

@sim_bp.route('/status')
@viewer_required
def sim_status():
    sims = SimPort.query.order_by(SimPort.port_number.asc()).all()
    print("DEBUG: Nombre de SIMs chargées =", len(sims))
    for sim in sims:
        print(f"SIM Port {sim.port_number} - {sim.sim_number} - {sim.status} - Signal {sim.signal_quality}")
    return render_template('sim_status.html', sims=sims)

@sim_bp.route('/status/cards')
@viewer_required
def sim_status_cards():
    sims = SimPort.query.order_by(SimPort.port_number.asc()).all()
    return render_template('partials/sim_cards.html', sims=sims)

@sim_bp.route('/status/ports')
@viewer_required
def sim_ports_api():
    """
    Return a JSON list of all SIM ports including:
      - id
      - port_number
      - sim_number      # phone number on the SIM
      - operator_name   # carrier label
      - status          # ONLINE / OFFLINE / etc.
    """
    sims = SimPort.query.order_by(SimPort.port_number.asc()).all()
    data = []
    for s in sims:
        data.append({
            'id':            s.id,
            'port_number':   s.port_number,
            'sim_number':    s.sim_number,
            'operator_name': s.operator_name,
            'status':        s.status
        })
    return jsonify(data)
