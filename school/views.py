from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from .models import Student, Subject, Result, CLASS_YEARS
from .forms import StudentForm, AssignSubjectsForm, ResultForm, ResultFormSet, BulkSelectForm, BulkResultFormSet

class StudentListView(ListView):
    model = Student
    template_name = 'school/student_list.html'

    def get_queryset(self):
        queryset = super().get_queryset()
        class_year = self.request.GET.get('class_year')
        level = self.request.GET.get('level')
        if class_year:
            queryset = queryset.filter(class_year=class_year)
        if level:
            queryset = queryset.filter(level=level)
        return queryset.order_by('name')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['class_years'] = CLASS_YEARS
        context['levels'] = [('O', 'O Level'), ('A', 'A Level')]
        context['current_class'] = self.request.GET.get('class_year')
        context['current_level'] = self.request.GET.get('level')
        # Precompute subjects and results for each student
        students = context['object_list']
        all_subjects = set()
        for student in students:
            all_subjects.update(student.subjects.all())
        context['subjects'] = sorted(all_subjects, key=lambda s: s.name)
        context['student_results'] = {
            student.pk: {
                subject.pk: Result.objects.filter(student=student, subject=subject).first()
                for subject in context['subjects']
            }
            for student in students
        }
        return context

class StudentDetailView(DetailView):
    model = Student
    template_name = 'school/student_detail.html'

class StudentCreateView(CreateView):
    model = Student
    form_class = StudentForm
    template_name = 'school/student_form.html'
    success_url = reverse_lazy('student_list')

class StudentUpdateView(UpdateView):
    model = Student
    form_class = StudentForm
    template_name = 'school/student_form.html'
    success_url = reverse_lazy('student_list')

class StudentDeleteView(DeleteView):
    model = Student
    template_name = 'school/student_delete.html'
    success_url = reverse_lazy('student_list')

def assign_subjects(request, pk):
    student = get_object_or_404(Student, pk=pk)
    if request.method == 'POST':
        form = AssignSubjectsForm(request.POST, level=student.level)
        if form.is_valid():
            student.subjects.set(form.cleaned_data['subjects'])
            return redirect('student_detail', pk=student.pk)
    else:
        form = AssignSubjectsForm(level=student.level)
    return render(request, 'school/assign_subjects.html', {'form': form, 'student': student})

def add_result(request, pk):
    student = get_object_or_404(Student, pk=pk)
    assigned_subjects = student.subjects.all()

    if request.method == 'POST':
        formset = ResultFormSet(request.POST, initial=[
            {'subject': subject} for subject in assigned_subjects
        ])
        if formset.is_valid():
            for form in formset:
                if form.cleaned_data:
                    Result.objects.update_or_create(
                        student=student,
                        subject=form.cleaned_data['subject'],
                        defaults={'score': form.cleaned_data['score']}
                    )
            return redirect('student_detail', pk=student.pk)
    else:
        formset = ResultFormSet(initial=[
            {'subject': subject} for subject in assigned_subjects
        ])

    return render(request, 'school/add_result.html', {
        'formset': formset,
        'student': student,
        'assigned_subjects': assigned_subjects
    })

def bulk_add_results(request):
    select_form = BulkSelectForm()
    formset = None
    if request.method == 'POST':
        if 'submit_selection' in request.POST:
            select_form = BulkSelectForm(request.POST)
            if formset.is_valid():
                for form in formset:
                    if form.cleaned_data:
                        Result.objects.update_or_create(
                            student=form.cleaned_data['student'],
                            subject=form.cleaned_data['subject'],
                            defaults={'score': form.cleaned_data['score']}
                        )
                return redirect('student_list')
    return render(request, 'school/bulk_add_results.html', {'select_form': select_form, 'formset': formset})

def generate_report(request, pk):
    student = get_object_or_404(Student, pk=pk)
    results = Result.objects.filter(student=student)
    return render(request, 'school/report.html', {'student': student, 'results': results})

class ClassReportView(ListView):
    model = Student
    template_name = 'school/class_reports.html'

    def get_queryset(self):
        queryset = super().get_queryset()
        class_year = self.request.GET.get('class_year')
        if class_year:
            queryset = queryset.filter(class_year=class_year)
        return queryset.order_by('name')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['class_years'] = CLASS_YEARS
        context['current_class'] = self.request.GET.get('class_year')
        if context['current_class']:
            students = context['object_list']
            all_subjects = set()
            for student in students:
                all_subjects.update(student.subjects.all())
            context['subjects'] = sorted(all_subjects, key=lambda s: s.name)
            context['student_results'] = {
                student.pk: {
                    subject.pk: Result.objects.filter(student=student, subject=subject).first()
                    for subject in context['subjects']
                }
                for student in students
            }
        return context

def home(request):
    return render(request, 'school/home.html')