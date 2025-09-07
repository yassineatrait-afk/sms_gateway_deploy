from flask import Blueprint, render_template, request, Response, url_for
from routes.auth_decorator import viewer_required
from database.models import Inbox
from datetime import datetime, timedelta
from io import StringIO
import csv

inbox_bp = Blueprint('inbox', __name__, url_prefix='/inbox')

@inbox_bp.route('/', methods=['GET'])
@viewer_required
def inbox():
    # ─── 1) Parse filters ───────────────────────────────────
    port      = request.args.get('port',      type=int)
    sender    = request.args.get('sender',    '').strip()
    date_min  = request.args.get('date_min',  '')
    date_max  = request.args.get('date_max',  '')
    export    = request.args.get('export',    '')

    # ─── 2) Build base query ───────────────────────────────
    q = Inbox.query
    if port:
        q = q.filter_by(port=port)
    if sender:
        q = q.filter(Inbox.sender.ilike(f"%{sender}%"))
    if date_min:
        dt_min = datetime.strptime(date_min, '%Y-%m-%d')
        q = q.filter(Inbox.received_at >= dt_min)
    if date_max:
        dt_max = datetime.strptime(date_max, '%Y-%m-%d') + timedelta(days=1)
        q = q.filter(Inbox.received_at < dt_max)

    q = q.order_by(Inbox.received_at.desc())

    # ─── 3) CSV export ──────────────────────────────────────
    if export.lower() == 'csv':
        str_io = StringIO()
        writer = csv.writer(str_io)
        writer.writerow(['#', 'Port SIM', 'Expéditeur', 'Message', 'Date'])
        for idx, sms in enumerate(q.all(), start=1):
            writer.writerow([
                idx,
                sms.port,
                sms.sender,
                sms.content,
                sms.received_at.strftime('%Y-%m-%d %H:%M:%S')
            ])
        output = str_io.getvalue()
        return Response(
            output,
            mimetype='text/csv',
            headers={
                'Content-Disposition': 'attachment; filename="inbox_export.csv"'
            }
        )

    # ─── 4) Pagination ──────────────────────────────────────
    page       = request.args.get('page', 1, type=int)
    per_page   = 20
    pagination = q.paginate(page=page, per_page=per_page, error_out=False)
    messages   = pagination.items

    return render_template(
        'reports/inbox_messages.html',  # see next file
        inbox=messages,
        pagination=pagination,
        filters=request.args
    )
