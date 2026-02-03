"""
WSGI config for cloudunderroof project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.2/howto/deployment/wsgi/
"""

import os
import sys

# Forçar UTF-8 para todas as operações
if sys.version_info[0] >= 3:
    import locale
    locale.setlocale(locale.LC_ALL, 'C.UTF-8')

os.environ.setdefault('LANG', 'C.UTF-8')
os.environ.setdefault('LC_ALL', 'C.UTF-8')

from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cloudunderroof.settings')

application = get_wsgi_application()
