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
    friends = models.ManyToManyField('self', related_name='my_friends', blank=True)
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