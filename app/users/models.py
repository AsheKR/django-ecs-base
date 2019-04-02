from django.contrib.auth.models import AbstractUser
from django.db.models import CharField


class User(AbstractUser):
    name = CharField("닉네임", blank=True, max_length=255)

    # def get_absolute_url(self):
    #     return reverse("users:detail", kwargs={"username": self.username})
