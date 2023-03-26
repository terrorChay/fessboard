import pandas as pd
from django import forms
from django.contrib.admin.widgets import FilteredSelectMultiple
from django.forms import formsets, BaseInlineFormSet, inlineformset_factory, formset_factory, BaseFormSet, \
    modelformset_factory
from .models import *

from datetime import datetime

from .widgets import BootstrapDateTimePickerInput
from django.forms.widgets import DateInput


class CompaniesForm(forms.ModelForm):
    class Meta:
        model = Companies
        fields = '__all__'
        widgets = {
            'company_name': forms.TextInput(attrs={'class': 'form-control'}),
            'company_website': forms.URLInput(attrs={'class': 'form-control'}),
            'company_type': forms.Select(attrs={'class': 'form-control'}),
            'company_sphere': forms.Select(attrs={'class': 'form-control'}),
            'company_full_name': forms.TextInput(attrs={'class': 'form-control'}),
        }


class StudentsForm(forms.ModelForm):
    class Meta:
        def possible_years(first_year_in_scroll, last_year_in_scroll):
            p_year = []
            for i in range(first_year_in_scroll, last_year_in_scroll, -1):
                p_year_tuple = str(i), i
                p_year.append(p_year_tuple)
            return p_year + [('', '----')]

        model = Students
        fields = '__all__'
        widgets = {
            'student_name': forms.TextInput(attrs={'class': 'form-control'}),
            'student_surname': forms.TextInput(attrs={'class': 'form-control'}),
            'student_midname': forms.TextInput(attrs={'class': 'form-control'}),
            'bachelor_start_year': forms.Select(attrs={'class': 'form-control'}, choices=possible_years(
                (datetime.now()).year, 2014)),
            'master_start_year': forms.Select(attrs={'class': 'form-control'}, choices=possible_years(
                (datetime.now()).year, 2014)),
            'bachelors_university': forms.Select(attrs={'class': 'form-control'}),
            'masters_university': forms.Select(attrs={'class': 'form-control'}),
            'student_status': forms.Select(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super(StudentsForm, self).__init__(*args, **kwargs)


def possible_years(first_year_in_scroll, last_year_in_scroll):
    p_year = []
    for i in range(first_year_in_scroll, last_year_in_scroll, -1):
        p_year_tuple = str(i), i
        p_year.append(p_year_tuple)
    return p_year + [('', '----')]


class ProjectForm(forms.ModelForm):
    def clean(self):
        cleaned_data = super(ProjectForm, self).clean()
        # additional cleaning here
        return cleaned_data

    class Meta:
        model = Projects
        fields = '__all__'
        exclude = ['is_frozen', 'project_dateadded', 'project_dateupdated']
        widgets = {
            'project_name': forms.TextInput(attrs={'class': 'form-control'}),
            'project_description': forms.TextInput(attrs={'class': 'form-control'}),
            'project_result': forms.TextInput(attrs={'class': 'form-control'}),
            'project_start_date': DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'project_end_date': DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'project_grade': forms.Select(attrs={'class': 'form-control'}),
            'project_company': forms.Select(attrs={'class': 'form-control'}),
            'project_field': forms.Select(attrs={'class': 'form-control'}),
            'project_full_name': forms.TextInput(attrs={'class': 'form-control'}),
        }


class EventForm(forms.ModelForm):
    def clean(self):
        cleaned_data = super(EventForm, self).clean()
        # additional cleaning here
        return cleaned_data

    class Meta:
        model = Events
        fields = '__all__'
        exclude = ['is_frozen']
        widgets = {
            'event_name': forms.TextInput(attrs={'class': 'form-control'}),
            'event_description': forms.TextInput(attrs={'class': 'form-control'}),
            'event_start_date': DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'event_end_date': DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'event_region': forms.Select(attrs={'class': 'form-control'}),
        }


class StudentForm(forms.Form):
    student = forms.ModelChoiceField(queryset=Students.objects.all(), label='Select Student')
    group_number = forms.IntegerField()
    is_curator = forms.BooleanField(required=False)
    is_moderator = forms.BooleanField(required=False)


StudentFormSet = forms.formset_factory(StudentForm, extra=1)


class ParticipantForm(forms.Form):
    student = forms.ModelChoiceField(queryset=Students.objects.all(), label='Select Student')
    is_manager = forms.BooleanField(required=False)


ParticipantFormSet = forms.formset_factory(ParticipantForm, extra=1)


class TeacherForm(forms.Form):
    teacher = forms.ModelChoiceField(queryset=Teachers.objects.all(), label='Select Teacher')


TeacherFormSet = forms.formset_factory(TeacherForm, extra=1)
