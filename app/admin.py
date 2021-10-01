from django.contrib import admin
from .models import Teacher

# Register your models here.

class TeacherAdmin(admin.ModelAdmin):
    list_display = ('first_name','last_name')
# Register your models here.
admin.site.register(Teacher,TeacherAdmin)