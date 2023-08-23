from django.contrib import admin
from .models import User

class CustomUserAdmin(admin.ModelAdmin):
    list_display = ['user_id', 'username', 'email']
    search_fields = ['username', 'email']

admin.site.register(User, CustomUserAdmin)