#!/usr/bin/env python
# -*- coding:utf-8 -*-
from django.shortcuts import render, redirect
from web import models
from web.utils.md5 import gen_md5
from rbac.service.init_permission import init__permission


def login(request):
    # 1. 用户登录
    if request.method == 'GET':
        return render(request, 'login.html')
    user = request.POST.get('user')
    pwd = gen_md5(request.POST.get('pwd'))

    current_user = models.UserInfo.objects.filter(name=user, password=pwd).first()
    if not current_user:
        return render(request, 'login.html', {'msg': '用户名或密码错误'})

    # 用户权限信息的初始化
    init__permission(current_user, request)

    request.session['user_info'] = {'id': current_user.id, 'nickname': current_user.nickname}

    return redirect('/index/')


def logout(request):
    request.session.delete()
    return redirect('/login/')


def index(request):
    return render(request, 'index.html')
