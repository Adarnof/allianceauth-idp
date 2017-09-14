from alliance_auth import hooks
from services.hooks import ServicesHook

from django.conf.urls import url, include
import saml2idp.urls

urlpatterns = [
    url('^idp/', include(saml2idp.urls)),
]


class IdPService(ServicesHook):
    def __init__(self):
        ServicesHook.__init__(self)
        self.urlpatterns = urlpatterns
        self.name = 'idp'


@hooks.register('services_hook')
def register_service():
    return IdPService()
