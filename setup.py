# -*- coding: utf-8 -*-
from setuptools import setup
import allianceauth_idp

setup(
    name='allianceauth-idp',
    version=allianceauth_idp.__version__,
    author='Basraah',
    author_email='basraaheve@gmail.com',
    description='SAML 2.0 IdP for Alliance Auth',
    install_requires=[
        'Django>=1.11',
        'dj-saml-idp'
    ],
    dependency_links=[
        'https://github.com/basraah/dj-saml-idp/tarball/master#egg=dj-saml-idp',
    ],
    license='GPLv3',
    packages=['allianceauth_idp'],
    url='https://github.com/basraah/allianceauth-idp',
    zip_safe=False,
    include_package_data=True,
)
