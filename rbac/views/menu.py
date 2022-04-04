from django.shortcuts import render, redirect, HttpResponse
from django.forms import formset_factory
from django.conf import settings
from django.utils.module_loading import import_string
from rbac import models
from rbac.forms.menu import MenuModelForm, SecondMenuModelForm, PermissionModelForm, MultiAddPermissionForm, MultiUpdatePermissionForm
from rbac.service.urls import memory_reverse
from rbac.service.routes import get_all_url_dict
from collections import OrderedDict


def menu_list(request):
    """菜单列表"""
    menus = models.Menu.objects.all()
    menu_id = request.GET.get('mid')
    second_menus_id = request.GET.get('sid')
    menu_exist = models.Menu.objects.filter(id=menu_id).exists()  # 如果无此id
    if not menu_exist:
        menu_id = None

    if menu_id:
        second_menus = models.Permission.objects.filter(menu_id=menu_id)
    else:
        second_menus = []  # 不选择一级菜单时 二级菜单为空

    second_menu_exist = models.Menu.objects.filter(id=menu_id).exists()  # 如果无此id
    if not second_menu_exist:
        second_menus_id = None

    if second_menus_id:
        permissions = models.Permission.objects.filter(pid_id=second_menus_id)  # 拿到不能作为二级菜单的权限
    else:
        permissions = []

    return render(
        request,
        'rbac/menu_list.html',
        {
            'menus': menus,
            'permissions':permissions,
            'second_menus': second_menus,
            'second_menus_id': second_menus_id,
            'menu_id': menu_id
        }
    )


def menu_add(request):
    """添加菜单"""
    if request.method == 'GET':
        form = MenuModelForm()
        return render(request, 'rbac/change.html', {'form': form})

    form = MenuModelForm(data=request.POST)  # 接收post请求中的数据
    if form.is_valid():
        form.save()  # 保存数据
        return redirect(memory_reverse(request, 'rbac:menu_list'))
    return render(request, 'rbac/change.html', {'form': form})  # 如果字段不合法 返回该页面并渲染错误信息


def menu_edit(request,pk):
    """编辑菜单"""
    obj = models.Menu.objects.filter(pk=pk).first()

    if not obj:
        return HttpResponse('404')

    if request.method == 'GET':
        form = MenuModelForm(instance=obj)  # 传入要修改的对象  传入后页面会有默认值
        return render(request, 'rbac/change.html', {'form': form})

    form = MenuModelForm(instance=obj, data=request.POST)
    if form.is_valid():
        form.save()
        return redirect(memory_reverse(request, 'rbac:menu_list')) # 根据别名反向解析该页面 名称空间:别名

    return render(request, 'rbac/change.html', {'form': form})


def menu_del(request,pk):
    """"删除菜单"""
    url = memory_reverse(request, 'rbac:menu_list') # 将删除后跳转的页面url 作为参数传入
    if request.method == 'GET':
        return render(request, 'rbac/delete.html', {'cancel': url})

    models.Menu.objects.filter(pk=pk).delete()

    return redirect(url)  # 根据别名反向解析该页面 名称空间:别名


def second_menu_add(request, menu_id):
    """添加二级菜单"""
    if request.method == 'GET':
        menu_obj = models.Menu.objects.filter(id=menu_id).first()
        form = SecondMenuModelForm(initial={'menu': menu_obj})  # 作默认选中
        return render(request, 'rbac/change.html', {'form': form})

    form = SecondMenuModelForm(data=request.POST)  # 接收post请求中的数据
    if form.is_valid():
        form.save()  # 保存数据
        return redirect(memory_reverse(request, 'rbac:menu_list'))
    return render(request, 'rbac/change.html', {'form': form})  # 如果字段不合法 返回该页面并渲染错误信息


def second_menu_edit(request, pk):
    """编辑二级菜单"""
    menu_obj = models.Permission.objects.filter(id=pk).first()

    if not menu_obj:
        return HttpResponse('404')

    if request.method == 'GET':
        form = SecondMenuModelForm(instance=menu_obj)
        return render(request, 'rbac/change.html', {'form': form})

    form = SecondMenuModelForm(instance=menu_obj, data=request.POST)
    if form.is_valid():
        form.save()
        return redirect(memory_reverse(request, 'rbac:menu_list'))

    return render(request, 'rbac/change.html', {'form': form})


def second_menu_del(request, pk):
    """删除二级菜单"""
    url = memory_reverse(request, 'rbac:menu_list') # 将删除后跳转的页面url 作为参数传入
    if request.method == 'GET':
        return render(request, 'rbac/delete.html', {'cancel': url})

    models.Permission.objects.filter(pk=pk).delete()

    return redirect(url)  # 根据别名反向解析该页面 名称空间:别名


