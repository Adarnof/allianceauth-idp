from django.contrib import admin
from .models import ServiceProvider, AttributeMapping, SamlAttribute


class ServiceProviderAdmin(admin.ModelAdmin):
    list_display = ('name', 'acs_url')
    search_fields = ('name', 'acs_url')
    filter_horizontal = ('groups_can_access', 'users_can_access')


class SamlAttributeInline(admin.TabularInline):
    model = SamlAttribute


class AttributeMappingAdmin(admin.ModelAdmin):
    inlines = [
        SamlAttributeInline,
    ]


admin.site.register(ServiceProvider, ServiceProviderAdmin)
admin.site.register(AttributeMapping, AttributeMappingAdmin)

