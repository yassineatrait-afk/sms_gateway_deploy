# routes/reports.py

from flask import Blueprint, render_template, request, Response, url_for
from datetime import datetime, timedelta
from database.models import Message, Campaign, db
from routes.auth_decorator import viewer_required

reports_bp = Blueprint('reports', __name__, url_prefix='/reports')


@reports_bp.route('/messages', methods=['GET'])
@viewer_required
def messages_report():
    # --- Filters from query string ---
    numero   = request.args.get('numero', type=str)
    statut   = request.args.get('statut', type=str)
    date_min = request.args.get('date_min')
    date_max = request.args.get('date_max')

    # Base query: only outgoing
    q = Message.query.filter_by(direction='OUT')

    if numero:
        q = q.filter(Message.phone_number.contains(numero))

    if statut:
        q = q.filter_by(status=statut)

    if date_min and date_max:
        # parse YYYY-MM-DD
        dt_min = datetime.strptime(date_min, '%Y-%m-%d')
        # include entire max day by adding one day and using < 
        dt_max = datetime.strptime(date_max, '%Y-%m-%d') + timedelta(days=1)
        q = q.filter(Message.send_time >= dt_min,
                     Message.send_time < dt_max)

    # --- CSV Export ---
    if request.args.get('export') == 'csv':
        import csv, io
        si = io.StringIO()
        writer = csv.writer(si)
        writer.writerow(['GSM','Date envoi','Message','Statut'])
        for m in q.order_by(Message.send_time.desc()).all():
            writer.writerow([
                m.phone_number,
                m.send_time.strftime('%Y-%m-%d %H:%M:%S'),
                m.message,
                m.status
            ])
        return Response(
            si.getvalue(),
            mimetype='text/csv',
            headers={'Content-Disposition':'attachment;filename=messages.csv'}
        )

    # --- Pagination ---
    page       = request.args.get('page', 1, type=int)
    #pagination = q.order_by(Message.send_time.desc()) \
    #              .paginate(page, 20, error_out=False)

    pagination = q.order_by(Message.send_time.desc()) \
                  .paginate(page=page, per_page=20, error_out=False)

    return render_template(
        'reports/messages.html',
        messages=pagination.items,
        pagination=pagination,
        filters=request.args
    )


@reports_bp.route('/campaigns', methods=['GET'])
@viewer_required
def campaigns_report():
    # --- Filters ---
    nom     = request.args.get('campagne', type=str)
    date_j  = request.args.get('journee')
    tp      = request.args.get('type')

    q = Campaign.query

    if nom:
        q = q.filter(Campaign.name.contains(nom))

    if date_j:
        # parse YYYY-MM-DD
        dt = datetime.strptime(date_j, '%Y-%m-%d').date()
        q = q.filter(db.func.date(Campaign.scheduled_at) == dt)

    if tp and tp != 'Tout':
        q = q.filter_by(status=tp.upper())

    # --- CSV Export ---
    if request.args.get('export') == 'csv':
        import csv, io
        si = io.StringIO()
        writer = csv.writer(si)
        writer.writerow(['Campagne','Fichier','Message','Date envoi','#SMS','SMS transmis'])
        for c in q.order_by(Campaign.scheduled_at.desc()).all():
            total = len(c.messages)
            sent  = sum(1 for m in c.messages if m.status == 'SENT')
            writer.writerow([
                c.name,
                c.filename or '',
                c.message or '',
                c.scheduled_at.strftime('%Y-%m-%d %H:%M:%S'),
                total,
                sent
            ])
        return Response(
            si.getvalue(),
            mimetype='text/csv',
            headers={'Content-Disposition':'attachment;filename=campaigns.csv'}
        )

    # --- Pagination ---
    page       = request.args.get('page', 1, type=int)
    pagination = q.order_by(Campaign.scheduled_at.desc()) \
                  .paginate(page, 20, error_out=False)

    return render_template(
        'reports/campaigns.html',
        campaigns=pagination.items,
        pagination=pagination,
        filters=request.args
    )
