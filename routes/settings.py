# routes/settings.py
from flask import Blueprint, render_template, request, redirect, url_for, flash
from routes.auth_decorator import login_required

settings_bp = Blueprint('settings', __name__, url_prefix='/settings')

# In a real app you'd load/save these from a DB table.
DEFAULTS = {
    'default_ip':  '192.168.88.132',
    'subnet_mask': '255.255.255.0',
    'gateway':     '192.168.88.1',
}

@settings_bp.route('/', methods=['GET', 'POST'])
@login_required
def index():
    if request.method == 'POST':
        # TODO: persist the posted values into your Settings table
        flash('Paramètres enregistrés avec succès.', 'success')
        return redirect(url_for('settings.index'))

    return render_template('settings.html', **DEFAULTS)
