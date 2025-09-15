from django.contrib import admin
from .models import Subject, Student, Result

@admin.register(Subject)
class SubjectAdmin(admin.ModelAdmin):
    list_display = ['name', 'level']
    list_filter = ['level']
    search_fields = ['name']

@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ['student_id', 'name', 'class_year', 'level', 'combination']  
    list_filter = ['class_year', 'level', 'combination'] 
    search_fields = ['name', 'student_id']
    filter_horizontal = ['subjects']

@admin.register(Result)
class ResultAdmin(admin.ModelAdmin):
    list_display = ['student', 'subject', 'score']
    list_filter = ['subject__level', 'score']
    search_fields = ['student__name', 'subject__name']