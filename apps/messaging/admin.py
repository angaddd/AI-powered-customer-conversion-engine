from django.contrib import admin

from .models import MessageLog, MessageTemplate

admin.site.register(MessageTemplate)
admin.site.register(MessageLog)

