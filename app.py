from flask import Flask, redirect, url_for, render_template, session, g
from config import Config
from database.models import db, User
import os
import logging
from logging.handlers import RotatingFileHandler



# Auth
from routes.auth import auth_bp
from routes.auth_decorator import login_required

# Admin (User & Role management)
from routes.admin import admin_bp

# Feature blueprints
from routes.sms import sms_bp
from routes.sms_campaign import sms_campaign_bp
from routes.at import at_bp
from routes.sim_status import sim_bp
from routes.ussd import ussd_bp             # ← USSD added
from routes.inbox import inbox_bp
from routes.tasks import tasks_bp

# Dashboard & Reports APIs
from routes.dashboard import dashboard_bp
from routes.reports import reports_bp

app = Flask(__name__)
app.secret_key = 'super_secure_74!sms'
app.config.from_object(Config)



# Setup logging
if not app.debug:
    log_dir = '/var/log/sms_gateway'
    os.makedirs(log_dir, exist_ok=True)
    
    file_handler = RotatingFileHandler(os.path.join(log_dir, 'app.log'), maxBytes=1_000_000, backupCount=5)
    file_handler.setLevel(logging.INFO)
    file_handler.setFormatter(logging.Formatter(
        '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
    ))

    app.logger.addHandler(file_handler)
    app.logger.setLevel(logging.INFO)
    app.logger.info('App started')




# Initialize DB
db.init_app(app)

@app.before_request
def load_current_user():
    g.current_user = None
    user_id = session.get('user_id')
    if user_id:
        g.current_user = User.query.get(user_id)

@app.context_processor
def inject_current_user():
    return dict(current_user=g.current_user)

# Register blueprints
app.register_blueprint(auth_bp)
app.register_blueprint(admin_bp)
app.register_blueprint(sms_bp)
app.register_blueprint(sms_campaign_bp)
app.register_blueprint(at_bp)
app.register_blueprint(sim_bp)
app.register_blueprint(ussd_bp)            # ← USSD
app.register_blueprint(inbox_bp)
app.register_blueprint(tasks_bp)
app.register_blueprint(dashboard_bp)
app.register_blueprint(reports_bp)

@app.route('/')
@login_required
def home():
    return render_template('dashboard.html')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)

