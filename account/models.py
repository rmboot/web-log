from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.timezone import now


# Create your models here.

class WebLogUser(AbstractUser):
    nickname = models.CharField('昵称', max_length=100, blank=True)
    created_time = models.DateTimeField('创建时间', default=now)
    last_mod_time = models.DateTimeField('修改时间', default=now)

    def __str__(self):
        return self.email

    class Meta:
        ordering = ['-id']
        verbose_name = "用户"
        verbose_name_plural = verbose_name
        get_latest_by = 'id'
