# routes/admin.py

from flask import Blueprint, render_template, request, redirect, url_for, flash
from werkzeug.security import generate_password_hash
from routes.auth_decorator import admin_required
from database.models import db, User, Role
from secrets import token_hex

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

@admin_bp.route('/')
@admin_required
def dashboard():
    return redirect(url_for('admin.list_users'))

# ─── Users ──────────────────────────────────────────────────────────────────

@admin_bp.route('/users')
@admin_required
def list_users():
    users = User.query.all()
    return render_template('admin/index.html', users=users)

@admin_bp.route('/users/create', methods=['GET','POST'])
@admin_required
def create_user():
    roles = Role.query.all()
    if request.method == 'POST':
        username   = request.form['username'].strip()
        password   = request.form['password']
        role_id    = request.form['role_id']
        enable_api = 'api_enabled' in request.form

        # Validation
        if not username or not password:
            flash('Veuillez remplir tous les champs.', 'warning')
        elif User.query.filter_by(username=username).first():
            flash('Ce nom d’utilisateur existe déjà.', 'warning')
        else:
            # Create user
            user = User(
                username=username,
                password_hash=generate_password_hash(password),
                role_id=role_id,
                api_enabled=enable_api
            )
            # Generate API key if enabled
            if enable_api:
                user.api_key = token_hex(32)
            db.session.add(user)
            db.session.commit()
            flash('Utilisateur créé.', 'success')
            return redirect(url_for('admin.list_users'))

    return render_template('admin/create.html', roles=roles)

@admin_bp.route('/users/edit/<int:user_id>', methods=['GET','POST'])
@admin_required
def edit_user(user_id):
    user  = User.query.get_or_404(user_id)
    roles = Role.query.all()

    if request.method == 'POST':
        username   = request.form['username'].strip()
        password   = request.form.get('password')  # optional
        role_id    = request.form['role_id']
        enable_api = 'api_enabled' in request.form
        regen_api  = request.form.get('regen_api')

        # Username validation
        if not username:
            flash("Le nom d’utilisateur ne peut pas être vide.", 'warning')
        elif username != user.username and User.query.filter_by(username=username).first():
            flash('Ce nom d’utilisateur est déjà utilisé.', 'warning')
        else:
            # Update fields
            user.username = username
            user.role_id  = role_id
            if password:
                user.password_hash = generate_password_hash(password)

            # Handle API access toggle / key
            if enable_api:
                user.api_enabled = True
                # generate new key if first time or if explicitly requested
                if regen_api or not user.api_key:
                    user.api_key = token_hex(32)
            else:
                # disable API and clear key
                user.api_enabled = False
                user.api_key     = None

            db.session.commit()
            flash('Utilisateur mis à jour.', 'success')
            return redirect(url_for('admin.list_users'))

    return render_template('admin/edit.html', user=user, roles=roles)

@admin_bp.route('/users/delete/<int:user_id>', methods=['POST'])
@admin_required
def delete_user(user_id):
    user = User.query.get_or_404(user_id)
    # Prevent deleting the admin role user
    if user.is_admin:
        flash('Impossible de supprimer l’administrateur.', 'danger')
    else:
        db.session.delete(user)
        db.session.commit()
        flash('Utilisateur supprimé.', 'success')
    return redirect(url_for('admin.list_users'))

# ─── Roles ──────────────────────────────────────────────────────────────────

@admin_bp.route('/roles')
@admin_required
def list_roles():
    roles = Role.query.all()
    return render_template('admin/roles.html', roles=roles)

@admin_bp.route('/roles/create', methods=['GET','POST'])
@admin_required
def create_role():
    if request.method == 'POST':
        name = request.form['name'].strip()
        if not name:
            flash('Le nom du rôle ne peut pas être vide.', 'warning')
        elif Role.query.filter_by(name=name).first():
            flash('Ce rôle existe déjà.', 'warning')
        else:
            db.session.add(Role(name=name))
            db.session.commit()
            flash('Rôle créé.', 'success')
            return redirect(url_for('admin.list_roles'))

    return render_template('admin/create_role.html')

@admin_bp.route('/roles/delete/<int:role_id>', methods=['POST'])
@admin_required
def delete_role(role_id):
    role = Role.query.get_or_404(role_id)
    if role.name.lower() == 'admin':
        flash('Impossible de supprimer le rôle administrateur.', 'danger')
    else:
        db.session.delete(role)
        db.session.commit()
        flash('Rôle supprimé.', 'success')
    return redirect(url_for('admin.list_roles'))

