from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models

class CustomUserManager(BaseUserManager):
    def create_user(self, email, first_name, password=None, **extra_fields):
        if not email:
            raise ValueError('The Email field must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, first_name=first_name, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, first_name='', password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')
        return self.create_user(email, first_name, password, **extra_fields)
    
class CustomUser(AbstractUser):
    email = models.EmailField(unique=True)
    otp = models.CharField(max_length=6, blank=True, null=True)
    user_type = models.CharField(max_length=10, default='user')
    
    objects = CustomUserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

class Job(models.Model):
    id = models.AutoField(primary_key=True)
    title = models.CharField(max_length=100)
    experience = models.FloatField()
    # experience_max = models.FloatField()
    package = models.FloatField()
    skills_required = models.CharField(max_length=100)
    job_type = models.CharField(max_length=100)
    location = models.CharField(max_length=100)
    company = models.CharField(max_length=100)
    qualification = models.CharField(max_length=100)
    total_applicants = models.IntegerField(default=0)
    posting_timestamp = models.DateTimeField(auto_now_add=True)
    company_logo = models.ImageField(upload_to='logos', blank=True, null=True)

class JobApplication(models.Model):
    id = models.AutoField(primary_key=True)
    job = models.ForeignKey(Job, on_delete=models.CASCADE)
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    resume = models.FileField(upload_to='resumes')

