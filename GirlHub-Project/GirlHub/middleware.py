from whitenoise import WhiteNoise # This is temp file (fixing /media/)
from django.conf import settings
import time
import threading


class MediaMiddleware(WhiteNoise):
    def __init__(self, application):
        super().__init__(application)
        self.add_files(settings.MEDIA_ROOT, prefix=settings.MEDIA_URL)
        self._start_auto_update()

    def _start_auto_update(self, interval=1):

        def update_task():
            print("Starting automatic media files update...")
            while True:
                try:
                    self.add_files(settings.MEDIA_ROOT, prefix=settings.MEDIA_URL)
                except Exception as e:
                    print(f"Error updating media files: {e}")
                time.sleep(interval)

        thread = threading.Thread(target=update_task, daemon=True)
        thread.start()
