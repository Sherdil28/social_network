from django.db import models
from django.contrib.auth.models import User

from django.contrib.auth.models import BaseUserManager, AbstractBaseUser, PermissionsMixin, AbstractUser, UserManager
from django.db.models import Q

# class CustomUserManager(UserManager):

#     def get_by_natural_key(self, username):
#         return self.get(
#             Q(**{self.model.USERNAME_FIELD: username}) |
#             Q(**{self.model.EMAIL_FIELD: username})
#         )
    
# class User(AbstractUser):
#     objects = CustomUserManager()

# class UserAccountManager(BaseUserManager):
#    def create_user(self, email, password=None, **extra_fields):
#        email = self.normalize_email(email)
#        user = self.model(email=email, **extra_fields)

#        user.set_password(password)
#        user.save()

#        return user

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    first_name = models.CharField(blank=True, max_length=20, null=True)
    last_name = models.CharField(blank=True, max_length=20, null=True)
    is_online = models.BooleanField(default=False)
    # friends = models.ManyToManyField('self', related_name='my_friends', blank=True)
    bio = models.CharField(default="",blank=True,null=True,max_length=350)
    date_of_birth = models.CharField(blank=True,max_length=150)
    updated = models.DateTimeField(auto_now=True)
    created = models.DateTimeField(auto_now_add=True)
    # image = models.ImageField(default='default.jpg', upload_to='profile_pics',blank=True, null=True)


    def get_full_name(self):
        return f"{self.first_name} {self.last_name}"

    def get_friends(self):
        return self.friends.all()

    def get_friends_no(self):
        return self.friends.all().count()

    def __str__(self):
        return f'{self.user.username} Profile'


# class UserAccount(AbstractBaseUser, PermissionsMixin):
#     email = models.EmailField(max_length=255, unique=True)
#     first_name = models.CharField(max_length=255)
#     last_name = models.CharField(max_length=255)
#     is_online = models.BooleanField(default=False)
#     friends = models.ManyToManyField('self', related_name='my_friends', blank=True)
#     bio = models.CharField(default="",blank=True,null=True,max_length=350)
#     date_of_birth = models.CharField(blank=True,max_length=150)
#     updated = models.DateTimeField(auto_now=True)
#     created = models.DateTimeField(auto_now_add=True)


class FriendRequest(models.Model):
    SEND = 'send'
    ACCEPTED = 'accepted'
    REJECTED = 'rejected'
    STATUS_CHOICES = (
    ('send','send'),
    ('accepted','accepted'),
    ('rejected', 'rejected')
)
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='friend_sender')
    receiver = models.ForeignKey(User, on_delete=models.CASCADE, related_name='friend_receiver')
    status = models.CharField(max_length=8, choices=STATUS_CHOICES)
    updated = models.DateTimeField(auto_now=True)
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.sender}-{self.receiver}-{self.status}"
    
    def accept(self):
        # update both sender and receiver friend list
        receiver_friend_list, flag = FriendList.objects.get_or_create(user=self.receiver)
        if receiver_friend_list:
            receiver_friend_list.add_friend(self.sender)
            sender_friend_list, flag = FriendList.objects.get_or_create(user=self.sender)
            if sender_friend_list:
                sender_friend_list.add_friend(self.receiver)
                self.status = FriendRequest.ACCEPTED
                self.save()

    def decline(self):
        self.status = FriendRequest.REJECTED
        self.save()

    def cancel(self):
        self.status = FriendRequest.REJECTED
        self.save()
    

""" FriendList model """
class FriendList(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='user')
    friends = models.ManyToManyField(User, blank=True, related_name='friends')
    
    def __str__(self):
        return self.user.username

    def add_friend(self, account):
        if not account in self.friends.all():
            self.friends.add(account)
            self.save()

    def remove_friend(self, account):
        if account in self.friends.all():
            self.friends.remove(account)
            self.save()

    def unfriend(self, removee):
        remover_friends_list = self
        remover_friends_list.remove_friend(removee)

        friends_list = FriendList.objects.get(user=removee)
        friends_list.remove_friend(self.user)

    def is_mutual_friend(self, friend):
        if friend in self.friends.all():
            return True
        return False
