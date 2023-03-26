from django import template
from django.contrib import messages
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.views import LoginView
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, redirect
from django.urls import reverse
from django.contrib.auth.decorators import login_required

from django.views.generic import CreateView
from .models import Companies
from .forms import *
from .models import *


class LoginUser(LoginView):
    form_class = AuthenticationForm
    template_name = 'registration/login.html'

    def get_context_data(self, *, object_list=None, **kwargs):
        return 0


@login_required
def createCompany(request):
    form = CompaniesForm(request.POST or None)
    if request.method == 'POST':
        form.save()
        messages.success(request, "Form saved successfully!")
        return HttpResponseRedirect('/company-hub/')
    else:
        form = CompaniesForm()
    return render(request, 'index.html', {'form': form})


@login_required
def updateCompany(request, pk):
    company = Companies.objects.get(company_id=pk)
    form = CompaniesForm(instance=company)

    if request.method == 'POST':
        form = CompaniesForm(request.POST, instance=company)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect('/company-hub/')

    context = {'form': form, 'company': company}
    return render(request, 'index.html', context)


@login_required
def deleteCompany(request, pk):
    company = Companies.objects.get(company_id=pk)
    context = {'item': company}
    if request.method == 'POST':
        company.delete()
        return HttpResponseRedirect('/company-hub/')
    return render(request, 'delete.html', context)


@login_required
def companyHub(request):
    context = {'Companies': Companies.objects.all()}
    return render(request, 'company_hub.html', context)


@login_required
def student_view(request):
    form = StudentsForm(request.POST or None)
    if request.method == 'POST':
        form.save()
        messages.success(request, "Form saved successfully!")
        return HttpResponseRedirect('/')
    else:
        form = StudentsForm()
    return render(request, 'index.html', {'form': form})


@login_required
def homepage(request):
    return render(request, 'homepage.html')


@login_required
def add_project(request):
    if request.method == 'POST':
        form = ProjectForm(request.POST)
        formset = StudentFormSet(request.POST)
        teacher_form = TeacherForm(request.POST)
        if form.is_valid() and formset.is_valid() and teacher_form.is_valid():
            project = form.save()
            for student_form in formset:
                print('Launched for')
                student = student_form.cleaned_data['student']
                group_number = student_form.cleaned_data['group_number']
                is_curator = student_form.cleaned_data['is_curator']
                is_moderator = student_form.cleaned_data['is_moderator']
                item = StudentsInProjects(project=project, student=student, team=group_number,
                                          is_curator=is_curator, is_moderator=is_moderator)
                item.save()
            teacher = teacher_form.cleaned_data.get('teacher')
            item = TeachersInProjects(project=project, teacher=teacher)
            item.save()
            return redirect('/')

    else:
        form = ProjectForm()
        formset = StudentFormSet()
        teacher_form = TeacherForm()
    return render(request, 'add_project.html', {'form': form, 'formset': formset, 'teacher_form': teacher_form})


@login_required
def edit_project(request, pk):
    project = Projects.objects.get(project_id=pk)
    form = ProjectForm(instance=project)

    if request.method == 'POST':
        form = ProjectForm(request.POST, instance=project)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect('/project-hub/')

    context = {'form': form, 'project': project}
    return render(request, 'index.html', context)


@login_required
def delete_project(request, pk):
    project = Projects.objects.get(project_id=pk)
    context = {'item': project}
    if request.method == 'POST':
        project.delete()
        return HttpResponseRedirect('/project-hub/')
    return render(request, 'delete_project.html', context)


@login_required
def projectHub(request):
    context = {'Projects': Projects.objects.all()}
    return render(request, 'project_hub.html', context)


@login_required
def edit_students(request, pk):
    students = StudentsInProjects.objects.filter(project_id=pk)
    context = {'project': pk, 'students': students}
    return render(request, 'students_in_project_hub.html', context)


@login_required
def edit_students_form(request, pk):
    project = Projects.objects.get(project_id=pk)
    if request.method == 'POST':
        formset = StudentFormSet(request.POST)
        if formset.is_valid():
            for student_form in formset:
                student = student_form.cleaned_data['student']
                group_number = student_form.cleaned_data['group_number']
                is_curator = student_form.cleaned_data['is_curator']
                is_moderator = student_form.cleaned_data['is_moderator']
                item = StudentsInProjects(project=project, student=student, team=group_number,
                                          is_curator=is_curator, is_moderator=is_moderator)
                item.save()
            return HttpResponseRedirect('/update-student-hub/' + str(pk) + '/')
    else:
        formset = StudentFormSet()
    context = {'project': pk, 'formset': formset}
    return render(request, 'update_students_in_project.html', context)


@login_required
def delete_students(request, pk):
    student = StudentsInProjects.objects.get(id=pk)
    context = {'item': student}
    if request.method == 'POST':
        student.delete(keep_parents=True)
        return HttpResponseRedirect('/update-student-hub/' + str(student.project_id) + '/')
    return render(request, 'delete_students.html', context)


@login_required
def edit_teachers(request, pk):
    teachers = TeachersInProjects.objects.filter(project_id=pk)
    context = {'project': pk, 'teachers': teachers}
    return render(request, 'teachers_in_project_hub.html', context)


