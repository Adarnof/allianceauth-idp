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

    def _decode_request(self):
        """
        Decodes _request_xml from _saml_request.
        """
        # Try non-gzip first
        super(AllianceAuthProcessor, self)._decode_request()

        # Is it XML yet?
        if not self._request_xml.strip().startswith(b'<'):
            # Try decode and inflate
            self._request_xml = codex.decode_base64_and_inflate(self._saml_request)

        self._logger.debug('SAML request decoded: '.format(self._request_xml))

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

    def _validate_user(self):
        user = get_user(self._django_request)
        if (user.serviceprovider_set.filter(pk=self._service_provider.pk).exists() or
            user.groups.filter(serviceprovider__pk=self._service_provider.pk).exists()):
            return
        raise exceptions.CannotHandleAssertion(_("User is not authorized to use this service provider"))

    def init_deep_link(self, request, sp_config, url):
        """
        Initialize this Processor to make an IdP-initiated call to the SP's
        deep-linked URL.
        """
        self._reset(request, sp_config)
        self._service_provider = ServiceProvider.objects.all()[0] # TODO: Temp placeholder
        acs_url = self._service_provider.acs_url # TODO: Temp placeholder
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
        self._relay_state = url

    def _format_response(self):
        """
        Formats _response_params as _response_xml.
        """
        self._response_xml = xml_render.get_response_xml(self._response_params, signed=self._service_provider.signed)

    def _format_assertion(self):
        self._assertion_xml = self._get_assertion_xml(xml_templates.ASSERTION_GOOGLE_APPS,
                                                      self._assertion_params, signed=self._service_provider.signed)

    def _get_assertion_xml(self, template, parameters, signed=False):
        # Reset signature.
        params = {}
        params.update(parameters)
        params['ASSERTION_SIGNATURE'] = ''
        template = string.Template(template)

        xml_render._get_in_response_to(params)
        xml_render._get_subject(params)  # must come before _get_attribute_statement()
        params['ATTRIBUTE_STATEMENT'] = self._get_attribute_statement()

        unsigned = template.substitute(params)
        self._logger.debug('Unsigned:')
        self._logger.debug(unsigned)
        if not signed:
            return unsigned

        # Sign it.
        signature_xml = xml_signing.get_signature_xml(unsigned, params['ASSERTION_ID'])
        params['ASSERTION_SIGNATURE'] = signature_xml
        signed = template.substitute(params)

        self._logger.debug('Signed:')
        self._logger.debug(signed)
        return signed

    def _get_attribute_statement(self):
        mapped = ''
        if self._service_provider.attribute_mapping.attributes.count() > 0:
            mapped = ET.tostring(
                self._service_provider.attribute_mapping.get_attributes_xml(get_user(self._django_request))
            ).decode('utf-8')

        return mapped  # , encoding='unicode'
