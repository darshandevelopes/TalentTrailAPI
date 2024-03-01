from .models import CustomUser
from django.contrib import admin
from .models import CustomUser, Job

class JobAdmin(admin.ModelAdmin):
    list_display = ['id','title','experience','package','skills_required','job_type','location','company','qualification','total_applicants','posting_timestamp','company_logo']

admin.site.register(CustomUser)
admin.site.register(Job, JobAdmin)
