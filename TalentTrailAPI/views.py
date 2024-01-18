from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.authentication import SessionAuthentication, TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status

from django.shortcuts import get_object_or_404
from django.contrib.auth.models import User
from rest_framework.authtoken.models import Token

from .serializers import UserSerializer
import os
from django.http import JsonResponse
from django.core.files.storage import FileSystemStorage
from django.conf import settings


@api_view(['POST'])
def signup(request):
    serializer = UserSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        user = User.objects.get(username=request.data['username'])
        user.set_password(request.data['password'])
        user.save()
        token = Token.objects.create(user=user)
        return Response({'token': token.key, 'user': serializer.data})
    return Response(serializer.errors, status=status.HTTP_200_OK)


@api_view(['POST'])
def login(request):
    user = get_object_or_404(User, username=request.data['username'])
    if not user.check_password(request.data['password']):
        return Response("missing user", status=status.HTTP_404_NOT_FOUND)
    token, created = Token.objects.get_or_create(user=user)
    serializer = UserSerializer(user)
    return Response({'token': token.key, 'user': serializer.data})


@api_view(['POST'])
@authentication_classes([SessionAuthentication, TokenAuthentication])
@permission_classes([IsAuthenticated])
def upload_resume(request):
    if 'file' in request.FILES:
        resume = request.FILES['file']
        if resume.content_type != 'application/pdf':
            return JsonResponse({'error': 'File type not supported'}, status=400)

        user_id = request.user.id
        filename = f"{user_id}.pdf"
        save_path = os.path.join(settings.MEDIA_ROOT, 'resumes', filename)
        os.makedirs(os.path.dirname(save_path), exist_ok=True)

        with open(save_path, 'wb+') as destination:
            for chunk in resume.chunks():
                destination.write(chunk)

        return JsonResponse({'message': 'Resume uploaded successfully'})
    else:
        return JsonResponse({'error': 'No file attached'}, status=400)
