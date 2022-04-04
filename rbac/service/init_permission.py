from django.conf import settings


def init__permission(current_user, request):
    permission_list = current_user.roles.filter(permissions__isnull=False).values("permissions__id",
                                                                                  "permissions__url",
                                                                                  "permissions__title",
                                                                                  "permissions__name",
                                                                                  "permissions__pid_id",
                                                                                  "permissions__pid__title",
                                                                                  "permissions__pid__url",
                                                                                  "permissions__menu_id",
                                                                                  "permissions__menu__title",
                                                                                  "permissions__menu__icon").distinct()
    # permissions__isnull=False 防止用户权限为空  distinct() 去重
    permission_dict = {}  # 列表生成式  用作权限校验
    menu_dict = {}
    for permission in permission_list:
        permission_dict[permission["permissions__name"]] = {  # 别名作为键值 目的是在模板上可以使用别名
            'id': permission['permissions__id'],
            'url': permission['permissions__url'],
            'title': permission['permissions__title'],
            'pid': permission['permissions__pid_id'],  # 自身是否是菜单 不为null 则指向默认菜单的id
            'p_title': permission['permissions__pid__title'],  # 导航条 得到之前所有的路径
            'p_url': permission['permissions__pid__url'],
        }

        menu_id = permission['permissions__menu_id']  # 一级菜单ID
        if not menu_id:
            continue
        node = {'id': permission['permissions__id'], 'title': permission['permissions__title'], 'url': permission['permissions__url']}
        if menu_id in menu_dict:
            # 若所属一级菜单存在 则将二级菜单加入所属一级菜单的字典
            menu_dict[menu_id]['children'].append(node)
        else:
            # 若所属一级菜单不存在 则添加一级菜单
            menu_dict[menu_id] = {
                'title': permission['permissions__menu__title'],
                'icon': permission['permissions__menu__icon'],
                'children': [node]
            }

    request.session[settings.PERMISSION_SESSION_KEY] = permission_dict  # 权限写入session
    request.session[settings.MENU_SESSION_KEY] = menu_dict
