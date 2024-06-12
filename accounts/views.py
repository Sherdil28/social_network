import json
from django.contrib.auth.models import Group, User
from django.db.models import Q
from accounts.models import FriendList, FriendRequest, Profile
from accounts.pagination import CustomPageNumberPagination
from rest_framework import permissions, viewsets, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.decorators import api_view, throttle_classes
from rest_framework.throttling import UserRateThrottle

from accounts.serializers import CreateProfileSerializer, CreateUserSerializer, SearchResultSerializer


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
        queryset = Profile.objects.all().exclude(user__id=request.user.id)
        response_list = []
        for itr in list(queryset):
            response_list.append({
                "username": itr.user.username,
                "user_id": itr.user.id,       # For making use in other APIs like send_friend_request, etc.
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
            search_queryset = Profile.objects.filter(user__email__iexact=search_val).exclude(user__id=request.user.id)
        
        elif search_keyword == "name":
            search_queryset = Profile.objects.filter(Q(first_name__icontains=search_val) | Q(last_name__icontains=search_val)).exclude(user__id=request.user.id)

        else:
            response = {"Error": "Wrong search_key. Search either by email/name"}
        
        for itr in list(search_queryset):
            response.append({
                  "name": itr.get_full_name(),
                  "user_id": itr.user.id,         # For making use in other APIs like send_friend_request, etc.
                  "email": itr.user.email,
                  "bio": itr.bio
                             })
            
        paginator = CustomPageNumberPagination()  # Instantiate paginator
        paginated_posts = paginator.paginate_queryset(search_queryset, request)  # Apply pagination
        serializer = SearchResultSerializer(paginated_posts, many=True)  # Serialize paginated data

        return paginator.get_paginated_response(serializer.data)  # Return paginated response
        

@api_view(['GET'])
def friends_list_view(request, *args, **kwargs):
    payload = {}
    user = request.user
    status_flag = status.HTTP_200_OK
    if user.is_authenticated:
        user_id = kwargs.get("user_id")
        if user_id:
            try:
                this_user = User.objects.get(pk=user_id)
                # user_serializer = CreateUserSerializer(data=this_user)
                # user_serializer.is_valid()
                payload['this_user'] = {"username": this_user.username, "user_id": this_user.id}
            except User.DoesNotExist:
                payload['Error'] = "That user does not exist."
                status_flag = status.HTTP_400_BAD_REQUEST
                return Response(payload, status=status_flag)
            try:
                friend_list = FriendList.objects.get(user=this_user)
            except FriendList.DoesNotExist:
                payload['Error'] = f"Could not find a friends list for {this_user.username}"
                status_flag = status.HTTP_400_BAD_REQUEST
                return Response(payload, status=status_flag)
            
            # Must be friends to view a friends list
            if user != this_user:
                if not user in friend_list.friends.all():
                    return Response("You must be friends to view their friends list.")
            friends = [] # [(friend1, True), (friend2, False), ...]
            # get the authenticated user's friend list
            auth_user_friend_list = FriendList.objects.get(user=user)
            for friend in friend_list.friends.all():
                # friend_user_serializer = CreateUserSerializer(data=friend)
                # friend_user_serializer.is_valid()
                friends.append(({"friend_username": friend.username, "user_id": friend.id}, auth_user_friend_list.is_mutual_friend(friend)))
            payload['friends'] = friends
            status_flag = status.HTTP_200_OK
    else:
        payload["Error"] = "You must be friends to view their friends list."
        status_flag = status.HTTP_400_BAD_REQUEST	
        return Response(payload, status=status_flag)
    return Response(payload, status=status_flag)

@api_view(['POST'])
@throttle_classes([UserRateThrottle])
def send_friend_request(request, *args, **kwargs):
    """
    This API will send friend request to selected user.
    """
    user = request.user
    if request.method == "POST" and user.is_authenticated:
        sender_id = user.id
        payload = {}
        receiver_id = request.data.get('receiver_id')
        if receiver_id:
            receiver = User.objects.get(pk=receiver_id)
            try:
                friend_requests = FriendRequest.objects.filter(sender=user, receiver=receiver, status__in=[FriendRequest.SEND])
                try:
                    for request in friend_requests:
                        payload['friend_request_id'] = request.id
                        raise Exception("You already sent them a friend request.")
                    friend_request = FriendRequest(sender=user, receiver=receiver, status=FriendRequest.SEND)
                    friend_request.save()
                    payload['response'] = "Friend request sent."
                    payload['friend_request_id'] = friend_request.id
                except Exception as e:
                    payload['response'] = str(e)
            except FriendRequest.DoesNotExist:
                friend_request = FriendRequest(sender=user, receiver=receiver, status=FriendRequest.SEND)
                friend_request.save()
                payload['response'] = "Friend request sent."
                payload['friend_request_id'] = friend_request.id
            
            if payload['response'] == None:
                payload['response'] = "Something went wrong."
        else:
            payload['response'] = "Unable to sent a friend request"
    else:
        payload['response'] = "You must be authenticated to send a friend request."
    return Response(payload, status=status.HTTP_200_OK)
    

@api_view(['PUT'])
def accept_friend_request(request, *args, **kwargs):
    '''
    This functions accepts Friend request.
    '''
    user = request.user
    payload = {}
    status_flag = status.HTTP_200_OK
    if request.method == "PUT" and user.is_authenticated:
        friend_request_id = kwargs.get("friend_request_id")
        if friend_request_id:
            friend_request = FriendRequest.objects.filter(pk=friend_request_id, status=FriendRequest.SEND).first()
            # confirm that is the correct request
            if friend_request:
                if friend_request.receiver == user: 
                    # Accepting the founded request
                    friend_request.accept()
                    payload['response'] = "Friend request accepted."
                    status_flag = status.HTTP_200_OK
                else:
                    payload['response'] = f"That is not {user.username}'s request to accept."
                    status_flag = status.HTTP_401_UNAUTHORIZED
            else:
                payload['response'] = "No Pending Friend request exists."
                status_flag = status.HTTP_400_BAD_REQUEST
        else:
            payload['response'] = "Unable to accept that friend request."
            status_flag = status.HTTP_400_BAD_REQUEST
    else:
        payload['response'] = "You must be authenticated to accept a friend request."
        status_flag.HTTP_401_UNAUTHORIZED
    return Response(payload, status=status_flag)

@api_view(['PUT'])
def decline_friend_request(request, *args, **kwargs):
    '''
    This function rejects Friend request.
    '''
    user = request.user
    payload = {}
    status_flag = status.HTTP_200_OK
    if request.method == "PUT" and user.is_authenticated:
        friend_request_id = kwargs.get("friend_request_id")
        if friend_request_id:
            friend_request = FriendRequest.objects.filter(pk=friend_request_id, status=FriendRequest.SEND).first()
            # confirm that is the correct request
            if friend_request:
                if friend_request.receiver == user: 
                    # Declining the founded request
                    friend_request.decline()
                    payload['response'] = "Friend request declined."
                    status_flag = status.HTTP_200_OK
                else:
                    payload['response'] = f"That is not {user.username}'s friend request to decline."
                    status_flag = status.HTTP_401_UNAUTHORIZED
            else:
                payload['response'] = "No Pending Friend request exists."
                status_flag = status.HTTP_400_BAD_REQUEST
        else:
            payload['response'] = "Unable to decline that friend request."
            status_flag = status.HTTP_400_BAD_REQUEST
    else:
        payload['response'] = "You must be authenticated to decline a friend request."
        status_flag = status.HTTP_401_UNAUTHORIZED
    return Response(payload, status=status_flag)

@api_view(['POST'])
def remove_friend(request, *args, **kwargs):
    '''
    This function removes Friend from user's FriendList.
    '''
    user = request.user
    payload = {}
    status_flag = status.HTTP_200_OK
    if request.method == "POST" and user.is_authenticated:
        user_id = request.data.get("receiver_user_id")
        if user_id:
            try:
                removee = User.objects.get(pk=user_id)
                friend_list = FriendList.objects.get(user=user)
                friend_list.unfriend(removee)
                payload['response'] = "Successfully removed that friend."
                status_flag = status.HTTP_200_OK
            except Exception as e:
                payload['response'] = f"Something went wrong: {str(e)}"
                status_flag = status.HTTP_400_BAD_REQUEST
        else:
            payload['response'] = "There was an error. Unable to remove that friend."
            status_flag = status.HTTP_400_BAD_REQUEST
    else:
        payload['response'] = "You must be authenticated to remove a friend."
        status_flag = status.HTTP_401_UNAUTHORIZED
    return Response(payload, status=status_flag)

@api_view(['GET'])
def friend_requests(request, *args, **kwargs):
    '''
    This function lists a user's All Pending Friend requests.
    '''
    payload = {}
    user = request.user
    status_flag = status.HTTP_200_OK
    if user.is_authenticated:
        user_id = kwargs.get("user_id")
        account = User.objects.get(pk=user_id)
        if account == user:
            friend_requests = FriendRequest.objects.filter(receiver=account, status=FriendRequest.SEND)
            payload['friend_requests'] = [{requests.id: requests.__str__()} for requests in list(friend_requests)] if friend_requests.exists() else None
            status_flag = status.HTTP_200_OK
        else:
            payload['error'] = "You can't view another users' friend requests."
            status_flag = status.HTTP_401_UNAUTHORIZED
            return Response(payload, status=status_flag)
    else:
        payload['error'] = "You must be authenticated to view friend requests."
        status_flag = status.HTTP_401_UNAUTHORIZED
    return Response(payload, status=status_flag)