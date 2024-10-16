from rest_framework import serializers
from .models import Alumni

class AlumniSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='user.username')

    class Meta:
        model = Alumni
        fields = ['id', 'first_name','last_name','username', 'email', 'company', 'designation', 'profile_picture_url']