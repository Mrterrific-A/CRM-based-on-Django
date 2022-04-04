from django.urls import reverse
from django.http import QueryDict


def memory_url(request, name, *args,**kwargs):
    """
    生成携带原参数的url
    :param request:
    :param name:
    :param args:
    :param kwargs:
    :return:
    """
    basic_url = reverse(name, args=args, kwargs=kwargs)  # 生成要跳转的原始url 有参数则根据参数生成
    if not request.GET:
        return basic_url
    query_dict = QueryDict(mutable=True)
    query_dict['_filter'] = request.GET.urlencode()  # request.GET.urlencode() 得到后面的一串参数
    # query_dict.urlencode() 对后面的参数中的特殊符号进行转义 将后面的所有参数打包成一个值
    return "%s?%s" % (basic_url, query_dict.urlencode())


def memory_reverse(request, name, *args, **kwargs):
    """
    反向生成携带原参数的url
    :param request:
    :param name:
    :param args:
    :param kwargs:
    :return:
    """
    url = reverse(name, args=args, kwargs=kwargs)
    origin_params = request.GET.get('_filter')  # 获取原来的参数
    if origin_params:
        url = '%s?%s' % (url, origin_params)
    return url

