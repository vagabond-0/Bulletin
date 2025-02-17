from django.db import models
from django.core.exceptions import ValidationError
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.authentication import JWTAuthentication

class Alumni(models.Model):
    username = models.CharField(max_length=255,unique = True, default="default_username")
    password = models.CharField(max_length=255, blank = True)
    first_name = models.CharField(max_length=100, blank=True)
    last_name = models.CharField(max_length=100, blank=True)
    email = models.EmailField(unique=True)
    company = models.CharField(max_length=100, blank=True)
    designation = models.CharField(max_length=100, blank=True)
    profile_picture_url = models.URLField(max_length=255, blank=True)
    # likes = models.ManyToManyField('self', symmetrical=False, related_name='liked_by',blank=True)
    
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