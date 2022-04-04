import re
from django.template import Library
from django.conf import settings
from collections import OrderedDict  # 导入有序字典
from rbac.service import urls
register = Library()


# @register.inclusion_tag('rbac/static_menu.html')  # 将此函数返回的结果放到该模板中渲染 渲染后返回给调用该标签的模板页
# def static_menu(request):
#     menu_list = request.session[settings.LUFFY_PERMISSION_URL_MENU]
#     return {'menu_list': menu_list}

# 动态二级菜单
@register.inclusion_tag('rbac/multi_menu.html')
def multi_menu(request):
    menu_dict = request.session[settings.MENU_SESSION_KEY]
    key_list = sorted(menu_dict)  # 对字典的key进行排序
    ordered_dict = OrderedDict()  # 字典是无序的数据结构 因此要确保二级菜单顺序固定
    for key in key_list:
        val = menu_dict[key]
        val['class'] = 'hide'  # 每一次将一级菜单重置 隐藏起来
        for per in val['children']:
            if request.current_selected_menu == per['id']:  # 如果当前网址的id或pid 与一级菜单的id对应
                val['class'] = ''  # 一级菜单拉出
                per['class'] = 'active'  # 二级菜单被选中

        ordered_dict[key] = val

    return {'menu_dict': ordered_dict}

# 导航栏
@register.inclusion_tag('rbac/breadcrumb.html')
def breadcrumb(request):
    return {'breadcrumb': request.breadcrumb}


# 校验权限
@register.filter
def has_permission(request, name):
    permission_dict = request.session[settings.PERMISSION_SESSION_KEY]
    if name in permission_dict:
        return True


@register.simple_tag
def memory_url(request, name, *args, **kwargs):
    """
    生成带有原搜索条件的url 将原搜索条件放入参数_filter中
    :param request:
    :param name: 别名
    :return:
    """
    return urls.memory_url(request, name, *args, **kwargs)

