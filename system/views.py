"""
The best sentence

1 Don’t hate your enemy, or you will make wrong judgment.
2 I'm gonna make him an offer he can't refuse.
3 A friend should always underestimate your virtues and an enemy overestimate your faults.
4 You know...the world’s full of lonely people afraid to make the first move
5 I suffer that slight alone,because I’m not accepted by my own people,
    because i’m not like them either! So if I'm not black enough and if I'm not white enough,
    then tell me, Tony, what am I !?
6 whatever you do,do it a hundred percent.when you work,when you laugh,laugh,when you eat,eat like it's your last meal.

@author:StrongXiuXiu
@file:
@time:2021/10/11
"""
import uuid
import base64
import datetime
import math
import time

from django.views import View
from django.contrib import auth
from django.core.cache import cache
from django.http import JsonResponse, FileResponse
from django.contrib.auth.models import User
from django.contrib.auth import login, logout
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Q
from django.db import transaction

from system import models, forms, function
from public_function import tool, web_conf, downold_file, time_dispose
from public_function.format_data import SuccessDataFormat, ErrorDataFormat, ExceptionDataFormat
from public_function.storage_api import RequestApi, GetIP
from public_function.redis_tool import RedisUtils


def log_record(*info):
    def log(func):
        """ 这是一个写入日志的装饰器"""

        def written_to_the_log(request, *arg, **kwargs):
            # '查看了所有菜单信息', "/sys/menu/list/", 3
            try:
                tokens = request.headers['Authorization']
                username = cache.get(tokens)
                a_info = info[0]
                login_ip = GetIP.get_self_ip()
                action_path = info[1]
                operating_level = info[2]
                infos = models.ActionLog(user_name=username, action_path=action_path, operating_level=operating_level,
                                         login_ip=login_ip,
                                         action_info=a_info, action_time=datetime.datetime.now())
                infos.save()
            except Exception as e:
                print(e)
            return func(request, *arg, **kwargs)

        return written_to_the_log

    return log


def params(*info):
    def login_token_auth(func):
        """ 这是一个token认证机制的装饰器"""

        def token_authentication(request, *arg, **kwargs):
            if not request.headers['Authorization']:  # 先查询请求中是否携带token
                # exec
                result = ErrorDataFormat(
                    ch_message=web_conf.sys_code["900001"], code=404).result()  # 无效的token
                return JsonResponse(result, safe=False)
            if not cache.has_key(request.headers['Authorization']):  # 证请求参数的token是否存在
                result = ErrorDataFormat(
                    ch_message=web_conf.sys_code["900002"], code=404).result()  # 登录状态过期
                return JsonResponse(result, safe=False)
            tokens = request.headers['Authorization']
            username = cache.get(tokens)
            user_id = cache.get(username)

            role_id_list = models.SysUserRole.objects.filter(user_id=user_id).values_list("role_id", flat=True)
            menu_id_list = models.SysRoleMenu.objects.filter(role_id__in=role_id_list).values_list("menu_id",
                                                                                                   flat=True)

            perms_list = models.SysMenu.objects.filter(id__in=menu_id_list).values_list("perms", flat=True)
            if not info[0] in perms_list:
                result = ErrorDataFormat(
                    ch_message=web_conf.sys_code["710013"], code=404).result()  # 没有登录权限
                return JsonResponse(result, safe=False)
            return func(request, *arg, **kwargs)

        return token_authentication

    return login_token_auth


class Login(View):
    def post(self, request):
        obj = forms.loginform(request.POST)  # 参数验证
        status = obj.is_valid()  # 开启验证
        if not status:  # status 为True 代表验证成功，否则则为失败
            result = ErrorDataFormat(
                ch_message=obj.errors).result()  # 验证数据格式错误
            return JsonResponse(result, safe=False)
        username = request.POST.get('username')
        password = request.POST.get('password')
        valid_code = request.POST.get('code')
        token = request.POST.get('token')
        code = cache.get(token)
        if code != valid_code:
            result = ErrorDataFormat(
                ch_message=web_conf.sys_code["410019"]).result()  # 验证码错误
            return JsonResponse(result, safe=False)
        cache.delete(token)
        user = auth.authenticate(request, username=username, password=password)  # 验证用户名密码
        if user:
            try:
                su = models.SysUser.objects.get(userId=user.id)
            except LookupError:
                result = ErrorDataFormat(
                    ch_message=web_conf.sys_code["800001"], code=404).result()  # 登录状态过期
                return JsonResponse(result, safe=False)
            if su.statu == 0:  # 0代表账号被禁用， 1代表账号正常
                result = ErrorDataFormat(
                    ch_message=web_conf.sys_code["800018"], code=404).result()  # 登录状态过期
                return JsonResponse(result, safe=False)

            # 登录成功，通过auth的login方法将用户写到session中
            auth.login(request, user)
            token = uuid.uuid1()  # 生成一份UUID
            cache.set(token, username, 60 * 60 * 24)  # 将用户名和token存储起来
            cache.set(username, user.id, 60 * 60 * 24)  # 将用户名和用户id存储起来
            request.session['username'] = username
            request.session['id'] = user.id
            request.session['token'] = token
            login(request, user)
            result = SuccessDataFormat(
                ch_message=web_conf.sys_code["800000"],
                code=1, data=token).result()
            return JsonResponse(result, safe=False)
        else:
            result = ErrorDataFormat(
                ch_message=web_conf.sys_code["800001"]).result()
            return JsonResponse(result, safe=False)

    def get(self, request):
        token = request.GET.get('token', "")
        username = cache.get(token)
        user_id = cache.get(username)
        if username and user_id:
            result = SuccessDataFormat(
                ch_message=web_conf.sys_code["900200"],
                code=1).result()
            return JsonResponse(result, safe=False)
        result = ErrorDataFormat(
            ch_message=web_conf.sys_code["900001"], code=404).result()  # 验证码错误
        return JsonResponse(result, safe=False)


def user_compulsory_offline(request):
    username = request.GET.get('username', "")
    user_id = cache.get(username)
    cache.delete(username)
    cache.delete(user_id)
    result = SuccessDataFormat(
        ch_message=web_conf.sys_code["210019"],
        code=1).result()
    return JsonResponse(result, safe=False)


def user_logout(request):
    username = request.session.get('username')
    logout(request)
    cache.delete(username)
    result = SuccessDataFormat(
        ch_message=web_conf.sys_code["800010"],
        code=1).result()
    return JsonResponse(result, safe=False)


class GetValidImg(View):
    def get(self, request):
        obj = tool.ValidCodeImg()  # 生成验证码
        img_data, valid_code = obj.getValidCodeImg()  # 获取验证码及图片
        token = uuid.uuid1()
        request.session['valid_code'] = valid_code
        request.session['token'] = token
        print(valid_code, token)
        cache.set(token, valid_code, 30 * 60)  # 写入key为key，值为value的缓存，有效期30分钟
        code_str = base64.b64encode(img_data)  # 转换
        img_data = "data:image/jpeg;base64," + str(code_str, 'utf-8')
        result = SuccessDataFormat(
            ch_message=web_conf.sys_code["210014"],
            data={"captchaImg": img_data, "token": token},
            code=1).result()
        return JsonResponse(result, safe=False)


# class GetUserInfo(View):
# @params(web_conf.access_code["修改用户"], web_conf.log_info_type['1001'], '查看了所有标的物信息', 3, "on") # on-off
def get_user_info(request):
    username = cache.get(request.headers['Authorization'])
    user_id = cache.get(username)
    result = SuccessDataFormat(
        ch_message=web_conf.sys_code["210016"],
        code=1, data={"username": username, "id": user_id}).result()
    return JsonResponse(result, safe=False)


