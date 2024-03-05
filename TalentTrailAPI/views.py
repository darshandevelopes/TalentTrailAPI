from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.authentication import SessionAuthentication, TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import get_object_or_404
from rest_framework.authtoken.models import Token
from django.contrib.auth import get_user_model
from .serializers import *
import os
from django.http import JsonResponse
from django.core.files.storage import FileSystemStorage
from django.conf import settings
from django.shortcuts import render
from AI.resume_score import ResumeAnalyzer 

User = get_user_model()

@api_view(['POST'])
def signup(request):
    serializer = UserSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        user = User.objects.get(email=request.data['email'])
        user.set_password(request.data['password'])
        user.save()
        token = Token.objects.create(user=user)
        return Response({'token': token.key, 'user': serializer.data}, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
def login(request):
    user = get_object_or_404(User, email=request.data['email'])
    if not user.check_password(request.data['password']):
        return Response({'error': 'Invalid credentials'}, status=status.HTTP_400_BAD_REQUEST)
    if user.user_type != 'user':
        return Response({'error': 'You are not a user'}, status=status.HTTP_400_BAD_REQUEST)
    token, created = Token.objects.get_or_create(user=user)
    serializer = UserSerializer(user)
    return Response({'token': token.key, 'user': serializer.data}, status=status.HTTP_200_OK)   

@api_view(['POST'])
@authentication_classes([SessionAuthentication, TokenAuthentication])
@permission_classes([IsAuthenticated])
def upload_resume(request):
    if 'file' in request.FILES:
        resume = request.FILES['file']
        if resume.content_type != 'application/pdf':
            return JsonResponse({'error': 'File type not supported'}, status=400)
        
        user_id = request.user.id
        job_id = request.data['job_id']

        # check if user already applied to this job
        job_application = JobApplication.objects.filter(user=user_id, job=job_id)
        if job_application.exists():
            return JsonResponse({'error': 'You have already applied to this job'}, status=status.HTTP_400_BAD_REQUEST)

        serializer = JobApplicationSerializer(data={'user': user_id, 'job':job_id,'resume': resume})
        if serializer.is_valid():
            job_application = serializer.save()
            # get resume path from serializer
            resume_path = serializer.data['resume']
            resume_path = os.path.join(settings.MEDIA_ROOT, resume_path)
            print(resume_path)
            resume_path  = '/home/darshan/Desktop/talenttrail-backend'+resume_path
            analyzer = ResumeAnalyzer(resume_path)
            analysis = analyzer.analyze_resume_for_hr()
            dd =  {'user': user_id, 'job':job_id,'resume': resume}
            for key in dd.keys():
                analysis[key] = dd[key]
            detail_serializer = JobApplicationDetailSerializer(job_application, data=analysis)
            if detail_serializer.is_valid():
                detail_serializer.save()
            else:
                print(detail_serializer.errors)

            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        # return JsonResponse({'message': 'Resume uploaded successfully'})
    else:
        return JsonResponse({'error': 'No file attached'}, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
def job_list(request):
    jobs = Job.objects.all()
    serializer = JobSerializer(jobs, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)

@authentication_classes([SessionAuthentication, TokenAuthentication])
@permission_classes([IsAuthenticated])
@api_view(['GET'])
def applied_job_list(request):
    user_id = request.user.id
    print(user_id)
    job_applications = JobApplication.objects.filter(user=user_id)
    serializer = JobApplicationSerializer(job_applications, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)

# HR Endpoints
@api_view(['GET'])
def hr_homepage(request):
    return render(request, 'home.html')

@api_view(['GET', 'POST'])
def hr_login(request):
    if request.method == 'POST':
        user = get_object_or_404(User, email=request.data['email'])
        if not user.check_password(request.data['password']):
            return Response({'error': 'Invalid credentials'}, status=status.HTTP_400_BAD_REQUEST)
        if user.user_type != 'hr':
            return Response({'error': 'You are not a hr'}, status=status.HTTP_400_BAD_REQUEST)
        token, created = Token.objects.get_or_create(user=user)
        serializer = UserSerializer(user)
        return render(request, 'login.html', {'token': token.key})
    else:
        return render(request, 'login.html')
    
@api_view(['GET', 'POST'])
def hr_signup(request):
    if request.method == 'POST':
        # username same as email from the requests
        data = request.data.copy()
        data['username'] = data['email']
        serializer = UserSerializer(data=data)
        if serializer.is_valid():            
            serializer.save()
            user = User.objects.get(email=data['email'])
            user.set_password(data['password'])
            user.user_type = 'hr'
            user.save()
            token = Token.objects.create(user=user)
            return render(request, 'signup.html', {'token': token.key})
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    else:
        return render(request, 'signup.html')

@api_view(['GET', 'POST'])
@authentication_classes([SessionAuthentication, TokenAuthentication])
@permission_classes([IsAuthenticated])
def hr_job_post(request):
    if request.method == 'GET':
        return render(request, 'postjob.html')
    else:
        serializer = JobSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
def view_jobs(request):
    return render(request, 'view-jobposts.html')

@api_view(['GET'])
def job_applications(request):
    if 'job_id' in request.data:
        job_id = request.data['job_id']
        job_applications = JobApplication.objects.filter(job=job_id)
        serializer = JobApplicationDetailSerializer(job_applications, many=True)
        return render(request, 'job_applications.html', {'job_applications': serializer.data})
    else:
        return Response({'error':'job_id is required'}, status.HTTP_400_BAD_REQUEST)
    