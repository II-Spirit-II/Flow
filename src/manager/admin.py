from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import Employee, RemoteDay, Center

class EmployeeAdmin(UserAdmin):
    list_display = ('username', 'remote_days_list', 'is_manager', 'center')
    list_filter = ('is_manager', 'center')
    search_fields = ('username',)

    fieldsets = UserAdmin.fieldsets + (
        (None, {'fields': ('center',)}),
    )

    def remote_days_list(self, obj):
        return ', '.join([str(remote_day.date) for remote_day in obj.remote_days.all()])

    remote_days_list.short_description = 'Remote Days'

admin.site.register(Employee, EmployeeAdmin)
admin.site.register(RemoteDay)
admin.site.register(Center)