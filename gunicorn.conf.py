import multiprocessing

# Gunicorn setup for heavy extraction engines
bind = "0.0.0.0:10000"
workers = multiprocessing.cpu_count() * 2 + 1
timeout = 120  # Timeout badha diya taaki yt_dlp load le sake