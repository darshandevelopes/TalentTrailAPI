from rest_framework import serializers
from .models import CustomUser, Job, JobApplication

class UserSerializer(serializers.ModelSerializer):
    class Meta(object):
        model = CustomUser
        fields = ['username','email', 'first_name']

class JobSerializer(serializers.ModelSerializer):
    class Meta(object):
        model = Job
        fields = ['id','title','experience','package','skills_required','job_type','location','company','qualification','total_applicants','posting_timestamp','company_logo']
        # fields = ['id','title']

class JobApplicationSerializer(serializers.ModelSerializer):
    class Meta(object):
        model = JobApplication
        fields = ['id','job','user','resume']
class JobApplicationDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = JobApplication
        fields = ['id', 'job', 'user', 'resume', 'predicted_profile', 'does_profile_match', 'score']
        