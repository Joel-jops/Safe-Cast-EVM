from django.contrib import admin
from .models import CustomUser, Candidate, Voter, Election
# Register your models here.
admin.site.register(CustomUser)
admin.site.register(Candidate)
admin.site.register(Voter)
admin.site.register(Election)