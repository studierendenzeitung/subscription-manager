# Django imports
from django.contrib import admin

# Application imports
from .models import Token


class TokenAdmin(admin.ModelAdmin):
    list_display = ['user']
    search_fields = ['user', 'action']


admin.site.register(Token, TokenAdmin)