@login_required
def edit_teachers_form(request, pk):
    project = Projects.objects.get(project_id=pk)
    if request.method == 'POST':
        formset = TeacherFormSet(request.POST)
        if formset.is_valid():
            for student_form in formset:
                teacher = student_form.cleaned_data['teacher']
                item = TeachersInProjects(project=project, teacher=teacher)
                item.save()
            return HttpResponseRedirect('/update-teacher-hub/' + str(pk) + '/')
    else:
        formset = TeacherFormSet()
    context = {'project': pk, 'formset': formset}
    return render(request, 'update_teachers_in_project.html', context)


@login_required
def delete_teachers(request, pk):
    teacher = TeachersInProjects.objects.get(id=pk)
    context = {'item': teacher}
    if request.method == 'POST':
        teacher.delete(keep_parents=True)
        return HttpResponseRedirect('/update-teacher-hub/' + str(teacher.project_id) + '/')
    return render(request, 'delete_teacher.html', context)


@login_required
def add_event(request):
    if request.method == 'POST':
        form = EventForm(request.POST)
        formset = ParticipantFormSet(request.POST)
        teacher_form = TeacherForm(request.POST)
        if form.is_valid() and formset.is_valid() and teacher_form.is_valid():
            event = form.save()
            for student_form in formset:
                print('Launched for')
                student = student_form.cleaned_data['student']
                is_manager = student_form.cleaned_data['is_manager']
                item = ParticipantsInEvents(event=event, student=student, is_manager=is_manager)
                item.save()
            teacher = teacher_form.cleaned_data.get('teacher')
            item = TeachersInEvents(event=event, teacher=teacher)
            item.save()
            return redirect('/')

    else:
        form = EventForm()
        formset = ParticipantFormSet()
        teacher_form = TeacherForm()
    return render(request, 'add_event.html', {'form': form, 'formset': formset, 'teacher_form': teacher_form})


@login_required
def edit_event(request, pk):
    event = Events.objects.get(event_id=pk)
    form = EventForm(instance=event)

    if request.method == 'POST':
        form = EventForm(request.POST, instance=event)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect('/event-hub/')

    context = {'form': form, 'project': event}
    return render(request, 'index.html', context)


@login_required
def delete_event(request, pk):
    event = Events.objects.get(event_id=pk)
    context = {'item': event}
    if request.method == 'POST':
        event.delete()
        return HttpResponseRedirect('/event-hub/')
    return render(request, 'delete_event.html', context)


@login_required
def eventHub(request):
    context = {'Events': Events.objects.all()}
    return render(request, 'event_hub.html', context)


@login_required
def edit_students_event(request, pk):
    students = ParticipantsInEvents.objects.filter(event_id=pk)
    context = {'event': pk, 'students': students}
    return render(request, 'students_in_event_hub.html', context)


@login_required
def edit_students_form_event(request, pk):
    event = Events.objects.get(event_id=pk)
    if request.method == 'POST':
        formset = ParticipantFormSet(request.POST)
        if formset.is_valid():
            for student_form in formset:
                student = student_form.cleaned_data['student']
                is_manager = student_form.cleaned_data['is_manager']
                item = ParticipantsInEvents(event=event, student=student,is_manager=is_manager)
                item.save()
            return HttpResponseRedirect('/update-student-hub-event/' + str(pk) + '/')
    else:
        formset = ParticipantFormSet()
    context = {'event': pk, 'formset': formset}
    return render(request, 'update_students_in_event.html', context)


@login_required
def delete_students_event(request, pk):
    student = ParticipantsInEvents.objects.get(id=pk)
    context = {'item': student}
    if request.method == 'POST':
        student.delete(keep_parents=True)
        return HttpResponseRedirect('/update-student-hub-event/' + str(student.event_id) + '/')
    return render(request, 'delete_students_event.html', context)


@login_required
def edit_teachers_event(request, pk):
    teachers = TeachersInEvents.objects.filter(event_id=pk)
    context = {'event': pk, 'teachers': teachers}
    return render(request, 'teachers_in_event_hub.html', context)


@login_required
def edit_teachers_form_event(request, pk):
    event = Events.objects.get(event_id=pk)
    if request.method == 'POST':
        formset = TeacherFormSet(request.POST)
        if formset.is_valid():
            for student_form in formset:
                teacher = student_form.cleaned_data['teacher']
                item = TeachersInEvents(event=event, teacher=teacher)
                item.save()
            return HttpResponseRedirect('/update-teacher-hub-event/' + str(pk) + '/')
    else:
        formset = TeacherFormSet()
    context = {'event': pk, 'formset': formset}
    return render(request, 'update_teachers_in_event.html', context)


@login_required
def delete_teachers_event(request, pk):
    teacher = TeachersInEvents.objects.get(id=pk)
    context = {'item': teacher}
    if request.method == 'POST':
        teacher.delete(keep_parents=True)
        return HttpResponseRedirect('/update-teacher-hub-event/' + str(teacher.event_id) + '/')
    return render(request, 'delete_teacher_event.html', context)