from django.db import models
from django.contrib.auth.models import AbstractBaseUser,BaseUserManager,PermissionsMixin
from django.db import connection
import string
import random

# Create your models here.

class UserManager(BaseUserManager) :
    use_in_migrations = True    
    
    def create_user(self, username, password, email, **extra_fields):
        cursor = connection.cursor()
        uid = ""
        while (True) :
            letters_set = string.ascii_letters
            num = random.randrange(1, 10) # 1부터 9 사이의 난수 생성
            random_list = random.sample(letters_set, num)
            random_str = f"U{''.join(random_list)}"

            post_list_sql = f'SELECT COUNT(*) FROM user WHERE user_id="{random_str}";'
            cursor.execute(post_list_sql)
            user_num = int(cursor.fetchone()[0])

            if (user_num == 0) : 
                uid = random_str
                break

        user = self.model(user_id=uid,
                          username=username, 
                          email=self.normalize_email(email), 
                          **extra_fields)
        user.set_password(password)  # 비밀번호를 해싱하여 저장
        user.save(using=self._db)
        return user
    
    def create_superuser(self, username, password, email, **extra_fields):
        # 슈퍼유저 생성 로직 작성
        user = self.create_user(username, password, email=self.normalize_email(email), **extra_fields)
        user.is_admin = True    
        user.is_superuser = True
        user.is_staff = True
        user.is_adult = True
        user.save(using=self._db)
        return user

class User(AbstractBaseUser, PermissionsMixin):
    objects = UserManager()
    
    user_id = models.CharField(primary_key=True, max_length=10)
    username = models.CharField(max_length=16, unique=True)
    password = models.CharField(max_length=200)
    profile_image = models.CharField(max_length=512, null=True)
    email = models.EmailField(max_length=255, unique=True)
    verified = models.BooleanField(blank=True, null=True, default=False)
    birthday = models.DateField(editable=True, null=True)
    is_adult = models.BooleanField(default=False)

    is_active = models.BooleanField(default=True)
    is_admin = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)
    date_joined = models.DateTimeField(auto_now_add=True)
    last_login = models.DateTimeField(null=True, blank=True)

    USERNAME_FIELD = 'email'
    EMAIL_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    class Meta:
        db_table = 'user'
    
    @classmethod
    def get_email_field_name(cls):
        try:
            return cls.EMAIL_FIELD
        except AttributeError:
            return "email"