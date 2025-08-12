import os

bind = f"0.0.0.0:{os.getenv('PORT', '8080')}"
workers = 1  # 무료 티어에서는 1로 고정
timeout = 30
preload_app = True  # 빠른 시작
