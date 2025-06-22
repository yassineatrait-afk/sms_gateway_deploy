from flask import Blueprint, render_template
from routes.auth_decorator import login_required
from database.models import Inbox

inbox_bp = Blueprint('inbox', __name__, url_prefix='/inbox')

@inbox_bp.route('/')
@login_required
def inbox():
    messages = Inbox.query.order_by(Inbox.received_at.desc()).all()
    return render_template('sms_inbox.html', inbox=messages)
