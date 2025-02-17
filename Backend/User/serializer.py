from rest_framework import serializers
from .models import Alumni, Post,Comment

class AlumniSerializer(serializers.ModelSerializer):
    class Meta:
        model = Alumni
        fields = ['id', 'username', 'email', 'company', 'designation', 'profile_picture_url']

class CommentSerializer(serializers.ModelSerializer):
    alumni_username = serializers.CharField(source='alumni.username', read_only=True)

    class Meta:
        model = Comment
        fields = ('id', 'post', 'alumni', 'alumni_username', 'comment_text', 'posted_date')
        read_only_fields = ('post', 'alumni', 'posted_date')


class PostSerializer(serializers.ModelSerializer):
    alumni = AlumniSerializer(read_only=True)
    comments = CommentSerializer(many=True, read_only=True) 

    class Meta:
        model = Post
        fields = ['id', 'alumni', 'posted_date', 'description', 'image_link', 'video_link', 'likes', 'comments'] 
        read_only_fields = ['posted_date', 'likes']
