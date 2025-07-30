"""
ASGI config for config project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/3.1/howto/deployment/asgi/
"""

import os
import dotenv
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
dotenv.load_dotenv(os.path.join(os.path.dirname(os.path.dirname(__file__)), ".env"))

django.setup()
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack

# Import your websocket routes if you have any
# from chat.routers import websocket_urlpatterns

application = ProtocolTypeRouter(
    {
        "http": get_asgi_application(),
        # Add "websocket" route handling here
        # "websocket": AuthMiddlewareStack(URLRouter(websocket_urlpatterns)),
    }
)
