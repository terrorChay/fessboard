import pandas as pd
from django import forms
from django.forms import formsets, BaseInlineFormSet, inlineformset_factory, formset_factory, BaseFormSet, \
    modelformset_factory

from .models import *

from datetime import datetime


class CompaniesForm(forms.ModelForm):
    class Meta:
        model = Companies
        fields = '__all__'
        widgets = {
            'company_name': forms.TextInput(attrs={'class': 'form-control'}),
            'company_website': forms.URLInput(attrs={'class': 'form-control'}),
            'company_type': forms.Select(attrs={'class': 'form-control'}),
            'company_sphere': forms.Select(attrs={'class': 'form-control'}),
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
        # self.fields['bachelors_university'] = forms.ModelChoiceField(queryset=Universities.objects.all(),
        #                                                      to_field_name='university_name',
        #                                                      empty_label='Выберите университет бакалавра',
        #                                                      widget=forms.Select(attrs={'class': 'form-control'}))
        # self.fields['masters_university'] = forms.ModelChoiceField(queryset=Universities.objects.all(),
        #                                                      to_field_name='university_name',
        #                                                      empty_label='Выберите университет магистратуры',
        #                                                     widget=forms.Select(attrs={'class': 'form-control'}), required=False)
        # self.fields['student_status'] = forms.ModelChoiceField(queryset=StudentStatuses.objects.all(),
        #                                                            to_field_name='student_status',
        #                                                            empty_label='Выберите статус студента',
        #                                                            widget=forms.Select(attrs={'class': 'form-control'}))


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
            'project_start_date': forms.SelectDateWidget(attrs={'class': 'form-control'}),
            'project_end_date': forms.SelectDateWidget(attrs={'class': 'form-control'}),
            'project_grade': forms.Select(attrs={'class': 'form-control'}),
            'project_company': forms.Select(attrs={'class': 'form-control'}),
            'project_field': forms.Select(attrs={'class': 'form-control'}),
        }


class StudentForm(forms.Form):
    student = forms.ModelChoiceField(queryset=Students.objects.all(), label='Select Student')
    group_number = forms.IntegerField()


StudentFormSet = forms.formset_factory(StudentForm, extra=2)

# class StudentsInProjectsForm(forms.ModelForm):
#     # def __init__(self, *args, **kwargs):
#     #     self.group_id = self.kwargs.pop('group_id', None)
#     #     self.project_id = self.kwargs.pop('project_id', None)
#     #     super().__init__(*args, **kwargs)
#
#     class Meta:
#         model = StudentsInProjects
#         fields = ['student_id', 'is_curator', 'group_id']
#
#         widgets = {
#             'student_id': forms.Select(attrs={'class': 'form-control'}),
#             'is_curator': forms.CheckboxInput(attrs={'class': 'form-control'}),
#             'group_id': forms.NumberInput(attrs={'class': 'form-control'})
#         }
#
#
# class BaseStudentsFormset(BaseFormSet):
#     def add_fields(self, form, index):
#         form.fields["student_id"] = forms.ModelChoiceField(queryset=Students.objects.all(),
#                                                            widget=forms.Select(attrs={'class': 'form-control'}))
#         form.fields["group_id"] = forms.IntegerField(widget=forms.NumberInput(attrs={'class': 'form-control'}))
#         form.fields["is_curator"] = forms.BooleanField(widget=forms.CheckboxInput(attrs={'class': 'form-control'}))
#         super().add_fields(form, index)
#
#
# #StudentFormset = modelformset_factory(StudentsInProjectsForm, fields=['student_id'])
