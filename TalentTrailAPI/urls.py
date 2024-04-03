"""
URL configuration for TalentTrailAPI project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from TalentTrailAPI import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/signup/', views.signup),
    path('api/login/', views.login),
    path('api/upload-resume/', views.upload_resume),
    path('api/jobs/', views.job_list, name='job_list'),
    path('api/applications/', views.applied_job_list, name='applied_job_list'),

    # HR Endpoints
    path('hr/', views.hr_homepage),
    path('hr/login/', views.hr_login, name='hr_login'),
    path('hr/signup/', views.hr_signup, name='hr_signup'),
    path('hr/postjob/', views.hr_job_post, name='hr_job_post'),
    path('hr/viewjobs', views.view_jobs),
    path('hr/job-applicants/<int:job_id>', views.job_applications, name='job_applications'),
]
# Only serves files in DEBUG mode
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
# in production do 
#Nginx settings as follows
# location /media/ {
#     alias /path/to/your/project/media/;
# }