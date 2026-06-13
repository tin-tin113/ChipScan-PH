from django.apps import AppConfig


class ScannerConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'scanner'

    def ready(self):
        import sys
        # Only trigger background loading if we are running the server
        if any(x in sys.argv for x in ['runserver', 'wsgi', 'asgi']) or 'gunicorn' in sys.argv[0]:
            import threading
            from scanner.ocr_pipeline import get_ocr_engine
            threading.Thread(target=get_ocr_engine, daemon=True).start()

