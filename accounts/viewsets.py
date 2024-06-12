"""
This file contains viewsets for calling actual views.
"""
from accounts.views import Search
from rest_framework import viewsets, status
from rest_framework.response import Response

# class ProfileViewSet(viewsets.ViewSet):
#     def create(self, request):




class SearchViewSet(viewsets.ViewSet):
    
    def list(self, request, *args, **kwargs):
        search_view = Search(request)
        response = search_view.execute_search()
        if response:
            return Response(response, status=status.HTTP_200_OK)
        else:
            response = {"Error":"No matching results found."}
            return Response(response, status=status.HTTP_204_NO_CONTENT)