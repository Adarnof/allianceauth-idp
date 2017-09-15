import saml2idp.urls

from alliance_auth import hooks
from services.hooks import ServicesHook
from .views import login_init_idp_sso

from django.conf.urls import url, include

urlpatterns = [
    url('^idp/init/sso/(?P<provider_id>[0-9]+)', login_init_idp_sso, name='login_init_idp_sso'),
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
