import xml.etree.ElementTree as ET

from django.db import models
from django.contrib.auth.models import Group
from django.conf import settings
from django.utils.translation import ugettext_lazy as _

from . import mapping


class AttributeMapping(models.Model):
    name = models.CharField(max_length=50)

    def get_attributes_xml(self, user):
        attribs = self.attributes.all()
        astat = ET.Element('saml:AttributeStatement')

        for attr in attribs:
            astat.append(attr.get_attribute_mapping(user).get_xml())
        return astat

    def __str__(self):
        return self.name


class ServiceProvider(models.Model):
    name = models.CharField(max_length=50, null=False,
                            help_text=_("The name field displayed to users when a login is requested"))
    acs_url = models.CharField(max_length=255, null=False,
                               help_text=_("Assertion Consumer Service URL"))
    signed = models.BooleanField(default=True,
                                 help_text=_("Cryptographically Sign the SAML Response."))
    groups_can_access = models.ManyToManyField(Group, blank=True,
                                               help_text=_("Groups can access this service provider"))
    users_can_access = models.ManyToManyField(settings.AUTH_USER_MODEL, blank=True,
                                              help_text=_("Users can access this service provider"))

    attribute_mapping = models.ForeignKey(AttributeMapping, default=None, null=True)

    def __str__(self):
        return self.name

    class Meta:
        pass


class DeepLink(models.Model):
    name = models.CharField(max_length=50, null=False)

    def __str__(self):
        return self.name


class SamlAttribute(models.Model):
    AAUTH_ATTR_CHOICES = (
        (mapping.Username.NAME, 'Alliance Auth Username'),
        (mapping.Email.NAME, 'Alliance Auth Email'),
        (mapping.CharacterName.NAME, 'Main Characters Name'),
        (mapping.CorpName.NAME, 'Main Characters Corporation Name'),
        (mapping.CorpID.NAME, 'Main Characters Corporation ID'),
        (mapping.CorpTicker.NAME, 'Main Characters Corporation Ticker'),
        (mapping.AllianceName.NAME, 'Main Characters Alliance Name'),
        (mapping.AllianceID.NAME, 'Main Characters Alliance ID'),
        (mapping.Groups.NAME, 'Alliance Auth Groups'),
    )
    remote_name = models.CharField(max_length=255, null=False)
    attribute = models.CharField(max_length=20, choices=AAUTH_ATTR_CHOICES)
    mapping = models.ForeignKey(AttributeMapping, related_name='attributes')

    def __str__(self):
        return self.remote_name

    def get_attribute_mapping(self, user):
        return mapping.SamlAttributeMap.get_attribute_map_from_name(user, self.attribute, self.remote_name)
