from django.contrib import admin
from .models import *

# Register your models here.
class AuthorAdmin(admin.ModelAdmin):
    pass


admin.site.register(Students, AuthorAdmin)
admin.site.register(Teachers, AuthorAdmin)
admin.site.register(Universities, AuthorAdmin)

