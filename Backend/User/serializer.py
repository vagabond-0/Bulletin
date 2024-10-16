from rest_framework import serializers
from .models import Alumni, Post,Comment

class AlumniSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='user.username')

    class Meta:
        model = Alumni
        fields = ['id', 'username', 'email', 'company', 'designation', 'profile_picture_url']

class PostSerializer(serializers.ModelSerializer):
    alumni_username = serializers.CharField(source='alumni.user.username', read_only=True)

    class Meta:
        model = Post
        fields = ['id', 'alumni_username', 'posted_date', 'description', 'image_link', 'video_link', 'likes']
        read_only_fields = ['posted_date', 'likes']
class CommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = ('id', 'post', 'alumni', 'comment_text', 'posted_date')
