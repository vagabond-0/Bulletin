from django.db import models
from django.core.exceptions import ValidationError
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.authentication import JWTAuthentication
from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin

class AlumniManager(BaseUserManager):
    def create_user(self, email, username, password=None, **extra_fields):
        if not email:
            raise ValueError('Email is required')
        if not username:
            raise ValueError('Username is required')
        
        user = self.model(
            email=self.normalize_email(email),
            username=username,
            **extra_fields
        )
        user.set_password(password)
        user.save(using=self._db)
        return user
    
    def create_superuser(self, email, username, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        
        return self.create_user(email, username, password, **extra_fields)

class Alumni(AbstractBaseUser, PermissionsMixin):
    username = models.CharField(max_length=255, unique=True)
    email = models.EmailField(unique=True)
    first_name = models.CharField(max_length=100, blank=True)
    last_name = models.CharField(max_length=100, blank=True)
    company = models.CharField(max_length=100, blank=True)
    designation = models.CharField(max_length=100, blank=True)
    profile_picture_url = models.URLField(max_length=255, blank=True)
    
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    
    likes = models.ManyToManyField('self', blank=True, symmetrical=False, related_name='liked_by')
    
    objects = AlumniManager()
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']
    
    def __str__(self):
        return self.username

class Post(models.Model):
    alumni = models.ForeignKey(Alumni, on_delete=models.CASCADE, related_name='posts')
    posted_date = models.DateTimeField(auto_now_add=True)
    description = models.TextField(blank=True, null=True)
    image_link = models.URLField(max_length=255, blank=True, null=True)
    video_link = models.URLField(max_length=255, blank=True, null=True)
    likes = models.ManyToManyField(Alumni, related_name='liked_posts')
    
    def __str__(self):
        return f"Post by {self.alumni.username} on {self.posted_date}"

class Comment(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='comments')
    alumni = models.ForeignKey(Alumni, on_delete=models.CASCADE, related_name='comments')
    comment_text = models.TextField()
    posted_date = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Comment by {self.alumni.username} on {self.posted_date}"