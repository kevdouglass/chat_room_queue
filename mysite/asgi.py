"""
ASGI config for mysite project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/3.0/howto/deployment/asgi/
"""

import os
from channels.auth import AuthMiddlewareStack
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.security.websocket import AllowedHostsOriginValidator, OriginValidator
from django.core.asgi import get_asgi_application
from  chat.routing import websocket_urlpatterns as chat_routing_ws_urlpatterns

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mysite.settings')
# application = get_asgi_application()

application = ProtocolTypeRouter({ 
    "http": get_asgi_application(), # Allow Http Protocal (we will add WS, next)
    # AllowedHostsOriginValidator - only allow Sockets to access domains specified in settings.py ALLOWED_HOSTS
    # AuthMiddlewareStack - populates the connections SCOPE with a REFERENCE to currently authenticated USER, similar to Djangos "Request.user" object in views.py and authenticated Users.. 
    # The URL router examines the Http path of this.Connection. Then Routes, it to a particular consumer (just like urls.py works)
    "websocket": AllowedHostsOriginValidator( 
        AuthMiddlewareStack( 
            URLRouter( 
                chat_routing_ws_urlpatterns,
            )
        ) 
    ),
})
