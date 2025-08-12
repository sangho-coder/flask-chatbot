# gunicorn.conf.py
import os
bind = f"0.0.0.0:{os.getenv('PORT', '8080')}"
workers = 1
timeout = 120
accesslog = "-"
errorlog = "-"
loglevel = "info"
