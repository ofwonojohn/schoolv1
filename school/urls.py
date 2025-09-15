from django.urls import path
from .views import (
    ClassReportView, StudentListView, StudentDetailView, StudentCreateView, StudentUpdateView, StudentDeleteView,
    assign_subjects, add_result, bulk_add_results, generate_report, home
)

urlpatterns = [
    path('', home, name='home'),
    path('students/', StudentListView.as_view(), name='student_list'),
    path('students/<int:pk>/', StudentDetailView.as_view(), name='student_detail'),
    path('students/create/', StudentCreateView.as_view(), name='student_create'),
    path('students/<int:pk>/update/', StudentUpdateView.as_view(), name='student_update'),
    path('students/<int:pk>/delete/', StudentDeleteView.as_view(), name='student_delete'),
    path('students/<int:pk>/assign_subjects/', assign_subjects, name='assign_subjects'),
    path('students/<int:pk>/add_result/', add_result, name='add_result'),
    path('students/<int:pk>/report/', generate_report, name='report'),
    path('bulk_add_results/', bulk_add_results, name='bulk_add_results'),
    path('class_reports/', ClassReportView.as_view(), name='class_reports'),


]