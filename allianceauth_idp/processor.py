import string
import xml.etree.ElementTree as ET
from saml2idp import base, exceptions, xml_render, xml_templates, xml_signing, codex
from .models import ServiceProvider
from django.contrib.auth import get_user
from django.utils.translation import ugettext_lazy as _


class AllianceAuthProcessor(base.Processor):
    def __init__(self, config, name=None):
        if name is None:
            name = 'allianceauth_idp'
        if type(config) is dict and 'acs_url' not in config:
            config['acs_url'] = ''
        super(AllianceAuthProcessor, self).__init__(config, name)

    def _validate_request(self):
        """
        Validates the _saml_request. Sub-classes should override this and
        throw an Exception if the validation does not succeed.
        """
        self._logger.debug("In _validate_request")
        if not ServiceProvider.objects.filter(acs_url=self._request_params['ACS_URL']).exists():
            self._logger.debug(self._request_params['ACS_URL'])
            raise exceptions.CannotHandleAssertion(_("AssertionConsumerService is not a AllianceAuth IdP."))
        self._service_provider = ServiceProvider.objects.get(acs_url=self._request_params['ACS_URL'])

        # Is signing required? Check the request is signed
        # and revalidate using the stored certificate
        if self._service_provider.require_signed_requests:
            assert self._request.signed
            self._request._signed_data = False
            self._request.parse_signed(self._service_provider.x509_cert)
            assert self._request.signed_data

    def _validate_user(self):
        user = get_user(self._django_request)
        if (user.serviceprovider_set.filter(pk=self._service_provider.pk).exists() or
            user.groups.filter(serviceprovider__pk=self._service_provider.pk).exists()):
            return
        raise exceptions.CannotHandleAssertion(_("User is not authorized to use this service provider"))

    def _reset(self, django_request, sp_config=None):
        self._service_provider = None
        super(AllianceAuthProcessor, self)._reset(django_request, sp_config)

    def init_idp_sso(self, request, service_provider, sp_config=None):
        """
        Initialize this Processor to make an IdP-initiated call to the SP
        """
        self._reset(request)
        self._service_provider = service_provider
        acs_url = self._service_provider.acs_url
        # NOTE: The following request params are made up. Some are blank,
        # because they comes over in the AuthnRequest, but we don't have an
        # AuthnRequest in this case:
        # - Destination: Should be this IdP's SSO endpoint URL. Not used in the response?
        # - ProviderName: According to the spec, this is optional.
        self._request_params = {
            'ACS_URL': acs_url,
            'DESTINATION': '',
            'PROVIDER_NAME': '',
        }

    def _format_response(self):
        """
        Formats _response_params as _response_xml.
        """
        self._response_xml = xml_render.get_response_xml(self._response_params, self._assertion_xml,
                                                         signed=self._service_provider.signed)

    def _format_assertion(self):
        self._assertion_xml = xml_render._get_assertion_xml(
            xml_templates.AssertionGoogleAppsTemplate, self._assertion_params, signed=self._service_provider.signed)

    def _get_attribute_statement(self):
        mapped = ''
        if self._service_provider.attribute_mapping.attributes.count() > 0:
            mapped = ET.tostring(
                self._service_provider.attribute_mapping.get_attributes_xml(get_user(self._django_request))
            ).decode('utf-8')

        return mapped  # , encoding='unicode'