# class GetMenuNav(View):
# @params(web_conf.access_code['修改菜单'], web_conf.log_info_type['1001'], '查看了所有标的物信息', 3)
def get_menu_nav(request):
    username = cache.get(request.headers['Authorization'])
    user_id = cache.get(username)
    print("用户名{},id{}".format(username, user_id))
    role_id = models.SysUserRole.objects.filter(user_id=user_id).all().values("role_id")
    authority = []
    nav = []
    if role_id:
        menu_list = models.SysRoleMenu.objects.filter(role_id=role_id[0]["role_id"]).all().values_list("menu_id",
                                                                                                       flat=True)
        res = models.SysMenu.objects.filter(id__in=menu_list).all().values().order_by("orderNum")
        for sm in res:
            authority.append(sm["perms"])
            if sm["parent_id"] == 0:
                sm_dict = {}
                sm_dict['orderNum'] = sm['orderNum']
                sm_dict['id'] = sm['id']
                sm_dict['name'] = sm['perms']
                sm_dict['title'] = sm['name']
                sm_dict['component'] = sm['component']
                sm_dict['icon'] = sm['icon']
                sm_dict['path'] = sm['path']
                sm_dict["children"] = function.back_children(res, sm["id"])
                nav.append(sm_dict)
        authority.insert(0, web_conf.role_joint + username)  # 前端界面构建的数据，需要的插入表头的特定样式
    result = SuccessDataFormat(
        ch_message=web_conf.sys_code["210016"],
        code=1, data={"nav": nav, "authority": authority}).result()
    return JsonResponse(result, safe=False)


# 保存新用户
@params(web_conf.access_code["添加用户"], web_conf.log_info_type['1001'], '查看了所有标的物信息', 3)
@log_record('添加了新的用户', "/sys/user/save/", 3, )
def user_save(request):
    if request.method == "POST":  #
        username = request.POST['username']
        password = web_conf.sys_default_password
        status = request.POST['statu']
        fullname = request.POST.get('fullName')
        phone = request.POST.get('phone')
        with transaction.atomic():  # 添加事物操作，事物操作内发生异常，回滚到最开始的状态，防止产生脏数据
            users = User.objects.create_user(
                username=username, password=password, is_staff=1)
            users.is_active = True
            # md5_password = users.password
            users.save()
            models.SysUser.objects.create(
                userId=users.id,
                username=username,
                # password=md5_password,
                fullName=fullname,
                created=datetime.datetime.now(),
                updated=datetime.datetime.now(),
                last_login=datetime.datetime.now(),
                statu=status,
                phone=phone
            )
        result = SuccessDataFormat(
            ch_message=web_conf.sys_code["210015"], code=1).result()
        return JsonResponse(result, safe=False)


# 编辑用户
@params(web_conf.access_code['修改用户'], web_conf.log_info_type['1001'])
@log_record('修改了用户的信息', "/sys/user/update/", 3, )
def user_update(request):
    if request.method == "POST":  #
        print(request.POST, 55556)
        user_id = request.POST['id']
        username = request.POST.get('username')
        status = request.POST.get('statu')
        fullname = request.POST.get('fullName')
        phone = request.POST.get('phone')
        try:
            su = models.SysUser.objects.get(userId=user_id)
        except LookupError:
            # "800404": "用户查询失败，或者用户不存在",
            result = ExceptionDataFormat(
                ch_message=web_conf.sys_code["800404"]).result()
            return JsonResponse(result, safe=False)
        try:
            user = User.objects.get(id=user_id)
        except LookupError:
            result = ExceptionDataFormat(
                ch_message=web_conf.sys_code["800015"]).result()
            return JsonResponse(result, safe=False)
        if fullname:
            su.fullName = fullname
        if phone:
            su.phone = phone
        if status:
            su.statu = status
        if username and username != su.username:
            if models.SysUser.objects.filter(username=username):
                result = ExceptionDataFormat(
                    ch_message=web_conf.sys_code["800004"]).result()
                return JsonResponse(result, safe=False)
            su.username = username
        else:
            result = ExceptionDataFormat(
                ch_message=web_conf.sys_code["800004"]).result()
            return JsonResponse(result, safe=False)
        su.save()
        # user_id = su.userId

        if user:
            print(username, user.username, 44444444444)

            if username and username != user.username:
                # username
                user.username = username
            else:
                result = ExceptionDataFormat(
                    ch_message=web_conf.sys_code["800004"]).result()
                return JsonResponse(result, safe=False)
            try:
                user.save()
            except LookupError:
                result = ExceptionDataFormat(
                    ch_message=web_conf.sys_code["800004"]).result()
                return JsonResponse(result, safe=False)

            result = SuccessDataFormat(
                ch_message=web_conf.sys_code["210015"], code=1).result()
            return JsonResponse(result, safe=False)
        else:
            result = ErrorDataFormat(
                ch_message=web_conf.sys_code["800001"]).result()
            return JsonResponse(result, safe=False)


