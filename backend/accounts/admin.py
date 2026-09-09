from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User


class CustomUserAdmin(UserAdmin):
    fieldsets = UserAdmin.fieldsets + (
        ('Datos del sitio', {'fields': ('avatar', 'chip_anomalo', 'nucleo_singularidad')}),
    )


admin.site.register(User, CustomUserAdmin)