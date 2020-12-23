from django.contrib import admin

from bp.models import BP, Project, TL, Student, TLLog


@admin.register(BP)
class BPAdmin(admin.ModelAdmin):
    pass


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_filter = ['bp']
    list_display = ['nr', 'title', 'tl', 'student_list', 'bp']
    list_display_links = ['nr', 'title']


@admin.register(TL)
class TLAdmin(admin.ModelAdmin):
    list_filter = ['bp']
    list_display = ['name', 'bp']


@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_filter = ['bp']
    list_display = ['name', 'project', 'bp']


@admin.register(TLLog)
class TLLogAdmin(admin.ModelAdmin):
    list_filter = ['bp']
    list_display = ['simple_timestamp', 'group', 'tl', 'requires_attention', 'bp']
