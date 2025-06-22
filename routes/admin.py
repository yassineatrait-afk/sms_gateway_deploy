# routes/admin.py
from flask import Blueprint, render_template, request, redirect, url_for, flash
from routes.auth_decorator import login_required, admin_required
from database.models import db, User, Role
from werkzeug.security import generate_password_hash

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

@admin_bp.route('/')
@login_required
@admin_required
def index():
    users = User.query.all()
    return render_template('admin/index.html', users=users)

@admin_bp.route('/create', methods=['GET','POST'])
@login_required
@admin_required
def create_user():
    if request.method == 'POST':
        user = User(
            username=request.form['username'],
            password_hash=generate_password_hash(request.form['password']),
            role_id=request.form['role_id']
        )
        db.session.add(user)
        db.session.commit()
        flash('Utilisateur créé.', 'success')
        return redirect(url_for('admin.index'))

    roles = Role.query.all()
    return render_template('admin/create.html', roles=roles)

