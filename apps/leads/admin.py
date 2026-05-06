from django.contrib import admin

from .models import Lead, VisitorSession

admin.site.register(Lead)
admin.site.register(VisitorSession)

