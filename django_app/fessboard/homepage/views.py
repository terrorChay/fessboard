from django.contrib import messages
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, redirect
from django.urls import reverse

from django.views.generic import CreateView
from .models import Companies
from .forms import *
from .models import *


def createCompany(request):
    form = CompaniesForm(request.POST or None)
    if request.method == 'POST':
        form.save()
        messages.success(request, "Form saved successfully!")
        return HttpResponseRedirect('/company-hub/')
    else:
        form = CompaniesForm()
    return render(request, 'index.html', {'form': form})


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


def deleteCompany(request, pk):
    company = Companies.objects.get(company_id=pk)
    context = {'item': company}
    if request.method == 'POST':
        company.delete()
        return HttpResponseRedirect('/company-hub/')
    return render(request, 'delete.html', context)


def companyHub(request):
    context = {'Companies': Companies.objects.all()}
    return render(request, 'company_hub.html', context)


def student_view(request):
    form = StudentsForm(request.POST or None)
    if request.method == 'POST':
        form.save()
        messages.success(request, "Form saved successfully!")
        return HttpResponseRedirect('/')
    else:
        form = StudentsForm()
    return render(request, 'index.html', {'form': form})


def homepage(request):
    return render(request, 'homepage.html')


def add_groups_and_students_view(request, *args, **pk):
    pk = request.session.get('selected_project_id')
    project = Projects.objects.get(project_id=pk)
    formset = 0
    # if request.method == 'POST':
    #     #formset = StudentFormset(request.POST)
    # else:
    #     #formset = StudentFormset()

    context = {'item': project, 'formset': formset}

    # Function for Adding students to groups form
    # if request.method == 'POST':
    #     form = StudentsInProjectsForm(group_id=1, project_id=pk)
    #     form.save()
    #     messages.success(request, "Form saved successfully!")
    # else:
    #     form = StudentsInProjectsForm()

    return render(request, 'group.html', context)


def add_project(request):
    if request.method == 'POST':
        form = ProjectForm(request.POST)
        formset = StudentFormSet(request.POST)
        if form.is_valid() and formset.is_valid():
            project = form.save()
            for student_form in formset:
                print('Launched for')
                student = student_form.cleaned_data['student']
                group_number = student_form.cleaned_data['group_number']
                item = Amogus(project=project, student=student, group=group_number)
                item.save()
            return redirect('/')

    else:
        form = ProjectForm()
        formset = StudentFormSet()
    return render(request, 'add_project.html', {'form': form, 'formset': formset})


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


def delete_project(request, pk):
    project = Projects.objects.get(project_id=pk)
    context = {'item': project}
    if request.method == 'POST':
        project.delete()
        return HttpResponseRedirect('/project-hub/')
    return render(request, 'delete_project.html', context)


def projectHub(request):
    context = {'Projects': Projects.objects.all()}
    return render(request, 'project_hub.html', context)


def edit_students(request, pk):
    students = Amogus.objects.query(project_id=pk)
    #formset = StudentFormSet(request.POST, initial=)

    if request.method == 'POST':
        form = ProjectForm(request.POST, instance=project)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect('/project-hub/')

    context = {'form': form, 'project': project}
    return render(request, 'index.html', context)
