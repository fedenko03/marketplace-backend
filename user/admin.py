from django.contrib import admin

from user.models import User


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('id', 'username', 'country', 'city', 'email', 'phone_number', 'role')
    search_fields = ('username', 'phone_number', 'email')