def permission_add(request, second_menu_id):
    """添加权限"""
    if request.method == 'GET':
        form = PermissionModelForm()  # 作默认选中
        return render(request, 'rbac/change.html', {'form': form})

    form = PermissionModelForm(data=request.POST)  # 接收post请求中的数据
    if form.is_valid():
        second_menu_obj = models.Permission.objects.filter(id=second_menu_id).first()
        # form.instance 包含用户提交的所有值 并生成一个对象  instance = models.Permission(title='', name='', url='')
        form.instance.pid = second_menu_obj
        form.save()  # 保存数据
        return redirect(memory_reverse(request, 'rbac:menu_list'))
    return render(request, 'rbac/change.html', {'form': form})  # 如果字段不合法 返回该页面并渲染错误信息


def permission_edit(request, pk):
    """编辑权限"""
    menu_obj = models.Permission.objects.filter(id=pk).first()

    if not menu_obj:
        return HttpResponse('404')

    if request.method == 'GET':
        form = PermissionModelForm(instance=menu_obj)
        return render(request, 'rbac/change.html', {'form': form})

    form = PermissionModelForm(instance=menu_obj, data=request.POST)
    if form.is_valid():
        form.save()
        return redirect(memory_reverse(request, 'rbac:menu_list'))

    return render(request, 'rbac/change.html', {'form': form})


def permission_del(request, pk):
    """删除权限"""
    url = memory_reverse(request, 'rbac:menu_list')  # 将删除后跳转的页面url 作为参数传入
    if request.method == 'GET':
        return render(request, 'rbac/delete.html', {'cancel': url})

    models.Permission.objects.filter(pk=pk).delete()

    return redirect(url)  # 根据别名反向解析该页面 名称空间:别名


def multi_permissions(request):
    """
    批量操作权限
    :param request:
    :return:
    """
    post_type = request.GET.get('type')
    generate_formset_class = formset_factory(MultiAddPermissionForm, extra=0)
    update_formset_class = formset_factory(MultiUpdatePermissionForm, extra=0)

    generate_formset = None
    update_formset = None

    if request.method == 'POST' and post_type == 'generate':
        formset = generate_formset_class(data=request.POST)
        if formset.is_valid():
            object_list = []
            post_row_list = formset.cleaned_data
            has_error = False
            for i in range(0, formset.total_form_count()):
                row_dict = post_row_list[i]  # 循环每行数据
                try:
                    new_object = models.Permission(**row_dict)
                    new_object.validate_unique()  # 作唯一性校验
                    object_list.append(new_object)
                except Exception as e:
                    formset.errors[i].update(e)
                    generate_formset = formset
                    has_error = True

            if not has_error:  # 如果没有错误 批量加入数据库
                models.Permission.objects.bulk_create(object_list, batch_size=100)  # 批量增加 第一个参数为列表 第二个参数一次性可以加多少个
        else:
            generate_formset = formset

    if request.method == 'POST' and post_type == 'update':
        formset = update_formset_class(data=request.POST)
        print(request.POST)
        if formset.is_valid():
            post_row_list = formset.cleaned_data
            for i in range(0, formset.total_form_count()):
                row_dict = post_row_list[i]
                permission_id = row_dict.pop('id')
                try:
                    row_object = models.Permission.objects.filter(id=permission_id).first()  # 找到这个对象
                    for k, v in row_dict.items():
                        setattr(row_object, k, v)  # 将修改后的值 赋给对应的属性
                    row_object.validate_unique()
                    row_object.save()
                except Exception as e:
                    formset.errors[i].update(e)
                    update_formset = formset
        else:
            update_formset = formset

    all_url_dict = get_all_url_dict()
    router_name_set = set(all_url_dict.keys())  # 获取所有自动找到的url的别名

    all_permissions = models.Permission.objects.all().values('id', 'title', 'name', 'url', 'menu_id', 'pid_id')  # 获取数据库中的所有Url信息
    permissions_dict = OrderedDict()
    permission_name_set = set()  # 数据库中所有url的别名
    for row in all_permissions:
        permissions_dict[row['name']] = row
        permission_name_set.add(row['name'])

    # 检测路由和数据库的url是否一致
    for name, item in permissions_dict.items():
        router_row_dict = all_url_dict.get(name)
        if not router_row_dict:
            continue
        if router_row_dict['url'] != item['url']:
            item['url'] = '路由和数据库不一致'

    if not generate_formset:
        # 自动找到 但在数据库中没有的 url 应添加
        generate_name_list = router_name_set - permission_name_set
        generate_formset = generate_formset_class(
            initial=[row_dict for name, row_dict in all_url_dict.items() if name in generate_name_list]
        )

    # 数据库中有 但自动获取没有的url 应删除
    delete_name_list = permission_name_set - router_name_set
    delete_row_list = [row_dict for name, row_dict in permissions_dict.items() if name in delete_name_list]

    if not update_formset:
        # 数据库中有 自动获取也有的 待更新 显示到页面中
        update_name_list = router_name_set & permission_name_set

        update_formset = update_formset_class(
            initial=[row_dict for name, row_dict in permissions_dict.items() if name in update_name_list]  # 数据库的数据更全面 以数据库为准
        )

    return render(request,
                  'rbac/multi_permissions.html',
                  {
                      'generate_formset': generate_formset,
                      'delete_row_list': delete_row_list,
                      'update_formset': update_formset
                  }
                  )


