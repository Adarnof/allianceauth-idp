from django.shortcuts import render, get_object_or_404
from django.core.exceptions import ImproperlyConfigured
from saml2idp import views, saml2idp_metadata
from .processor import AllianceAuthProcessor
from .models import ServiceProvider

RESOURCE_NAME = 'allianceauth_idp'


def _get_config_by_name(resource_name):
    md = saml2idp_metadata.SAML2IDP_REMOTES
    for k, v in md.items():
        if k == resource_name:
            return v
    raise ImproperlyConfigured('SAML2IDP_REMOTES is not configured to handle the named resource "%s"' % resource_name)


def login_init_idp_sso(request, provider_id):
    sp_config = _get_config_by_name(RESOURCE_NAME)
    proc = AllianceAuthProcessor(sp_config)

    provider = get_object_or_404(ServiceProvider, pk=provider_id)

    proc.init_idp_sso(request, provider, sp_config)

    return views._generate_response(request, proc)
