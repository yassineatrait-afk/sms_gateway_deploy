# scripts/seed_settings.py
import os, sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import sys, os
# Ensure project root is on Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import app
from database.models import db, Setting

DEFAULTS = {
    'device_alias':       'SMS Gateway',
    'time_zone':          'UTC',
    'refresh_interval':   '5',
    'ip_mode':            'DHCP',
    'static_ip':          '',
    'subnet_mask':        '',
    'gateway':            '',
    'dns_servers':        '',
    'http_port':          '5000',
    'sim_pin_required':   'no',
    'default_sim_pin':    '',
    'ip_whitelist':       '127.0.0.1/32',
    'enable_2fa':         '0',
}

if __name__ == '__main__':
    with app.app_context():
        for key, val in DEFAULTS.items():
            if not Setting.query.filter_by(key=key).first():
                db.session.add(Setting(key=key, value=val))
        db.session.commit()
        print("Default settings seeded.")

