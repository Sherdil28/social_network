from django.contrib import admin

# Register your models here.

from accounts.models import FriendList, FriendRequest

# admin.site.register(FriendList)
# admin.site.register(FriendRequest)

@admin.register(FriendRequest)
class FrienRequestAdmin(admin.ModelAdmin):
    list_display = ["sender", "receiver", "status", "created", "updated"]

@admin.register(FriendList)
class FriendListAdmin(admin.ModelAdmin):
    list_display = ["user"]