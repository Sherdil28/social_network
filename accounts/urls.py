from django.urls import include, path
from rest_framework import routers

from accounts import views, viewsets

app_name = 'accounts'

# router = routers.DefaultRouter()
# router.register(r'search/', viewsets.SearchViewSet, basename='search-profiles')

urlpatterns = [
    path('profile/', views.CreateProfileView.as_view(), name='create-user'),
    # path('search/', viewsets.SearchViewSet.as_view, name='search-profiles'),
    path('search/', views.Search.as_view(), name='search-profiles')
    

]