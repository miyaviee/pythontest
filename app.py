import os
import bjoern

from django.core.wsgi import get_wsgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "fuga.settings")

application = get_wsgi_application()

bjoern.run(application, host="127.0.0.1", port=8000)
