import datetime

from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User


# Create your models here.
class SysMenu(models.Model):
    id = models.BigAutoField(primary_key=True)
    parent_id = models.BigIntegerField(verbose_name="父菜单ID，一级菜单为0", blank=True, null=True)
    name = models.CharField(max_length=64, blank=False, null=False)
    path = models.CharField(max_length=255, blank=True, null=True, verbose_name="菜单URL")
    perms = models.CharField(max_length=255, blank=True, null=True, verbose_name="授权(多个用逗号分隔，如：user:list,user:create)")
    component = models.CharField(max_length=255, blank=True, null=True, )
    type = models.IntegerField(blank=True, verbose_name="类型 0：目录  1：菜单  2：按钮")  #
    icon = models.CharField(max_length=32, blank=True, null=True, verbose_name="菜单图标")
    orderNum = models.IntegerField(blank=True, null=True, verbose_name="排序")
    created = models.DateTimeField(default=timezone.now, blank=False, null=False)
    updated = models.DateTimeField(default=timezone.now, null=True, blank=True)
    statu = models.IntegerField(blank=False, null=False, verbose_name="代码为状态,单词少写了个s")

    def __str__(self):
        return str(self.id)

    class Meta:
        db_table = 'sys_menu'  # 通过db_table自定义数据表名


# Create your models here.
class SysRole(models.Model):
    id = models.BigAutoField(primary_key=True)
    name = models.CharField(max_length=64, blank=False, null=False)
    code = models.CharField(max_length=64, blank=False, null=False)
    remark = models.CharField(max_length=64, blank=True, null=True)
    created = models.DateTimeField(default=timezone.now, blank=True, null=True)
    updated = models.DateTimeField(default=timezone.now, blank=True, null=True)
    statu = models.IntegerField(blank=False, null=False, verbose_name="代码为状态，单词少写了个s")

    def __str__(self):
        return str(self.id)

    class Meta:
        db_table = 'sys_role'  # 通过db_table自定义数据表名


# Create your models here.
class SysRoleMenu(models.Model):
    id = models.BigAutoField(primary_key=True)
    role_id = models.BigIntegerField(blank=False, null=False)
    menu_id = models.BigIntegerField(blank=False, null=False)

    def __str__(self):
        return str(self.id)

    class Meta:
        db_table = 'sys_role_menu'  # 通过db_table自定义数据表名


class SysUser(models.Model):
    # user = models.OneToOneField(User, on_delete=models.CASCADE,
    #                             related_name='profile')
    # id = models.BigAutoField(primary_key=True)
    username = models.CharField(max_length=64, blank=True, null=True)
    password = models.CharField(max_length=64, blank=True, null=True)
    fullName = models.CharField(max_length=64, blank=True, null=True)
    created = models.DateTimeField(default=timezone.now, blank=True, null=True)
    updated = models.DateTimeField(default=timezone.now, blank=True, null=True)
    last_login = models.DateTimeField(default=timezone.now, blank=True, null=True)  #
    statu = models.IntegerField(blank=False, null=False, verbose_name="代码为状态，单词少写了个s")  #
    phone = models.CharField(max_length=64, blank=True, null=True)
    userId =  models.IntegerField(blank=False, null=False, verbose_name="用户的id")
    # def __str__(self):
    #     return str(self.id)

    class Meta:
        db_table = 'sys_user'  # 通过db_table自定义数据表名


# Create your models here.
class SysUserRole(models.Model):
    id = models.BigAutoField(primary_key=True)
    user_id = models.BigIntegerField(blank=False, null=False)  # uuid
    role_id = models.BigIntegerField(blank=False, null=False)  # uuid

    def __str__(self):
        return str(self.id)

    class Meta:
        db_table = 'sys_user_role'  # 通过db_table自定义数据表名


class ActionLog(models.Model):
    user_name = models.CharField(max_length=50, blank=False)
    login_ip = models.CharField(max_length=50, blank=False)
    action_info = models.CharField(max_length=50, blank=False)
    action_path = models.CharField(max_length=50, blank=False)
    action_time = models.DateTimeField(default=timezone.now)
    operating_level = models.CharField(max_length=50, blank=False)
    remark = models.CharField(max_length=50, blank=False)

    def __str__(self):
        return self.login_ip

    class Meta:
        db_table = 'SysActionLog'  # 通过db_table自定义数据表名
