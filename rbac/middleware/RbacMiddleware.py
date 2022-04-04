import re
from django.utils.deprecation import MiddlewareMixin
from django.shortcuts import HttpResponse
from django.conf import settings


class RbacMiddleware(MiddlewareMixin):

    def process_request(self, request):
        current_url = request.path_info  # 返回域名后的网址 不带参数

        # 校验访问网址是否在白名单内
        for white in settings.WHITE_LIST:  # 白名单不需要任何权限
            url = '^%s$' % white  # 正则匹配  有的网址以..开头 以..结尾

            if re.match(url, current_url):
                return None  # 进入下一个中间件

        permission_dict = request.session.get(settings.PERMISSION_SESSION_KEY)  # 获取权限列表 get方法权限为空时不会报错

        if not permission_dict:
            return HttpResponse('未获取到用户权限信息，请登录')

        record_url = [{
            'title': '首页',
            'url': '#'
        }]

        for url in settings.NO_PERMISSION_LIST:
            # 需要登陆但无需校验的权限
            if re.match(url, request.path_info):
                request.current_selected_menu = 0
                request.breadcrumb = record_url
                return None

        flag = False  # 校验有否有权限访问该网址

        for permission in permission_dict.values():
            url = "^%s$" % permission['url']  # 正则匹配网址 可以加一些约束 如^$
            if re.match(url, current_url):
                flag = True
                request.current_selected_menu = permission['id'] or permission['pid']  # 查看自身是否为菜单 若不是则查找自身所属的菜单

                if not permission['pid']:
                    record_url.extend([{'url': permission['url'], 'title': permission['title'], 'class':'active'}]) # 一级菜单为最后一项
                else:
                    record_url.extend([
                        {'url': permission['p_url'], 'title': permission['p_title']},
                        {'url': permission['url'], 'title': permission['title'],'class':'active'}, # 二级菜单为最后一项 最后一项加上class:'active
                    ])
                request.breadcrumb = record_url
                break

        if not flag:
            return HttpResponse('无权访问')
