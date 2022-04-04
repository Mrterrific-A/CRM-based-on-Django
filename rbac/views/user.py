from django.shortcuts import render, redirect, HttpResponse
from rbac import models
from django.urls import reverse
from rbac.forms.user import UserModelForm, UpdateUserModelForm, ResetpwdUserModelForm


def user_list(request):
    """
    用户列表
    :param request:
    :return:
    """
    user_queryset = models.UserInfo.objects.all()
    return render(request, 'rbac/user_list.html', {'users': user_queryset})


def user_add(request):
    """添加用户"""
    if request.method == 'GET':
        form = UserModelForm()
        return render(request, 'rbac/change.html', {'form':form})

    form = UserModelForm(data=request.POST)  # 接收post请求中的数据
    if form.is_valid():
        form.save()  # 保存数据
        return redirect(reverse('rbac:user_list'))  # 根据别名反向解析该页面 名称空间:别名
    return render(request, 'rbac/change.html', {'form': form})  # 如果字段不合法 返回该页面并渲染错误信息


def user_edit(request, pk):
    """
    编辑用户
    :param request:
    :param pk:
    :return:
    """
    obj = models.UserInfo.objects.filter(pk=pk).first()

    if not obj:
        return HttpResponse('404')

    if request.method == 'GET':
        form = UpdateUserModelForm(instance=obj)  # 传入要修改的对象
        return render(request, 'rbac/change.html', {'form': form})

    form = UpdateUserModelForm(instance=obj, data=request.POST)
    if form.is_valid():
        form.save()
        return redirect(reverse('rbac:user_list'))
    return render(request, 'rbac/change.html', {'form': form})


def user_reset_pwd(request, pk):
    """
    密码重置
    :param request:
    :param pk:
    :return:
    """
    obj = models.UserInfo.objects.filter(pk=pk).first()

    if not obj:
        return HttpResponse('404')

    if request.method == 'GET':
        form = ResetpwdUserModelForm()
        return render(request, 'rbac/change.html', {'form': form})

    form = ResetpwdUserModelForm(instance=obj, data=request.POST)
    if form.is_valid():
        form.save()
        return redirect(reverse('rbac:user_list'))
    return render(request, 'rbac/change.html', {'form': form})


def user_del(request, pk):
    """
    删除用户
    :param request:
    :param pk:
    :return:
    """
    origin_url = reverse("rbac:user_list")
    if request.method == 'GET':
        return render(request,'rbac/delete.html',{'cancel':origin_url})

    models.UserInfo.objects.filter(pk=pk).delete()
    return redirect(origin_url)
