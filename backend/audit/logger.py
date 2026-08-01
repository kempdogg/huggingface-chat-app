"""
backend/audit/logger.py
Simple audit logger for image-analysis operations. Stores a JSON lines log with timestamps, operator, action, and details.

In production, replace with structured audit storage (database, WORM logs) and RBAC checks.
"""
import json
import datetime
from pathlib import Path

AUDIT_LOG_PATH = Path('backend/logs/audit.log')
AUDIT_LOG_PATH.parent.mkdir(parents=True, exist_ok=True)


def audit_log(action: str, operator: str, details: dict):
    entry = {
        'ts': datetime.datetime.utcnow().isoformat() + 'Z',
        'action': action,
        'operator': operator,
        'details': details
    }
    with AUDIT_LOG_PATH.open('a', encoding='utf-8') as fh:
        fh.write(json.dumps(entry, ensure_ascii=False) + '\n')