def multi_permissions_del(request, pk):
    """
    删除批量操作的权限
    :param request:
    :param pk:
    :return:
    """
    url = memory_reverse(request, 'rbac:multi_permissions')  # 将删除后跳转的页面url 作为参数传入
    if request.method == 'GET':
        return render(request, 'rbac/delete.html', {'cancel': url})

    models.Permission.objects.filter(pk=pk).delete()

    return redirect(url)  # 根据别名反向解析该页面 名称空间:别名


def distribute_permissions(request):
    """分配权限"""
    user_id = request.GET.get('uid')

    user_model_class = import_string(settings.RBAC_USER_MODEL_CLASS)  # 业务中的用户表 导入这个类

    user_object = user_model_class.objects.filter(id=user_id).first()

    role_id = request.GET.get('rid')
    role_object = models.Role.objects.filter(id=role_id).first()

    if not user_object:
        user_id = None
    if not role_object:
        role_id = None

    if request.method == 'POST' and request.POST.get('type') == 'role':
        role_id_list = request.POST.getlist('roles')
        if not user_object:
            return HttpResponse('请选择用户，然后再分配角色')
        user_object.roles.set(role_id_list)  # 多对多 往第三张表中更新数据

    if request.method == 'POST' and request.POST.get('type') == 'permission':
        permission_id_list = request.POST.getlist('permissions')
        if not role_object:
            return HttpResponse('请选择角色，然后再分配权限')
        role_object.permissions.set(permission_id_list)

    # 获取当前用户所有的角色
    if user_id:
        user_has_roles = user_object.roles.all()
    else:
        user_has_roles = []
    user_has_roles_dict = {item.id: None for item in user_has_roles}  # 转换成字典 查找速度更快

    # 如果有选中的角色优先显示选中角色所拥有的权限
    # 有过没有选中角色才显示用户所拥有的权限
    if role_id:
        user_has_permissions = role_object.permissions.all()
        user_has_permissions_dict = {item.id: None for item in user_has_permissions}
    elif user_object:  # 未选角色但选择了用户
        user_has_permissions = user_object.roles.filter(permissions__id__isnull=False).values('id', 'permissions').distinct()
        user_has_permissions_dict = {item['permissions']: None for item in user_has_permissions}  # item['permissions'] 为权限id
    else:
        user_has_permissions_dict = {}

    all_user_list = user_model_class.objects.all()
    all_role_list = models.Role.objects.all()
    all_menu_list = models.Menu.objects.all().values('id', 'title')
    all_menu_dict = {}

    for row in all_menu_list:
        row['children'] = []  # 用于放二级菜单
        all_menu_dict[row['id']] = row  # 将列表变为字典 便于下一级菜单对键值的查找 并且列表字典修改的内部是同一个字典 共享同一片内存空间

    all_second_menu_list = models.Permission.objects.filter(menu_id__isnull=False).values('id', 'title', 'menu_id')
    all_second_menu_dict = {}

    for row in all_second_menu_list:
        row['children'] = []  # 以装入下一级权限
        all_second_menu_dict[row['id']] = row

        menu_id = row['menu_id']
        all_menu_dict[menu_id]['children'].append(row)  # 将二级菜单加入对应的一级菜单

    # 所有不能做菜单的权限
    all_permission_list = models.Permission.objects.filter(menu_id__isnull=True).values('id', 'title', 'pid_id')

    for row in all_permission_list:
        pid = row['pid_id']
        if not pid:
            continue
        all_second_menu_dict[pid]['children'].append(row)

    return render(request, 'rbac/distribute_permissions.html',
                      {
                          'all_user_list': all_user_list,
                          'all_role_list': all_role_list,
                          'all_menu_list': all_menu_list,
                          'user_id': user_id,
                          'role_id':role_id,
                          'user_has_roles_dict': user_has_roles_dict,
                          'user_has_permissions_dict': user_has_permissions_dict

                      }
                  )