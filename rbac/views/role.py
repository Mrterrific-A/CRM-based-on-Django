from django.shortcuts import render, redirect, HttpResponse
from rbac import models
from django.urls import reverse
from rbac.forms.role import RoleModelForm


def role_list(request):
    """
    角色列表
    :param request:
    :return:
    """
    role_queryset = models.Role.objects.all()
    return render(request, 'rbac/role_list.html', {'roles': role_queryset})


def role_add(request):
    """
    添加角色
    :param request:
    :return:
    """
    if request.method == 'GET':
        form = RoleModelForm()
        return render(request, 'rbac/change.html', {'form':form})

    form = RoleModelForm(data=request.POST)  # 接收post请求中的数据
    if form.is_valid():
        form.save()  # 保存数据
        return redirect(reverse('rbac:role_list'))  # 根据别名反向解析该页面 名称空间:别名
    return render(request, 'rbac/change.html', {'form': form})  # 如果字段不合法 返回该页面并渲染错误信息


def role_edit(request,pk):
    """编辑角色"""
    obj = models.Role.objects.filter(pk=pk).first()

    if not obj:
        return HttpResponse('404')

    if request.method == 'GET':
        form = RoleModelForm(instance=obj)  # 传入要修改的对象  传入后页面会有默认值
        return render(request, 'rbac/change.html', {'form':form})

    form = RoleModelForm(instance=obj, data=request.POST)
    if form.is_valid():
        form.save()
        return redirect(reverse('rbac:role_list'))
    return render(request, 'rbac/change.html', {'form': form})


def role_del(request, pk):
    """删除角色"""
    origin_url = reverse("rbac:role_list")  # 将删除后跳转的页面url 作为参数传入
    if request.method == 'GET':
        return render(request,'rbac/delete.html',{'cancel':origin_url})

    models.Role.objects.filter(pk=pk).delete()
    return redirect(origin_url)
