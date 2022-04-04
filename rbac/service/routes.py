from collections import OrderedDict
from django.conf import settings
from django.utils.module_loading import import_string
from django.urls import URLResolver, URLPattern
import re


def check_url_exclude(url):
    """
    匹配除定制规则外的其他url
    :param url:
    :return:
    """
    for regex in settings.AUTO_DISCOVER_EXCLUDE:
        if re.match(regex,url):
            return True


def recursion_urls(pre_namespace, pre_url, urlpatterns, ordered_url_dict):
    """
    :param pre_namespace: namespace前缀 用于拼接namespace
    :param pre_url:  url前缀 用于拼接Url
    :param urlpatterns:  路由关系列表
    :param ordered_url_dict:  用于保存递归中获取的全部路由
    :return:
    """
    for item in urlpatterns:
        if isinstance(item, URLPattern):  # 最后一层
            if not item.name:  # 如果没有别名 跳过
                continue
            if pre_namespace:
                name = '%s:%s' % (pre_namespace, item.name)
            else:
                name = item.name
            url = pre_url + item.pattern.regex.pattern  # 获取带正则表达式的路径
            url = url.replace('^', '').replace('$', '')  # 去^ $

            if check_url_exclude(url):
                continue

            ordered_url_dict[name] = {'name': name, 'url': url}

        elif isinstance(item, URLResolver):  # 继续分发路由
            if pre_namespace:  # 如果父级有名称空间
                if item.namespace:  # 如果自己有名称空间
                    namespace = '%s:%s' % (pre_namespace, item.namespace)
                else:
                    namespace = item.namespace
            else:  # 父级无名称空间
                if item.namespace:  # 自己有名称空间
                    namespace = item.namespace
                else:
                    namespace = None
            recursion_urls(namespace, pre_url+item.pattern.regex.pattern, item.url_patterns, ordered_url_dict)


def get_all_url_dict():
    """
    获取所有的url
    :return:
    """
    url_ordered_dict = OrderedDict()
    """
    {
        'rbac:menu_list': { 'name': 'rbac:menu_list', 'url': 'xxx/menu/list/'}
    }
    """
    md = import_string(settings.ROOT_URLCONF)  # 根据字符串引入模块
    recursion_urls(None, '/', md.urlpatterns, url_ordered_dict)
    return url_ordered_dict
