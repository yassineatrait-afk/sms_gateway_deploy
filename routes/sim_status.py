from flask import Blueprint, render_template, jsonify
from database.models import SimPort
from routes.auth_decorator import login_required

# Déclaration du blueprint
sim_bp = Blueprint('sim', __name__, url_prefix='/sim')

# Route principale : page complète avec layout
@sim_bp.route('/status')
@login_required
def sim_status():
    sims = SimPort.query.order_by(SimPort.port_number.asc()).all()

    # DEBUG serveur (affiche dans console)
    print("DEBUG: Nombre de SIMs chargées =", len(sims))
    for sim in sims:
        print(f"SIM Port {sim.port_number} - {sim.sim_number} - {sim.status} - Signal {sim.signal_quality}")

    return render_template('sim_status.html', sims=sims)

# Route AJAX partielle : uniquement les cartes SIM pour rafraîchissement
@sim_bp.route('/status/cards')
@login_required
def sim_status_cards():
    sims = SimPort.query.order_by(SimPort.port_number.asc()).all()
    return render_template('partials/sim_cards.html', sims=sims)





#JSON endpoint that returns current SIM ports.

@sim_bp.route('/status/ports')
@login_required
def sim_ports_api():
    """
    Return a JSON list of all SIM ports (id + port_number).
    """
    sims = SimPort.query.order_by(SimPort.port_number).all()
    data = [
        {'id': s.id, 'port_number': s.port_number}
        for s in sims
    ]
    return jsonify(data)
