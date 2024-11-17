import os

from django.core.wsgi import get_wsgi_application
from GirlHub.middleware import MediaMiddleware # This is temp (fixing /media/)

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'GirlHub.settings')

application = get_wsgi_application()

application = MediaMiddleware(application) # This is temp (fixing /media/)
