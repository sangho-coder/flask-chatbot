bind = f"0.0.0.0:{os.getenv('PORT', '8080')}"
workers = 1  # Railway 무료 티어 안정성 보장
timeout = 120
accesslog = "-"
errorlog = "-"
loglevel = "info"
