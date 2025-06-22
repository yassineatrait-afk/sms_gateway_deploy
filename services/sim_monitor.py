# services/sim_monitor.py

from app import app
from database.models import SimPort, db, SignalLog
from datetime import datetime


def update_sim_status(port_number, status, signal_quality, operator_name):
    """
    Update the status of a single SIM port, then log the average signal quality across all ONLINE SIMs.

    :param port_number: Integer port identifier
    :param status: String status ('ONLINE', 'OFFLINE', etc.)
    :param signal_quality: Integer 0-31
    :param operator_name: String operator label
    """
    # Ensure we have an application context for DB operations
    with app.app_context():
        # Fetch or create the SimPort record
        sim = SimPort.query.filter_by(port_number=port_number).first()
        if not sim:
            sim = SimPort(port_number=port_number)
            db.session.add(sim)

        # Update SIM fields
        sim.status = status
        sim.signal_quality = signal_quality
        sim.operator_name = operator_name
        sim.last_update = datetime.utcnow()
        db.session.commit()

        # Log the average signal quality of all ONLINE SIMs
        avg = (
            db.session.query(db.func.avg(SimPort.signal_quality))
                      .filter(SimPort.status == 'ONLINE')
                      .scalar()
            or 0.0
        )
        db.session.add(SignalLog(avg_quality=avg))
        db.session.commit()

