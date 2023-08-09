from django.contrib import admin
from .models import User

class CustomUserAdmin(admin.ModelAdmin):
    list_display = ['user_id', 'username', 'e_mail']
    search_fields = ['username', 'e_mail']

admin.site.register(User, CustomUserAdmin)