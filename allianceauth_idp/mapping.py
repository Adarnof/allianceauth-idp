import xml.etree.ElementTree as ET
from eveonline.managers import EveManager


class SamlAttributeMap:

    NAME = None
    NS = 'saml:'

    def __init__(self, user, remote_attr_name):
        self.user = user
        self.attr_name = remote_attr_name

    @classmethod
    def get_attribute_map_from_name(cls, user, attr_name, remote_attr_name):
        """
        Factory to get the relevant attribute map class from its name
        :return: SamlAttributeMap instance
        """
        for c in cls.__subclasses__():
            if c.NAME == attr_name:
                return c(user, remote_attr_name)
        raise ModuleNotFoundError

    def get_xml_string(self):
        return ET.tostring(self.get_xml(), encoding='unicode')

    def get_xml(self):
        attrib = self.get_xml_attribute()
        attrib.append(self.get_xml_attribute_value())
        return attrib

    def get_xml_attribute(self, attr_name_format=None):
        """
        Get the XML attribute
        :param attr_name:
        :param name_format:
        :return:
        """
        attrib = self.create_element('Attribute')
        attrib.set('Name', self.attr_name)
        attrib.set('NameFormat', attr_name_format if attr_name_format is not None else
                   'urn:oasis:names:tc:SAML:2.0:attrname-format:basic')
        return attrib

    def ns(self, tag):
        """
        Appropriately namespace the give tag
        :param tag: str tag to namespace
        :return: str namespaced tag
        """
        return self.NS + tag

    def create_element(self, tag):
        """
        Create an etree element
        :param tag: str tag to give XML element
        :return: xml.etree.ElementTree.Element
        """
        return ET.Element(self.ns(tag))

    def create_attribute_value_element(self):
        val = self.create_element('AttributeValue')
        #val.set('xmlns:xs', 'http://www.w3.org/2001/XMLSchema')
        #val.set('xmlns:xsi', 'http://www.w3.org/2001/XMLSchema-instance')
        return val

    def get_xml_attribute_value(self):
        raise NotImplementedError

    @property
    def attribute(self):
        raise NotImplementedError


class Username(SamlAttributeMap):
    """
    Django.contrib.auth.models.User.username
    """

    NAME = 'username'

    @property
    def attribute(self):
        return self.user.username

    def get_xml_attribute_value(self):
        val = self.create_attribute_value_element()
        val.set('xsi:type', 'xs:string')
        val.text = self.attribute
        return val


class Email(SamlAttributeMap):
    """
    Django.contrib.auth.models.User.email
    """
    NAME = 'email'

    @property
    def attribute(self):
        return self.user.email

    def get_xml_attribute_value(self):
        val = self.create_attribute_value_element()
        val.set('xsi:type', 'xs:string')
        val.text = self.attribute
        return val


class CharacterName(SamlAttributeMap):
    """
    eveonline.models.EveCharacter.character_name
    """
    NAME = 'character_name'

    @property
    def attribute(self):
        return EveManager.get_main_character(self.user).character_name

    def get_xml_attribute_value(self):
        val = self.create_attribute_value_element()
        val.set('xsi:type', 'xs:string')
        val.text = self.attribute
        return val


class CharacterID(SamlAttributeMap):
    """
    eveonline.models.EveCharacter.character_name
    """
    NAME = 'character_id'

    @property
    def attribute(self):
        return EveManager.get_main_character(self.user).character_name

    def get_xml_attribute_value(self):
        val = self.create_attribute_value_element()
        val.set('xsi:type', 'xs:string')
        val.text = self.attribute
        return val


class CorpName(SamlAttributeMap):
    """
    eveonline.models.EveCharacter.corporation_name
    """
    NAME = 'corp_name'

    @property
    def attribute(self):
        return EveManager.get_main_character(self.user).corporation_name

    def get_xml_attribute_value(self):
        val = self.create_attribute_value_element()
        val.set('xsi:type', 'xs:string')
        val.text = self.attribute
        return val


class CorpID(SamlAttributeMap):
    """
    eveonline.models.EveCharacter.corporation_id
    """
    NAME = 'corp_id'

    @property
    def attribute(self):
        return EveManager.get_main_character(self.user).corporation_id

    def get_xml_attribute_value(self):
        val = self.create_attribute_value_element()
        val.set('xsi:type', 'xs:string')
        val.text = self.attribute
        return val


class CorpTicker(SamlAttributeMap):
    """
    eveonline.models.EveCharacter.corporation_ticker
    """
    NAME = 'corp_ticker'

    @property
    def attribute(self):
        return EveManager.get_main_character(self.user).corporation_ticker

    def get_xml_attribute_value(self):
        val = self.create_attribute_value_element()
        val.set('xsi:type', 'xs:string')
        val.text = self.attribute
        return val


class AllianceName(SamlAttributeMap):
    """
    eveonline.models.EveCharacter.alliance_name
    """
    NAME = 'alliance_name'

    @property
    def attribute(self):
        return EveManager.get_main_character(self.user).alliance_name

    def get_xml_attribute_value(self):
        val = self.create_attribute_value_element()
        val.set('xsi:type', 'xs:string')
        val.text = self.attribute
        return val


class AllianceID(SamlAttributeMap):
    """
    eveonline.models.EveCharacter.alliance_id
    """
    NAME = 'alliance_id'

    @property
    def attribute(self):
        return EveManager.get_main_character(self.user).alliance_id

    def get_xml_attribute_value(self):
        val = self.create_attribute_value_element()
        val.set('xsi:type', 'xs:string')
        val.text = self.attribute
        return val


class Groups(SamlAttributeMap):
    """
    django.contrib.auth.models.User.groups
    """
    NAME = 'groups'

    @property
    def attribute(self):
        return self.user.groups.all()

    def get_xml(self):
        attrib = self.get_xml_attribute()
        for val in self.get_xml_attribute_value():
            attrib.append(val)
        return attrib

    def get_xml_attribute_value(self):
        for g in self.attribute:
            val = self.create_attribute_value_element()
            val.set('xsi:type', 'xs:string')
            val.text = g.name
            yield val
