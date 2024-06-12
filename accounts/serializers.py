from django.contrib.auth import get_user_model
from accounts.models import Profile
from rest_framework import serializers


User = get_user_model()

# class UserSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = User
#         fields = ['id', 'username', 'email']

class CreateUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'email')
        # extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        user = User.objects.create_user(validated_data['email'], validated_data['email'], validated_data['email'])
        return user

class CreateProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = ('user', 'first_name', 'last_name')



class SearchResultSerializer(serializers.Serializer):
    user = CreateUserSerializer()

    first_name = serializers.CharField()
    last_name = serializers.CharField()
    name = serializers.SerializerMethodField()
    # user_id = serializers.IntegerField()
    # email = serializers.EmailField()
    bio = serializers.CharField()

    def get_name(self, obj):
        return f"{obj.first_name} {obj.last_name}"