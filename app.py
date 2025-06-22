from flask import Flask, redirect, url_for, render_template
from config import Config
from database.models import db

# Auth
from routes.auth import auth_bp
from routes.auth_decorator import login_required

# Feature blueprints
from routes.sms import sms_bp
from routes.sms_campaign import sms_campaign_bp
from routes.at import at_bp
from routes.sim_status import sim_bp
from routes.inbox import inbox_bp
from routes.tasks import tasks_bp

# Dashboard API blueprint
from routes.dashboard import dashboard_bp

app = Flask(__name__)
app.secret_key = 'super_secure_74!sms'  # À sécuriser en prod
app.config.from_object(Config)

# Initialize DB
db.init_app(app)

# Register blueprints
app.register_blueprint(auth_bp)
app.register_blueprint(sms_bp)
app.register_blueprint(sms_campaign_bp)
app.register_blueprint(at_bp)
app.register_blueprint(sim_bp)
app.register_blueprint(inbox_bp)
app.register_blueprint(tasks_bp)
app.register_blueprint(dashboard_bp)  # <— Dashboard APIs

# Homepage / dashboard view
@app.route('/')
@login_required
def home():
    return render_template('dashboard.html')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
