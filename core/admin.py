from django.contrib import admin
from .models import CustomUser, Project, Sprint, Ticket

admin.site.register(CustomUser)
admin.site.register(Project)
admin.site.register(Sprint)
admin.site.register(Ticket)
