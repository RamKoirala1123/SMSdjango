from django.contrib import admin

from department.models import Department, DepartmentAssigns, DepartmentPhotos, Sections
# Register your models here.


class DepartmentAdmin(admin.TabularInline):
    model = Department


class DepartmentImagesAdmin(admin.ModelAdmin):
    inline = [Department]


admin.site.register(Department)
admin.site.register(DepartmentPhotos, DepartmentImagesAdmin)

admin.site.register(Sections)
admin.site.register(DepartmentAssigns)
