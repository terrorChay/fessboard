from django import template
from ..models import Students, Teachers

register = template.Library()


@register.filter(name='get_student_name')
def get_student_name(student_id):
    return Students.objects.get(student_id=student_id)


@register.filter(name='get_teacher_name')
def get_teacher_name(teacher_id):
    return Teachers.objects.get(teacher_id=teacher_id)