# 用户列表
# @login_token_auth
@params(web_conf.access_code["用户管理"], web_conf.log_info_type['1001'])
@log_record('查看了用户的列表', "/sys/user/list/", 2)
def user_list(request):
    if request.method == "GET":  #
        print(request.POST, 666)
        username = request.GET.get('username', '')
        if username:
            records = models.SysUser.objects.filter(username__contains=username).values("id", 'username', "fullName",
                                                                                        "created", "updated",
                                                                                        "last_login",
                                                                                        "statu", "phone",
                                                                                        "userId").order_by("id")
        else:
            records = models.SysUser.objects.all().values("id", 'username', "fullName", "created", "updated",
                                                          "last_login",
                                                          "statu", "phone", "userId").order_by("id")
        for r in records:
            r['id'] = r["userId"]  # 两个表共用一个ID所以用user_id覆盖user # 数据库表使用问题，可优化
            syr = models.SysUserRole.objects.filter(user_id=r['id']).values_list("role_id", flat=True)
            r["sysRoles"] = SuccessDataFormat.serialize(models.SysRole.objects.filter(id__in=syr).values())
        limit = request.GET.get('size', 10)
        page = request.GET.get('current', 1)
        paginator = Paginator(records, limit)  # 分页操作
        try:
            contacts = paginator.page(page)
        except PageNotAnInteger:
            contacts = paginator.page(1)
        except EmptyPage:
            contacts = paginator.page(paginator.num_pages)
        contacts_list = SuccessDataFormat.serialize(contacts)
        return JsonResponse({"records": contacts_list, "total": paginator.count,
                             "current": int(page), "size": int(limit),
                             "pages": int((paginator.count + int(limit) - 1) // int(limit)),
                             "code": 1, "msg": web_conf.sys_code["210014"]}, safe=False)
    else:
        result = ErrorDataFormat(
            ch_message=web_conf.sys_code["800001"]).result()
        return JsonResponse(result, safe=False)


# 新增角色
@params(web_conf.access_code["添加角色"], web_conf.log_info_type['1001'])
@log_record('添加了一个系统角色', "/sys/role/save/", 3)
def role_save(request):
    if request.method == "POST":  #
        print(request.POST, 4444)
        # id = request.POST['id']
        name = request.POST['name']
        code = request.POST['code']
        statu = request.POST['statu']
        remark = request.POST.get('remark')
        if models.SysRole.objects.filter(code=code):
            # 角色唯一编码已存在,请修改后重试
            result = ErrorDataFormat(
                ch_message=web_conf.sys_code["800014"]).result()
            return JsonResponse(result, safe=False)

        # else:
        models.SysRole.objects.create(
            name=name,
            code=code,
            statu=statu,
            created=datetime.datetime.now(),
            updated=datetime.datetime.now(),
            remark=remark,
        )
        result = SuccessDataFormat(
            ch_message=web_conf.sys_code["210015"], code=1).result()
        return JsonResponse(result, safe=False)
    else:
        result = ErrorDataFormat(
            ch_message=web_conf.sys_code["410011"]).result()
        return JsonResponse(result, safe=False)


# 编辑角色
@params(web_conf.access_code["修改角色"], web_conf.log_info_type['1001'])
@log_record('修改了一个系统角色信息', "/sys/role/update/", 3)
def role_update(request):
    if request.method == "POST":  #
        print(request.POST, 4444)
        role_id = request.POST['id']
        name = request.POST.get('name')
        code = request.POST.get('code')
        statu = request.POST.get('statu')
        remark = request.POST.get('remark')
        for i in models.SysRole.objects.filter(~Q(id=role_id)).all().values():
            if i['code'] == code:
                # 角色唯一编码已存在,请修改后重试
                result = ExceptionDataFormat(
                    ch_message=web_conf.sys_code["800014"]).result()
                return JsonResponse(result, safe=False)
        try:
            sr = models.SysRole.objects.get(id=role_id)
        except LookupError:
            result = ExceptionDataFormat(
                ch_message=web_conf.sys_code["800015"]).result()
            return JsonResponse(result, safe=False)
        if name:
            sr.name = name
        if code:
            sr.code = code
        if statu:
            sr.statu = statu
        if remark:
            sr.remark = remark
        sr.save()
        result = SuccessDataFormat(
            ch_message=web_conf.sys_code["210015"], code=1).result()
        return JsonResponse(result, safe=False)
    else:
        result = ErrorDataFormat(
            ch_message=web_conf.sys_code["410011"]).result()
        return JsonResponse(result, safe=False)


# 角色删除
@params(web_conf.access_code["删除用户"], web_conf.log_info_type['1001'])
@log_record('删除了用户操作', "/sys/user/delete/", 5)
def user_delete(request, user_id):
    if request.method == "POST":  #
        print(request.POST, 123)
        # role_id = request.POST['role_id']
        User.objects.filter(id=user_id).delete()
        models.SysUser.objects.filter(userId=user_id).delete()
        models.SysUserRole.objects.filter(user_id=user_id).delete()
        result = SuccessDataFormat(
            ch_message=web_conf.sys_code["210012"], code=1).result()
        return JsonResponse(result, safe=False)
    else:
        result = ErrorDataFormat(
            ch_message=web_conf.sys_code["410011"]).result()
        return JsonResponse(result, safe=False)


# 角色删除
@params(web_conf.access_code["删除角色"], web_conf.log_info_type['1001'])
@log_record('删除了角色操作', "/sys/role/delete/", 5)
def role_delete(request, role_id):
    if request.method == "POST":  #
        print(request.POST, 123)
        # role_id = request.POST['role_id']
        if models.SysUserRole.objects.filter(role_id=role_id):
            #  "角色中还存在分配用户，请将用户移除后重试"
            result = ErrorDataFormat(
                ch_message=web_conf.sys_code["800016"]).result()
            return JsonResponse(result, safe=False)
        try:
            sr = models.SysRole.objects.get(id=role_id)
        except LookupError:
            result = ExceptionDataFormat(
                ch_message=web_conf.sys_code["800015"]).result()
            return JsonResponse(result, safe=False)
        sr.delete()
        result = SuccessDataFormat(
            ch_message=web_conf.sys_code["210012"], code=1).result()
        return JsonResponse(result, safe=False)
    else:
        result = ErrorDataFormat(
            ch_message=web_conf.sys_code["410011"]).result()
        return JsonResponse(result, safe=False)


# /sys/user/info/5 用户信息
# @login_token_auth
@params(web_conf.access_code["修改用户"], web_conf.log_info_type['1001'])
@log_record('查看了用户信息', "/sys/user/info/", 3)
def user_info(request, user_id):
    if request.method == "GET":  #
        records = models.SysUser.objects.filter(userId=user_id).all().values("id", 'username', "fullName", "created",
                                                                             "updated", "last_login",
                                                                             "statu", "phone", "userId")
        for r in records:
            r['id'] = r["userId"]  # 两个表共用一个ID所以用user_id覆盖user # 数据库表使用问题，可优化
            syr = models.SysUserRole.objects.filter(user_id=r['id']).values_list("role_id", flat=True)
            r["sysRoles"] = SuccessDataFormat.serialize(models.SysRole.objects.filter(id__in=syr).values())
        result = SuccessDataFormat(
            ch_message=web_conf.sys_code["210012"], data=records, serialize=True, code=1).result()
        return JsonResponse(result, safe=False)
    else:
        result = ErrorDataFormat(
            ch_message=web_conf.sys_code["410011"]).result()
        return JsonResponse(result, safe=False)


@params(web_conf.access_code["分配角色"], web_conf.log_info_type['1001'])
@log_record('查看了用户的角色信息', "/sys/user/role/", 1)
def user_role(request, user_id):
    if request.method == "POST":  #
        role_id_list = []  # 界面上传过来的最终都要创建的
        print(request.POST, 44)
        for k, v in request.POST.items():
            role_id_list.append(v)
        # 现在表里存在的
        with transaction.atomic():  # 添加事物操作
            role_new_list = models.SysUserRole.objects.filter(user_id=user_id).values_list('role_id', flat=True)
            for i in role_new_list:
                models.SysUserRole.objects.filter(user_id=user_id, role_id=i).delete()
            for idl in role_id_list:
                res = models.SysUserRole.objects.create(user_id=user_id, role_id=idl)
                res.save()
            result = SuccessDataFormat(
                ch_message=web_conf.sys_code["210011"], code=1).result()
            return JsonResponse(result, safe=False)
    else:
        result = ErrorDataFormat(
            ch_message=web_conf.sys_code["410011"]).result()
        return JsonResponse(result, safe=False)


# @params(web_conf.access_code["修改用户"], web_conf.log_info_type['1001'], '查看了所有标的物信息', 3)
@log_record('修改了账号密码', "/sys/user/update/password", 3)
def user_update_password(request):
    if request.method == "POST":  #
        old_password = request.POST['old_password']
        new_password = request.POST['new_password']
        confirm_password = request.POST['confirm_password']
        username = cache.get(request.headers['Authorization'])
        user = auth.authenticate(username=username, password=old_password)  # 验证用户名密码
        if user:
            if new_password == confirm_password:
                user.set_password(new_password)
                user.save()
                result = SuccessDataFormat(
                    ch_message=web_conf.sys_code["210013"], code=1).result()
                return JsonResponse(result, safe=False)
            else:
                result = ErrorDataFormat(
                    ch_message=web_conf.sys_code["800012"]).result()
                return JsonResponse(result, safe=False)
        else:
            result = ErrorDataFormat(
                ch_message=web_conf.sys_code["800017"]).result()
            return JsonResponse(result, safe=False)
    else:
        result = ErrorDataFormat(
            ch_message=web_conf.sys_code["410011"]).result()
        return JsonResponse(result, safe=False)


@params(web_conf.access_code["重置密码"], web_conf.log_info_type['1001'])
@log_record('重置了账号密码', "/sys/user/update/password", 3)
def user_reset_password(request):
    if request.method == "POST":  #
        user_id = request.POST['user_id']
        user = User.objects.get(id=user_id)
        user.set_password(web_conf.sys_default_password)
        user.save()
        result = SuccessDataFormat(
            ch_message=web_conf.sys_code["210013"], code=1).result()
        return JsonResponse(result, safe=False)
    else:
        result = ErrorDataFormat(
            ch_message=web_conf.sys_code["410011"]).result()
        return JsonResponse(result, safe=False)


# 角色列表
# @login_token_auth
@params(web_conf.access_code["角色管理"], web_conf.log_info_type['1001'], '查看了所有标的物信息', 3)
@log_record('查看了所有角色信息列表', "/sys/role/list", 1)
def role_list(request):
    if request.method == "GET":  #
        current = request.GET.get('current', 1)
        size = request.GET.get('size', 10)
        name = request.GET.get('name', "")
        if name:
            res = models.SysRole.objects.filter(name__contains=name).all().values().order_by("id")
        else:
            res = models.SysRole.objects.all().values().order_by("id")
        paginator = Paginator(res, size)  # 分页
        try:
            contacts = paginator.page(current)
        except PageNotAnInteger:
            contacts = paginator.page(1)
        except EmptyPage:
            contacts = paginator.page(paginator.num_pages)
        contacts_list = SuccessDataFormat.serialize(contacts)
        return JsonResponse({"records": contacts_list, "total": paginator.count,
                             "current": int(current), "size": int(size),
                             "pages": (paginator.count + int(size) - 1) // int(size),
                             "code": 1, "msg": web_conf.sys_code["210014"]}, safe=False)
    else:
        result = ErrorDataFormat(
            ch_message=web_conf.sys_code["410011"]).result()
        return JsonResponse(result, safe=False)


#  /sys/role/info/
# 角色信息查询接口
# @login_token_auth
@params(web_conf.access_code["修改角色"], web_conf.log_info_type['1001'])
@log_record('查看了角色信息详情', "/sys/role/info", 1)
def role_info(request, role_id):
    if request.method == "GET":  #
        res = models.SysRole.objects.filter(id=role_id).all().values()
        for i in res:
            i['menuIds'] = SuccessDataFormat.serialize(
                models.SysRoleMenu.objects.filter(role_id=role_id).values_list("menu_id", flat=True))
        result = SuccessDataFormat(
            ch_message=web_conf.sys_code["210016"], data=res, serialize=True, code=1).result()
        return JsonResponse(result, safe=False)
    else:
        result = ErrorDataFormat(
            ch_message=web_conf.sys_code["410011"]).result()
        return JsonResponse(result, safe=False)


# 角色分配权限
@params(web_conf.access_code["分配权限"], web_conf.log_info_type['1001'])
@log_record('分配了角色的权限', "/sys/role/perm", 3)
def role_perm(request, role_id):
    if request.method == "POST":  #
        print(request.POST, 4444)
        menu_id_list = []
        for k, v in request.POST.items():
            menu_id_list.append(v)
        menu_new_list = models.SysRoleMenu.objects.filter(role_id=role_id).values_list('menu_id', flat=True)
        with transaction.atomic():  # 添加事物操作
            for i in menu_new_list:
                models.SysRoleMenu.objects.filter(role_id=role_id, menu_id=i).delete()
            for menu_id in menu_id_list:
                models.SysRoleMenu.objects.create(role_id=role_id, menu_id=menu_id)
            result = SuccessDataFormat(
                ch_message=web_conf.sys_code["210011"], code=1).result()
            return JsonResponse(result, safe=False)
    else:
        result = ErrorDataFormat(
            ch_message=web_conf.sys_code["410011"]).result()
        return JsonResponse(result, safe=False)


# /sys/menu/list
# 菜单列表
# @login_token_auth

@params(web_conf.access_code["菜单管理"], web_conf.log_info_type['1001'], )
@log_record('查看了所有菜单信息', "/sys/menu/list/", 1)
def menu_list(request):
    if request.method == "GET":  #
        # authority = []
        # print(123123123312)
        nav = []
        res = models.SysMenu.objects.filter(parent_id=0).all().values().order_by("orderNum")
        all_res = models.SysMenu.objects.filter(~Q(parent_id=0)).all().values().order_by("orderNum")
        for sm in res:
            if sm["parent_id"] == 0:
                sm_dict = {}
                sm_dict['perms'] = sm['perms']
                sm_dict['orderNum'] = sm['orderNum']
                sm_dict['id'] = sm['id']
                sm_dict['name'] = sm['name']
                sm_dict['component'] = sm['component']
                sm_dict['icon'] = sm['icon']
                sm_dict['path'] = sm['path']
                sm_dict['type'] = sm['type']
                sm_dict['created'] = sm['created']
                sm_dict['updated'] = sm['updated']
                sm_dict['statu'] = sm['statu']
                sm_dict["children"] = function.back_children(all_res, sm["id"], whole=True)
                nav.append(sm_dict)
        result = SuccessDataFormat(
            ch_message=web_conf.sys_code["210016"], data=nav, code=1).result()
        # print(result, 4444)
        return JsonResponse(result, safe=False)
    else:
        result = ErrorDataFormat(
            ch_message=web_conf.sys_code["410011"]).result()
        return JsonResponse(result, safe=False)


# /sys/menu/save
# 新增角色

@params(web_conf.access_code["添加菜单"], web_conf.log_info_type['1001'])
@log_record('添加了新的菜单操作', "/sys/menu/save", 3)
def menu_save(request):
    if request.method == "POST":  #
        # print(request.POST, 5555)
        parent_id = request.POST['parent_id']  # 父ID
        name = request.POST['name']  # 名称
        perms = request.POST['perms']  # 编码
        order_num = request.POST['orderNum']  # 排序id
        status = request.POST['statu']  # 状态
        types = request.POST['type']  # 类型
        icon = request.POST.get('icon')
        path = request.POST.get('path')
        component = request.POST.get('component')
        models.SysMenu.objects.create(
            parent_id=parent_id,
            name=name,
            perms=perms,
            created=datetime.datetime.now(),
            updated=datetime.datetime.now(),
            orderNum=order_num,
            statu=status,
            type=types,
            icon=icon,
            path=path,
            component=component,
        )
        result = SuccessDataFormat(
            ch_message=web_conf.sys_code["210015"], code=1).result()
        return JsonResponse(result, safe=False)


# /sys/menu/save
# 新增角色
@params(web_conf.access_code["修改菜单"], web_conf.log_info_type['1001'])
@log_record('编辑了菜单的信息操作', "/sys/menu/update", 3)
def menu_update(request):
    if request.method == "POST":  #
        print(request.POST, 555555)
        menu_id = request.POST['id']  # 父ID
        parent_id = request.POST.get('parent_id', '')  # 父ID
        name = request.POST.get('name', '')  # 名称
        perms = request.POST.get('perms', '')  # 编码
        order_num = request.POST.get('orderNum', '')  # 排序id
        status = request.POST.get('statu', '')  # 状态
        types = request.POST.get('type', "")  # 类型
        icon = request.POST.get('icon', "")
        path = request.POST.get('path', "")
        component = request.POST.get('component', "")
        sm = models.SysMenu.objects.get(id=menu_id)
        if parent_id:
            sm.parent_id = parent_id
        if name:
            sm.name = name
        if perms:
            sm.perms = perms
        if order_num:
            sm.orderNum = order_num
        if status:
            sm.statu = status
        if types:
            sm.type = types
        if icon:
            sm.icon = icon
        if path:
            sm.path = path
        if component:
            sm.component = component
        sm.save()
        result = SuccessDataFormat(
            ch_message=web_conf.sys_code["210015"], code=1).result()
        return JsonResponse(result, safe=False)
    else:
        result = ErrorDataFormat(
            ch_message=web_conf.sys_code["410011"]).result()
        return JsonResponse(result, safe=False)


# /sys/menu/info/1
@params(web_conf.access_code["修改菜单"], web_conf.log_info_type['1001'])
@log_record('查看了菜单信息操作', "/sys/menu/save", 1)
def menu_info(request, menu_id):
    if request.method == "GET":  #
        res = models.SysMenu.objects.filter(id=menu_id).all().values()
        result = SuccessDataFormat(
            ch_message=web_conf.sys_code["210015"], data=res, serialize=True, code=1).result()
        return JsonResponse(result, safe=False)
    else:
        result = ErrorDataFormat(
            ch_message=web_conf.sys_code["410011"]).result()
        return JsonResponse(result, safe=False)


# /sys/menu/info/1

@params(web_conf.access_code["修改菜单"], web_conf.log_info_type['1001'])
@log_record('删除了菜单信息操作', "/sys/menu/delete", 5)
def menu_delete(request, menu_id):
    if request.method == "POST":  #
        print(request.POST, 555555)
        res = models.SysMenu.objects.filter(id=menu_id).all().values("id")
        for i in res:
            if models.SysMenu.objects.filter(parent_id=i["id"]):  # 如果有子菜单，那就让他删除失败直接退出了
                result = ErrorDataFormat(
                    ch_message=web_conf.sys_code["800013"], code=0).result()
                return JsonResponse(result, safe=False)
        try:
            sr = models.SysMenu.objects.get(id=menu_id)
        except Exception as e:
            print(e)
            result = ErrorDataFormat(
                ch_message=web_conf.sys_code["110113"]).result()
            return JsonResponse(result, safe=False)

        sr.delete()
        result = SuccessDataFormat(
            ch_message=web_conf.sys_code["210012"], code=1).result()
        return JsonResponse(result, safe=False)
    else:
        result = ErrorDataFormat(
            ch_message=web_conf.sys_code["410011"]).result()
        return JsonResponse(result, safe=False)


# /sys/menu/list
# psutil
# @params(web_conf.access_code["运行监控"], web_conf.log_info_type['1001'], '查看了系统的运行监控', 1, "/sys/monitoring", 'on')
def sys_monitoring(request):
    if request.method == "GET":  #
        thread_list = []
        res_name = ["network", "cpu_usage", 'memory_usage', 'IOPS']
        network1 = tool.MyThread(tool.Network().get_network_rate)  # 网络测速
        cpu1 = tool.MyThread(tool.CPU().get_usage_rate)  # cpu用量
        memory1 = tool.MyThread(tool.Memory().get_used_memory)  # 内存使用率
        iops = tool.MyThread(tool.Disk().get_disk_io)  # 磁盘IO读写次数
        network1.setDaemon(True)  # 开启守护进程
        network1.start()
        thread_list.append(network1)
        cpu1.start()
        thread_list.append(cpu1)
        memory1.start()
        thread_list.append(memory1)
        iops.start()
        thread_list.append(iops)
        res_dict = {}
        for name, tr in zip(res_name, thread_list):
            tr.join(1)
            res_dict[name] = tr.get_result()  # 获取打印的数据值
        result = SuccessDataFormat(
            ch_message=web_conf.sys_code["210016"], data=res_dict, code=1).result()
        return JsonResponse(result, safe=False)
    else:
        result = ErrorDataFormat(
            ch_message=web_conf.sys_code["410011"]).result()
        return JsonResponse(result, safe=False)


def monitor_playback(request):
    if request.method == "GET":  #
        start_time = request.GET.get('start_time', "")  # 起始时间
        end_time = request.GET.get('end_time', "")  # 当前时间
        t = datetime.datetime.now()
        if not start_time:  # 当时间没有发送的时候，默认回放12小时内的数据
            t2 = (t - datetime.timedelta(hours=12)).strftime("%Y-%m-%d %H:%M:%S")
            # 转为秒级时间戳
            start_time_tamp = time.mktime(time.strptime(t2, '%Y-%m-%d %H:%M:%S'))
            start_time = int(start_time_tamp)
        if not end_time:
            # 当前日期
            t1 = t.strftime('%Y-%m-%d %H:%M:%S')
            # 转为秒级时间戳
            end_time_tamp = time.mktime(time.strptime(t1, '%Y-%m-%d %H:%M:%S'))
            end_time = int(end_time_tamp)
        # print(type(start_time), start_time)
        start_time_int = int(start_time)  # 把字符串，或者float类型转为int
        end_time_int = int(end_time)  # 把字符串，或者float类型转为int
        start_time_str = time.localtime(start_time_int)  # 把时间戳改成2020-10-01 20:00:01
        start_time = time.strftime("%Y-%m-%d %H:%M:%S", start_time_str)
        end_time_str = time.localtime(end_time_int)
        end_time = time.strftime("%Y-%m-%d %H:%M:%S", end_time_str)
        # 小于1000的时候，说明数据量在一小时内，可以把该数据范围内的数据全部取出
        # 因为我们规定定义最多给到1800个时间点
        if end_time_int - start_time_int < 1000:
            # time_duration = end_time_int - start_time_int
            time_duration = 1  # 1 秒一次
        else:
            time_duration = math.ceil((end_time_int - start_time_int) / 1000)  # 最多给1000个点 先前取整，保证数据获取合理
        frequency = time_dispose.split_time_ranges(start_time, end_time, time_duration)  # 将剩下的时间分为最多1000份
        r = RedisUtils(host=GetIP.get_self_ip(), port=web_conf.redis_port, password=web_conf.redis_password,
                       db=web_conf.redis_db)
        timeStamp_values_list = []
        time_all = []
        for i in frequency:
            timeArray = time.strptime(i[0], "%Y-%m-%d %H:%M:%S")
            timeStamp = int(time.mktime(timeArray))
            if r.get_value(timeStamp):
                timeStamp_values_list.append(r.get_value(timeStamp))
                time_all.append(timeStamp * 1000)  # 前端界面需要精确到毫秒固*1000

        # 根据数据构造我们所需要的数据
        res = {}
        res["IOPS"] = tool.Disk().create_io_playback(timeStamp_values_list, time_all)
        res["network"] = tool.Network().create_network_playback(timeStamp_values_list, time_all)
        res["cpu_usage"] = tool.CPU().create_cpu_playback(timeStamp_values_list, time_all)
        res["memory_usage"] = tool.Memory().create_memory_playback(timeStamp_values_list, time_all)
        result = SuccessDataFormat(
            ch_message=web_conf.sys_code["210016"], data=res, code=1).result()
        return JsonResponse(result, safe=False)
    else:
        result = ErrorDataFormat(
            ch_message=web_conf.sys_code["410011"]).result()
        return JsonResponse(result, safe=False)


# @params(web_conf.access_code["节点状态"], web_conf.log_info_type['1001'], '查看了所有标的物信息', 3)
@params(web_conf.access_code["节点状态"], web_conf.log_info_type['1001'], '查看了节点的数据信息', 1, "/sys/node/info", 'on')
@log_record('查看了节点状态信息', "/sys/node/info", 1)
def node_info(request):
    if request.method == "GET":  #
        node_info_dict = {}
        node_info_dict["cpu"] = tool.CPU().get_node_info_cpu_info()  # 获取CPU信息
        node_info_dict["network"] = tool.Network().get_node_info_network()  # 获取网络网卡相关信息
        node_info_dict["memory"] = tool.Memory().get_node_info_memory_info()  # 获取内存相关信息
        node_info_dict["device_state"] = "normal"
        result = SuccessDataFormat(
            ch_message=web_conf.sys_code["210016"], data=node_info_dict, code=1).result()
        return JsonResponse(result, safe=False)
    else:
        result = ErrorDataFormat(
            ch_message=web_conf.sys_code["410011"]).result()
        return JsonResponse(result, safe=False)


# @params(web_conf.access_code["节点状态"], web_conf.log_info_type['1001'], '查看了节点的数据信息', 1, "/sys/node/info", 'on')
def all_service_state(request):
    if request.method == "GET":  #
        api = RequestApi(ip=GetIP.get_self_ip(), url="/api/all/all_service",
                         item=web_conf.default_storage_port)  # 调用8086后端服务的接口
        server_all_state_dict = {}
        for k, v in api.get_public_api().items():
            try:
                server_all_state_dict[k] = v["message"]["self_starting_state"]
            except:
                server_all_state_dict[k] = "abnormal"
        result = SuccessDataFormat(
            ch_message=web_conf.sys_code["210016"], data=server_all_state_dict, code=1).result()
        return JsonResponse(result, safe=False)
    else:
        result = ErrorDataFormat(
            ch_message=web_conf.sys_code["410011"]).result()
        return JsonResponse(result, safe=False)


def all_service_set(request):
    if request.method == "GET":  #
        server_name = request.GET['server_name']
        setstate = request.GET['setstate']
        url = None
        for k, v in web_conf.server_all_name.items():
            if k == server_name:
                url = v
        api = RequestApi(ip=GetIP.get_self_ip(), url=url, params={"serviceCmd": setstate},
                         item=web_conf.default_storage_port)  # 调用8086的接口
        # print(api.joint_url(), 44444)
        res = api.get_public_api()
        # print(res, 45555)
        if res['code'] == 1:
            result = SuccessDataFormat(
                ch_message=web_conf.sys_code["210018"], code=1).result()
            return JsonResponse(result, safe=False)
        result = ErrorDataFormat(
            ch_message=web_conf.sys_code["410020"]).result()
        return JsonResponse(result, safe=False)
    else:
        result = ErrorDataFormat(
            ch_message=web_conf.sys_code["410011"]).result()
        return JsonResponse(result, safe=False)


def operate_log(request):
    if request.method == "GET":  #
        current = request.GET.get('current', 1)
        size = request.GET.get('size', 10)
        username = request.GET.get('username', "")  # 用户名
        content = request.GET.get('content', "")  # 事件内容
        start_time = request.GET.get('start_time', "")  # 开始时间
        end_time = request.GET.get('end_time', "")  # 结束时间
        node_ip = request.GET.get('node_ip', "")  # 节点ip
        query = None
        if content:
            query = Q(action_info__contains=content)
        if username:
            if query:
                query = query & Q(user_name__contains=username)
            else:
                query = Q(user_name__contains=username)
        if node_ip:
            if query:
                query = query & Q(login_ip__contains=node_ip)
            else:
                query = Q(login_ip__contains=node_ip)

        if start_time:
            if query:
                query = query & Q(action_time__gte=start_time)  # 小于某个时间
            else:
                query = Q(action_time__gte=start_time)  # 小于某个时间
        if end_time:
            if query:
                query = query & Q(action_time__lt=end_time)
            else:
                query = Q(action_time__lt=end_time)
        if query:
            res = models.ActionLog.objects.filter(query).all().values().order_by("-action_time")
        else:
            res = models.ActionLog.objects.all().values().order_by("-action_time")
        paginator = Paginator(res, size)
        try:
            contacts = paginator.page(current)
        except PageNotAnInteger:
            contacts = paginator.page(1)
        except EmptyPage:
            contacts = paginator.page(paginator.num_pages)
        for i in contacts:
            i["action_time"] = i["action_time"].strftime('%Y-%m-%d %H:%M:%S')

        contacts_list = SuccessDataFormat.serialize(contacts)
        return JsonResponse({"records": contacts_list, "total": paginator.count,
                             "current": int(current), "size": int(size),
                             "pages": (paginator.count + int(size) - 1) // int(size),
                             "code": 1, "msg": web_conf.sys_code["210014"]}, safe=False)
    else:
        result = ErrorDataFormat(
            ch_message=web_conf.sys_code["410011"]).result()
        return JsonResponse(result, safe=False)


def alarm_log(request):
    if request.method == "GET":  #
        current = request.GET.get('current', 1)
        size = request.GET.get('size', 10)
        username = request.GET.get('username', "")  # 用户名
        content = request.GET.get('content', "")  # 事件内容
        start_time = request.GET.get('start_time', "")  # 开始时间
        end_time = request.GET.get('end_time', "")  # 结束时间
        node_ip = request.GET.get('node_ip', "")  # 节点ip
        status = request.GET.get('status', "")  # 节点ip
        query = None
        if content:
            query = Q(action_info__contains=content)
        if username:
            if query:
                query = query & Q(user_name__contains=username)
            else:
                query = Q(user_name__contains=username)
        if node_ip:
            if query:
                query = query & Q(login_ip__contains=node_ip)
            else:
                query = Q(login_ip__contains=node_ip)

        if start_time:
            if query:
                query = query & Q(action_time__gte=start_time)  # 小于某个时间
            else:
                query = Q(action_time__gte=start_time)  # 小于某个时间
        if end_time:
            if query:
                query = query & Q(action_time__lt=end_time)
            else:
                query = Q(action_time__lt=end_time)
        if query:
            res = models.ActionLog.objects.filter(query).all().values().order_by("-action_time")
        else:
            res = models.ActionLog.objects.all().values().order_by("-action_time")
        paginator = Paginator(res, size)
        try:
            contacts = paginator.page(current)
        except PageNotAnInteger:
            contacts = paginator.page(1)
        except EmptyPage:
            contacts = paginator.page(paginator.num_pages)
        for i in contacts:
            i["action_time"] = i["action_time"].strftime('%Y-%m-%d %H:%M:%S')
        contacts_list = SuccessDataFormat.serialize(contacts)
        return JsonResponse({"records": contacts_list, "total": paginator.count,
                             "current": int(current), "size": int(size),
                             "pages": (paginator.count + int(size) - 1) // int(size),
                             "code": 1, "msg": web_conf.sys_code["210014"]}, safe=False)
    else:
        result = ErrorDataFormat(
            ch_message=web_conf.sys_code["410011"]).result()
        return JsonResponse(result, safe=False)


def storage_log(request):
    if request.method == "GET":  #
        current = request.GET.get('current', 1)
        size = request.GET.get('size', 10)
        username = request.GET.get('username', "")  # 用户名
        content = request.GET.get('content', "")  # 事件内容
        start_time = request.GET.get('start_time', "")  # 开始时间
        end_time = request.GET.get('end_time', "")  # 结束时间
        node_ip = request.GET.get('node_ip', "")  # 节点ip
        file_name = request.GET.get('file_name', "")  # 节点ip
        query = None
        if content:
            query = Q(action_info__contains=content)
        if username:
            if query:
                query = query & Q(user_name__contains=username)
            else:
                query = Q(user_name__contains=username)
        if node_ip:
            if query:
                query = query & Q(login_ip__contains=node_ip)
            else:
                query = Q(login_ip__contains=node_ip)

        if start_time:
            if query:
                query = query & Q(action_time__gte=start_time)  # 小于某个时间
            else:
                query = Q(action_time__gte=start_time)  # 小于某个时间
        if end_time:
            if query:
                query = query & Q(action_time__lt=end_time)
            else:
                query = Q(action_time__lt=end_time)
        if query:
            res = models.ActionLog.objects.filter(query).all().values().order_by("-action_time")
        else:
            res = models.ActionLog.objects.all().values().order_by("-action_time")
        paginator = Paginator(res, size)
        try:
            contacts = paginator.page(current)
        except PageNotAnInteger:
            contacts = paginator.page(1)
        except EmptyPage:
            contacts = paginator.page(paginator.num_pages)
        for i in contacts:
            i["action_time"] = i["action_time"].strftime('%Y-%m-%d %H:%M:%S')
        contacts_list = SuccessDataFormat.serialize(contacts)
        return JsonResponse({"records": contacts_list, "total": paginator.count,
                             "current": int(current), "size": int(size),
                             "pages": (paginator.count + int(size) - 1) // int(size),
                             "code": 1, "msg": web_conf.sys_code["210014"]}, safe=False)
    else:
        result = ErrorDataFormat(
            ch_message=web_conf.sys_code["410011"]).result()
        return JsonResponse(result, safe=False)


def download_log(request):
    if request.method == "GET":  #
        username = request.GET.get('username', "")  # 用户名
        content = request.GET.get('content', "")  # 事件内容
        start_time = request.GET.get('start_time', "")  # 开始时间
        end_time = request.GET.get('end_time', "")  # 结束时间
        node_ip = request.GET.get('node_ip', "")  # 节点ip
        query = None
        if content:
            query = Q(action_info__contains=content)
        if username:
            if query:
                query = query & Q(user_name__contains=username)
            else:
                query = Q(user_name__contains=username)
        if node_ip:
            if query:
                query = query & Q(login_ip__contains=node_ip)
            else:
                query = Q(login_ip__contains=node_ip)
        if start_time:
            start_time = start_time.strftime('%Y-%m-%d %H:%M:%S')
            if query:
                query = query & Q(action_time__gte=start_time)  # 小于某个时间
            else:
                query = Q(action_time__gte=start_time)  # 小于某个时间
        if end_time:
            end_time = end_time.strftime('%Y-%m-%d %H:%M:%S')
            if query:
                query = query & Q(action_time__lt=end_time)
            else:
                query = Q(action_time__lt=end_time)
        if query:
            res = models.ActionLog.objects.filter(query).all().values().order_by("-action_time")
        else:
            res = models.ActionLog.objects.all().values().order_by("-action_time")
        downold_file.excel_obj(res)
        file = open(web_conf.download_log_path, 'rb')
        response = FileResponse(file)
        response['Content-Type'] = 'application/octet-stream'
        response['Content-Disposition'] = 'attachment;filename="auction_log.xls"'
        return response
    else:
        result = ErrorDataFormat(
            ch_message=web_conf.sys_code["410011"]).result()
        return JsonResponse(result, safe=False)


def log_strategy(request):
    if request.method == "GET":  #
        expiration_day = request.GET.get('expiration_day', "")  # 过期时间
        backups_day = request.GET.get('backups_day', "")  # 备份时间
        backups_time = request.GET.get('backups_time', "")  # 开始时间
        configuration = web_conf.Configuration()
        if expiration_day:
            configuration.set_items("log", "expiration_day", expiration_day)
        if backups_day:
            configuration.set_items("log", "backups_day", backups_day)
        if backups_time:
            configuration.set_items("log", "backups_time", backups_time)
        result = SuccessDataFormat(
            ch_message=web_conf.sys_code["210015"],
            code=1).result()
        return JsonResponse(result, safe=False)


def log_configuration_information(request):
    configuration = web_conf.Configuration()
    res = configuration.get_items("log")
    log_config_dict = {}
    for i in res:
        try:
            log_config_dict[i[0]] = i[1]
        except Exception as e:
            print(e)
            result = ErrorDataFormat(
                ch_message=web_conf.sys_code["510012"]).result()
            return JsonResponse(result, safe=False)
    result = SuccessDataFormat(
        ch_message=web_conf.sys_code["210016"], data=log_config_dict,
        code=1).result()
    return JsonResponse(result, safe=False)


# 所有网卡配置信息
def all_network_card_information(request):
    api = RequestApi(ip=GetIP.get_self_ip(), url="/api/network/net_info",
                     item=web_conf.default_storage_port)  # # 先调用网卡信息的合集，拿出所有的网卡信息
    if api.get_public_api()["code"] == 1:
        api.url = "/api/network/net_nmcli_connection"
        print(api.get_public_api(), 333)

        for i in api.get_public_api()["message"]:
            i["name"]
        api.url = "/api/network/net_nmcli_connection_show"

    result = SuccessDataFormat(
        ch_message=web_conf.sys_code["210016"], data=api.get_public_api()["message"],
        code=1).result()
    return JsonResponse(result, safe=False)


# 添加网卡配置文件
def add_network_card_config(request):
    """
        名称	类型	必填	参数位置	默认值	备注
        conn_type	string	false	普通参数	ethernet	配置类型
        options	string	false	普通参数	None	{'ipv4.addresses': '192.168.9.19/24','ipv4.gateway': '192.168.9.255','ipv4.method': 'manual'}
        ifname	string	false	普通参数	*	网卡名
        name	string	false	普通参数	None	配置文件名
        autoconnect	boolean	false	普通参数	False	自动连接
    """
    options_dict = {}
    if request.POST.get("addresses"):
        options_dict["ipv4.addresses"] = request.POST.get("addresses")
    if request.POST.get("gateway"):
        options_dict["ipv4.gateway"] = request.POST.get("gateway")
    if request.POST.get("method"):
        options_dict["ipv4.method"] = request.POST.get("method")
    ifname = request.POST.get("ifname")
    name = request.POST.get("name")
    autoconnect = request.POST.get("autoconnect", "False")
    api = RequestApi(ip=GetIP.get_self_ip(), url="/api/network/net_nmcli_connection_add",
                     params={
                         "options": options_dict,
                         "ifname": ifname,
                         "name": name,
                         "autoconnect": autoconnect},
                     item=web_conf.default_storage_port)  # 调用8086后端服务的接口
    result = SuccessDataFormat(
        ch_message=web_conf.sys_code["210016"], data=api.get_public_api(),
        code=1).result()
    return JsonResponse(result, safe=False)


# 添加/编辑网卡配置文件
def add_modify_network_card_config(request):
    options_dict = {}
    if request.POST.get("addresses"):
        options_dict["ipv4.addresses"] = request.POST.get("addresses")
    if request.POST.get("gateway"):
        options_dict["ipv4.gateway"] = request.POST.get("gateway")
    if request.POST.get("method"):
        options_dict["ipv4.method"] = request.POST.get("method")
    ifname = request.POST.get("ifname")
    config_name = request.POST.get("config_name", "")
    autoconnect = request.POST.get("autoconnect", "False")
    if config_name:  # 有配置文件，就修改.反之则新增
        api = RequestApi(ip=GetIP.get_self_ip(), url="/api/network/net_nmcli_connection_modify",
                         params={
                             "options": options_dict,
                             "ifname": ifname,
                             "name": config_name,
                             "autoconnect": autoconnect},
                         item=web_conf.default_storage_port, )  # 调用8086后端服务的接口
    else:
        config_name = ifname + "_1"  # 该网卡啊没有配置文件的情况下，给拼接一个配置文件生成新的
        api = RequestApi(ip=GetIP.get_self_ip(), url="/api/network/net_nmcli_connection_add",
                         params={
                             "options": options_dict,
                             "ifname": ifname,
                             "name": config_name,
                             "autoconnect": autoconnect},
                         item=web_conf.default_storage_port)  # 调用8086后端服务的接口
    result = SuccessDataFormat(
        ch_message=web_conf.sys_code["210016"], data=api.get_public_api(),
        code=1).result()
    return JsonResponse(result, safe=False)


# 删除网卡配置文件
def delete_network_card_config(request):
    config_name = request.POST["config_name"]  # 配置文件名称
    api = RequestApi(ip=GetIP.get_self_ip(), url="/api/network/net_nmcli_connection_delete",
                     params={"name": config_name},
                     item=web_conf.default_storage_port)  # 调用8086后端服务的接口
    result = SuccessDataFormat(
        ch_message=web_conf.sys_code["210016"], data=api.get_public_api(),
        code=1).result()
    return JsonResponse(result, safe=False)


# 激活网卡配置文件
def activate_network_card_config(request):
    config_name = request.POST["config_name"]  # 配置文件名称
    api = RequestApi(ip=GetIP.get_self_ip(), url="/api/network/net_nmcli_connection_up",
                     params={"name": config_name},
                     item=web_conf.default_storage_port)  # 调用8086后端服务的接口
    result = SuccessDataFormat(
        ch_message=web_conf.sys_code["210016"], data=api.get_public_api(),
        code=1).result()
    return JsonResponse(result, safe=False)


# 取消激活网卡配置文件
def deactivate_network_card_config(request):
    config_name = request.POST["config_name"]  # 配置文件名称
    api = RequestApi(ip=GetIP.get_self_ip(), url="/api/network/net_nmcli_connection_down",
                     params={"name": config_name},
                     item=web_conf.default_storage_port)  # 调用8086后端服务的接口
    result = SuccessDataFormat(
        ch_message=web_conf.sys_code["210016"], data=api.get_public_api(),
        code=1).result()
    return JsonResponse(result, safe=False)


# @params(web_conf.log_info_type['1001'], '查看了所有标的物信息', 3)
@log_record(1, 22, 3, 4, 5)
def test(request):
    # print(request.headers['Authorization'])
    res = [
        {"1637086106": {'bond1_input': 0.0, 'bond1_output': 0.0, 'ens37_input': 0.64453125, 'ens37_output': 0.64453125,
                        'lo_input': 363.166015625, 'lo_output': 363.166015625, 'ens33_input': 3.818359375,
                        'ens33_output': 3.818359375,
                        'ens38_input': 0.64453125, 'ens38_output': 0.64453125},
         "1637086107": {'bond1_input': 0.0, 'bond1_output': 0.0, 'ens37_input': 0.64453125, 'ens37_output': 0.64453125,
                        'lo_input': 363.166015625, 'lo_output': 363.166015625, 'ens33_input': 3.818359375,
                        'ens33_output': 3.818359375,
                        'ens38_input': 0.64453125, 'ens38_output': 0.64453125},

         "1637086108": {'bond1_input': 0.0, 'bond1_output': 0.0, 'ens37_input': 0.64453125, 'ens37_output': 0.64453125,
                        'lo_input': 363.166015625, 'lo_output': 363.166015625, 'ens33_input': 3.818359375,
                        'ens33_output': 3.818359375,
                        'ens38_input': 0.64453125, 'ens38_output': 0.64453125},
         "1637086109": {'bond1_input': 0.0, 'bond1_output': 0.0, 'ens37_input': 0.64453125, 'ens37_output': 0.64453125,
                        'lo_input': 363.166015625, 'lo_output': 363.166015625, 'ens33_input': 3.818359375,
                        'ens33_output': 3.818359375,
                        'ens38_input': 0.64453125, 'ens38_output': 0.64453125},
         "1637086110": {'bond1_input': 0.0, 'bond1_output': 0.0, 'ens37_input': 0.64453125, 'ens37_output': 0.64453125,
                        'lo_input': 363.166015625, 'lo_output': 363.166015625, 'ens33_input': 3.818359375,
                        'ens33_output': 3.818359375,
                        'ens38_input': 0.64453125, 'ens38_output': 0.64453125},
         "1637086111": {'bond1_input': 0.0, 'bond1_output': 0.0, 'ens37_input': 0.64453125, 'ens37_output': 0.64453125,
                        'lo_input': 363.166015625, 'lo_output': 363.166015625, 'ens33_input': 3.818359375,
                        'ens33_output': 3.818359375,
                        'ens38_input': 0.64453125, 'ens38_output': 0.64453125},
         "1637086112": {'bond1_input': 0.0, 'bond1_output': 0.0, 'ens37_input': 0.64453125, 'ens37_output': 0.64453125,
                        'lo_input': 363.166015625, 'lo_output': 363.166015625, 'ens33_input': 3.818359375,
                        'ens33_output': 3.818359375,
                        'ens38_input': 0.64453125, 'ens38_output': 0.64453125},
         "1637086113": {'bond1_input': 0.0, 'bond1_output': 0.0, 'ens37_input': 0.64453125, 'ens37_output': 0.64453125,
                        'lo_input': 363.166015625, 'lo_output': 363.166015625, 'ens33_input': 3.818359375,
                        'ens33_output': 3.818359375,
                        'ens38_input': 0.64453125, 'ens38_output': 0.64453125},
         "1637086114": {'bond1_input': 0.0, 'bond1_output': 0.0, 'ens37_input': 0.64453125, 'ens37_output': 0.64453125,
                        'lo_input': 363.166015625, 'lo_output': 363.166015625, 'ens33_input': 3.818359375,
                        'ens33_output': 3.818359375,
                        'ens38_input': 0.64453125, 'ens38_output': 0.64453125},
         "1637086115": {'bond1_input': 0.0, 'bond1_output': 0.0, 'ens37_input': 0.64453125, 'ens37_output': 0.64453125,
                        'lo_input': 363.166015625, 'lo_output': 363.166015625, 'ens33_input': 3.818359375,
                        'ens33_output': 3.818359375,
                        'ens38_input': 0.64453125, 'ens38_output': 0.64453125}}
    ]
    # username = cache.get(request.headers['Authorization'], default=None, version=None)
    # username = request.session.get('username')
    # logout(request)
    # cache.delete(username)
    result = SuccessDataFormat(
        ch_message=web_conf.sys_code["800010"], data=res,
        code=1).result()
    return JsonResponse(result, safe=False)


class Test(View):
    @params(web_conf.log_info_type['1001'], '查看了所有标的物信息', 3)
    def get(self, request):
        # print(request.headers['Authorization'])
        username = cache.get(request.headers['Authorization'], default=None, version=None)
        print(username, 33444)
        # username = request.session.get('username')
        # logout(request)
        # cache.delete(username)
        result = SuccessDataFormat(
            ch_message=web_conf.sys_code["800010"],
            code=1).result()
        return JsonResponse(result, safe=False)
