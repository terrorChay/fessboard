from django.db import models


class Companies(models.Model):
    company_id = models.AutoField(primary_key=True)
    company_name = models.CharField(max_length=255)
    company_type = models.ForeignKey('CompanyTypes', models.DO_NOTHING)
    company_sphere = models.ForeignKey('CompanySpheres', models.DO_NOTHING)
    company_website = models.TextField()

    class Meta:
        managed = False
        db_table = 'companies'

    def __str__(self):
        return self.company_name


class CompanySpheres(models.Model):
    company_sphere_id = models.AutoField(primary_key=True)
    company_sphere = models.CharField(max_length=255)

    class Meta:
        managed = False
        db_table = 'company_spheres'

    def __str__(self):
        return self.company_sphere


class CompanyTypes(models.Model):
    company_type_id = models.AutoField(primary_key=True)
    company_type = models.CharField(max_length=255)

    class Meta:
        managed = False
        db_table = 'company_types'

    def __str__(self):
        return self.company_type


class Events(models.Model):
    event_id = models.AutoField(primary_key=True)
    event_name = models.CharField(max_length=255)
    event_start_date = models.DateField()
    event_end_date = models.DateField()
    event_description = models.TextField()
    is_frozen = models.IntegerField()

    class Meta:
        managed = False
        db_table = 'events'

    def __str__(self):
        return self.event_name


class FieldSpheres(models.Model):
    sphere_id = models.AutoField(primary_key=True)
    sphere = models.CharField(max_length=255)

    class Meta:
        managed = False
        db_table = 'field_spheres'

    def __str__(self):
        return self.sphere


class ManagersInEvents(models.Model):
    event = models.ForeignKey(Events, models.DO_NOTHING)
    student = models.ForeignKey('Students', models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'managers_in_events'


class ManagersInProjects(models.Model):
    project = models.ForeignKey('Projects', models.DO_NOTHING)
    student = models.ForeignKey('Students', models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'managers_in_projects'


class ParticipantsInEvents(models.Model):
    event = models.ForeignKey(Events, models.DO_NOTHING)
    student = models.ForeignKey('Students', models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'participants_in_events'


class ProjectFields(models.Model):
    field_id = models.AutoField(primary_key=True)
    field = models.CharField(max_length=255)
    sphere = models.ForeignKey(FieldSpheres, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'project_fields'

    def __str__(self):
        return self.field


class ProjectGrades(models.Model):
    grade_id = models.AutoField(primary_key=True)
    grade = models.CharField(max_length=255)

    class Meta:
        managed = False
        db_table = 'project_grades'

    def __str__(self):
        return self.grade


class Regions(models.Model):
    region_id = models.AutoField(primary_key=True)
    region = models.CharField(max_length=255)
    is_foreign = models.IntegerField()

    class Meta:
        managed = False
        db_table = 'regions'

    def __str__(self):
        return self.region


class StudentStatuses(models.Model):
    student_status_id = models.AutoField(primary_key=True)
    student_status = models.CharField(max_length=255)

    class Meta:
        managed = False
        db_table = 'student_statuses'

    def __str__(self):
        return self.student_status


class Projects(models.Model):
    project_id = models.AutoField(primary_key=True)
    project_name = models.CharField(max_length=255, null=True, blank=True)
    project_description = models.TextField(null=True, blank=True)
    project_result = models.TextField(null=True, blank=True)
    is_frozen = models.IntegerField(default=0, null=True, blank=True)
    project_start_date = models.DateField(null=True, blank=True)
    project_end_date = models.DateField(null=True, blank=True)
    project_grade = models.ForeignKey(ProjectGrades, models.DO_NOTHING, null=True, blank=True)
    project_field = models.ForeignKey(ProjectFields, models.DO_NOTHING, null=True, blank=True)
    project_company = models.ForeignKey(Companies, models.DO_NOTHING, default='No company')
    project_dateadded = models.DateTimeField(db_column='project_dateAdded', blank=True,
                                             null=True)  # Field name made lowercase.
    project_dateupdated = models.DateTimeField(db_column='project_dateUpdated', blank=True,
                                               null=True)  # Field name made lowerca

    class Meta:
        db_table = 'projects'

    def __str__(self):
        return self.project_name


class Students(models.Model):
    student_id = models.AutoField(primary_key=True)
    student_surname = models.CharField(max_length=255)
    student_name = models.CharField(max_length=255)
    student_midname = models.CharField(max_length=255)
    bachelors_start_year = models.TextField(blank=True,
                                            null=True)  # This field type is a guess.
    masters_start_year = models.TextField(blank=True,
                                          null=True)  # This field type is a guess.
    student_status = models.ForeignKey(StudentStatuses, models.DO_NOTHING)
    bachelors_university = models.ForeignKey('Universities', models.DO_NOTHING, blank=True, null=True)
    masters_university = models.ForeignKey('Universities', models.DO_NOTHING, related_name='Uni_masters',  blank=True, null=True)

    class Meta:
        db_table = 'students'

    def __str__(self):
        return self.student_surname+self.student_name+self.student_midname


class Amogus(models.Model):
    id = models.AutoField(primary_key=True)
    student = models.ForeignKey('Students', models.DO_NOTHING)
    project = models.ForeignKey('Projects', models.DO_NOTHING)
    group = models.CharField(max_length=255)


class Teachers(models.Model):
    teacher_id = models.AutoField(primary_key=True)
    teacher_surname = models.CharField(max_length=255)
    teacher_name = models.CharField(max_length=255)
    teacher_midname = models.CharField(max_length=255)
    teacher_university = models.ForeignKey('Universities', models.DO_NOTHING, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'teachers'

    def __str__(self):
        return self.teacher_surname+self.teacher_name+self.teacher_midname


class TeachersInEvents(models.Model):
    teacher = models.ForeignKey(Teachers, models.DO_NOTHING)
    event = models.ForeignKey(Events, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'teachers_in_events'


class TeachersInProjects(models.Model):
    teacher = models.ForeignKey(Teachers, models.DO_NOTHING)
    project = models.ForeignKey(Projects, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'teachers_in_projects'


class Universities(models.Model):
    university_id = models.AutoField(primary_key=True)
    university_name = models.CharField(max_length=255)
    university_logo = models.TextField()
    university_region = models.ForeignKey(Regions, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'universities'

    def __str__(self):
        return self.university_name




