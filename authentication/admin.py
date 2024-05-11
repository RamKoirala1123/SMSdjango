from django.contrib import admin

# Register your models here.
from authentication.models import User, Notice

class UserAdmin(admin.ModelAdmin):
    list_display = ('username','email', 'first_name', 'last_name')
    list_filter = ('is_staff', 'is_superuser')
admin.site.register(User, UserAdmin)

class NoticeAdmin(admin.ModelAdmin):
    pass
admin.site.register(Notice, NoticeAdmin)