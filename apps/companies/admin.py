from django.contrib import admin

from .models import Company, CompanyMembership

admin.site.register(Company)
admin.site.register(CompanyMembership)

