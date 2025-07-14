from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class Message(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    direction = db.Column(db.Enum('OUT', 'IN'), nullable=False)
    sim_port = db.Column(db.Integer, nullable=False)
    phone_number = db.Column(db.String(20))
    message = db.Column(db.Text)
    status = db.Column(db.Enum('PENDING', 'SENT', 'FAILED', 'RECEIVED'), default='PENDING')
    encoding = db.Column(db.Enum('GSM', 'UCS2', 'ASCII'), default='GSM')
    send_time = db.Column(db.DateTime, default=datetime.utcnow)
    received_time = db.Column(db.DateTime)
    campaign_id = db.Column(db.Integer, db.ForeignKey('campaign.id'))

class Campaign(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    message = db.Column(db.Text)
    filename = db.Column(db.String(255))
    scheduled_at = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    status = db.Column(db.Enum('PENDING', 'RUNNING', 'DONE', 'FAILED'), default='PENDING')
    messages = db.relationship('Message', backref='campaign', lazy=True)

class ATCommand(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    port_number = db.Column(db.Integer, nullable=False)
    command_text = db.Column(db.String(255), nullable=False)
    status = db.Column(db.Integer, default=0)  # 0 = pending, 1 = executed
    result = db.Column(db.Text)               # populated by backend executor
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    executed_at = db.Column(db.DateTime)

class ScheduledTask(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    task_type = db.Column(db.Enum('SINGLE', 'CAMPAIGN'), nullable=False)
    target_id = db.Column(db.Integer, nullable=False)
    scheduled_at = db.Column(db.DateTime)
    executed_at = db.Column(db.DateTime)
    status = db.Column(db.Enum('QUEUED', 'SENT', 'FAILED'), default='QUEUED')

class SimPort(db.Model):
    __tablename__ = 'sim_ports'
    id = db.Column(db.Integer, primary_key=True)
    port_number = db.Column(db.Integer, unique=True, nullable=False)
    sim_number = db.Column(db.String(20))
    status = db.Column(db.Enum('ONLINE', 'OFFLINE', 'REGISTERING', 'ERROR'), default='OFFLINE')
    signal_quality = db.Column(db.Integer)
    operator_name = db.Column(db.String(100))
    last_update = db.Column(db.DateTime, default=datetime.utcnow)

class SignalLog(db.Model):
    """Historical logging of average signal quality."""
    id = db.Column(db.Integer, primary_key=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    avg_quality = db.Column(db.Float, nullable=False)

class Whitelist(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    phone_number = db.Column(db.String(20), unique=True)
    description = db.Column(db.String(100))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Inbox(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    port = db.Column(db.Integer)
    sender = db.Column(db.String(20))
    content = db.Column(db.Text)
    received_at = db.Column(db.DateTime, default=datetime.utcnow)
    processed = db.Column(db.Boolean, default=False)

class Log(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    type = db.Column(db.Enum('INFO', 'WARNING', 'ERROR', 'COMMAND', 'SYSTEM'), nullable=False)
    message = db.Column(db.Text)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

# ─────────────────────────────────────────────────────────────────────────────
# New models for User & Role management:

class Role(db.Model):
    __tablename__ = 'role'
    id    = db.Column(db.Integer, primary_key=True)
    name  = db.Column(db.String(50), unique=True, nullable=False)
    users = db.relationship('User', backref='role', lazy=True)

class User(db.Model):
    __tablename__ = 'user'
    id            = db.Column(db.Integer, primary_key=True)
    username      = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    role_id       = db.Column(db.Integer, db.ForeignKey('role.id'), nullable=False)

    @property
    def is_authenticated(self):
        return True

    @property
    def is_admin(self):
        return self.role and self.role.name.lower() == 'admin'

# ─────────────────────────────────────────────────────────────────────────────
# USSD sessions

class USSDSession(db.Model):
    __tablename__   = 'ussd_session'
    id              = db.Column(db.Integer, primary_key=True)
    port_number     = db.Column(db.Integer, nullable=False)
    code            = db.Column(db.String(32), nullable=False)
    response        = db.Column(db.Text)
    status          = db.Column(db.Enum('PENDING','DONE','FAILED'), default='PENDING')
    created_at      = db.Column(db.DateTime, default=datetime.utcnow)
    completed_at    = db.Column(db.DateTime)




# ─────────────────────────────────────────────────────────────────────────────
class User(db.Model):
    __tablename__  = 'user'
    __table_args__ = {'extend_existing': True}  # allow re-definition

    id            = db.Column(db.Integer, primary_key=True)
    username      = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    role_id       = db.Column(db.Integer, db.ForeignKey('role.id'), nullable=False)

    # ← NEW: per-user API toggle & key
    api_enabled   = db.Column(db.Boolean, default=False)
    api_key       = db.Column(db.String(64), unique=True)

    @property
    def is_authenticated(self):
        return True

    @property
    def is_admin(self):
        return self.role and self.role.name.lower() == 'admin'

