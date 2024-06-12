from django.contrib.auth.models import Group, User
from accounts.models import Profile
from rest_framework import permissions, viewsets, status
from rest_framework.views import APIView
from rest_framework.response import Response

from accounts.serializers import CreateProfileSerializer


# class UserViewSet(viewsets.ModelViewSet):
#     """
#     API endpoint that allows users to be viewed or edited.
#     """
#     queryset = User.objects.all().order_by('-date_joined')
#     serializer_class = UserSerializer
#     # permission_classes = [permissions.IsAuthenticated]


class CreateProfileView(APIView):

    model = Profile
    # serializer_class = CreateUserSerializer
    # permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request, *args, **kwargs):
        user = request.user
        request_data = request.data.copy()
        request_data["user"] = user.pk
        serializer = CreateProfileSerializer(data=request_data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def get(self, request, *args, **kwargs):
        queryset = Profile.objects.all()
        response_list = []
        for itr in list(queryset):
            response_list.append({
                "username": itr.user.username,
                "name": f"{itr.first_name} {itr.last_name}",
                "email": itr.user.email
            })

        return Response(response_list, status=status.HTTP_200_OK)
    

class Search(APIView):
    
    def get(self, request):
        search_keyword = request.data.get('search_key')
        search_val = request.data.get('search_val')
        response = []
        if search_keyword == "email":
            search_queryset = Profile.objects.filter(user__email__iexact=search_val)
        
        elif search_keyword == "name":
            search_queryset = Profile.objects.filter(first_name__icontains=search_val)

        else:
            response = {"Error": "Wrong search_key. Search either by email/name"}
        
        for itr in list(search_queryset):
            response.append({
                  "name": itr.get_full_name(),
                  "email": itr.user.email,
                  "bio": itr.bio
                             })
        
        if response:
            return Response(response, status=status.HTTP_200_OK)
        else:
            response = {"Error": "No matching results found."}
            return Response(response, status=status.HTTP_204_NO_CONTENT)
