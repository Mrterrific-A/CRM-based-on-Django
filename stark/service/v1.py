from django.conf.urls import url
from django.shortcuts import HttpResponse, render, redirect
from types import FunctionType
from django.utils.safestring import mark_safe
from django.urls import reverse
from stark.utils.pagination import Pagination
from django.http import QueryDict
from django import forms
from django.db.models import Q
from django.db.models.fields import related
import functools


def get_choice_text(title, field, *args, **kwargs):
    """
    对于Stark组件中定义列时，choice如果想要显示中文信息调用此方法
    :param title:
    :param field:
    :return:
    """

    def inner(self, obj=None, is_head=None, *args, **kwargs):
        """
        闭包
        :param self:
        :param obj:
        :param is_head:
        :return:
        """
        if is_head:
            return title
        method = 'get_%s_display' % field  # get_字段_display 可以通过选择的choice中的数字显示中文
        return getattr(obj, method)()

    return inner


def get_datetime_text(title, field, format_type='%Y-%m-%d', *args, **kwargs):
    """
    对于Stark组件中定义列时，定制日期格式
    :param title: 表头
    :param field: 字段
    :param format_type: 格式化的格式
    :return:
    """
    def inner(self, obj=None, is_head=None, *args, **kwargs):
        if is_head:
            return title
        datetime_value = getattr(obj, field)
        return datetime_value.strftime(format_type)

    return inner


def get_m2m_text(title, field, *args, **kwargs):
    """
    对于Stark组件中定义列时，显示many_to_many中的信息
    :param title: 表头
    :param field: 字段
    :return:
    """
    def inner(self, obj=None, is_head=None, *args, **kwargs):
        if is_head:
            return title
        query_set = getattr(obj, field).all()  # 获取对象列表
        text_list = [str(row) for row in query_set]
        return ','.join(text_list)  # 拼接显示
    return inner


class SearchGroupRow(object):
    """将搜索得到的不同条件类型(元组，Queryset)封装成一个统一的对象"""
    # 如果一个类中定义了__iter__方法且该方法返回了一个迭代器，那么该类实例化的对象是一个可迭代对象
    # 生成器是特殊的迭代器
    def __init__(self, title, queryset_or_tuple, option, query_dict):
        """
        :param title: 组合搜索的列名称
        :param queryset_or_tuple: 组合搜索关联获取到的数据
        :param option: 搜索字段对应的option对象
        :param query_dict: request.GET
        """
        self.title = title
        self.queryset_or_tuple = queryset_or_tuple
        self.option = option
        self.query_dict = query_dict

    def __iter__(self):
        yield "<div class='whole'>"
        yield self.title + ':'
        yield "</div>"
        yield "<div class='others'>"
        total_query_dict = self.query_dict.copy()
        total_query_dict._mutable = True
        origin_value_list = self.query_dict.getlist(self.option.field)  # 获取此字段的请求值列表
        if origin_value_list:
            total_query_dict.pop(self.option.field)  # 如果有参数 点击全部时应把参数除掉
            yield "<a href='?%s'>全部</a>" % total_query_dict.urlencode()
        else:  # 如果没有参数则选择全部
            yield "<a class='active'  href='?%s'>全部</a>" % total_query_dict.urlencode()

        for item in self.queryset_or_tuple:
            text = self.option.get_text_func(item)
            value = str(self.option.get_value_func(item))
            # 3 运营 <QueryDict: {'gender': ['1'], 'depart': ['3']}>
            # print(value, text , self.query_dict)
            query_dict = self.query_dict.copy()  # 深拷贝 修改值不会影响原来request.GET的值
            query_dict._mutable = True  # QueryDict默认不可被修改 是对HTTP请求数据包中携带的数据的封装

            if not self.option.is_multi:  # 单选
                query_dict[self.option.field] = value
                if value in origin_value_list:  # 如果是选中的值 则添加active样式
                    query_dict.pop(self.option.field)  # 如果已选中 再点击则去掉该选择
                    yield "<a class='active' href='?%s'>%s</a>" % (query_dict.urlencode(), text)  # urlencode() 将请求的url变成字符串
                else:
                    yield "<a href='?%s'>%s</a>" % (query_dict.urlencode(), text)  # urlencode() 将请求的url变成字符串
            else:  # 多选
                multi_value_list = query_dict.getlist(self.option.field)
                if value in multi_value_list:
                    multi_value_list.remove(value)  # 如果在里面 移除地址(两次点击消除)
                    query_dict.setlist(self.option.field, multi_value_list)
                    yield "<a class='active' href='?%s'>%s</a>" % (query_dict.urlencode(), text)
                else:
                    multi_value_list.append(value)
                    query_dict.setlist(self.option.field, multi_value_list)  # setlist(key, list) 修改key对应的列表
                    yield "<a href='?%s'>%s</a>" % (query_dict.urlencode(), text)

        yield "</div>"


class Option(object):
    def __init__(self, field, is_multi=False, db_condition=None, text_func=None, value_func=None):
        """
        :param field: 组合搜索关联的字段
        :param db_condition: 数据库关联查询时的条件
        :param text_func: 用于显示组合搜索按钮页面文本
        :param value_func: 用于显示组合搜索按钮值
        """
        self.field = field
        if not db_condition:
            db_condition = {}
        self.db_condition = db_condition
        self.text_func = text_func
        self.value_func = value_func
        self.is_multi = is_multi

        self.is_choice = False

    def get_db_condition(self, request, *args, **kwargs):
        """可自定义类重写该方法 以自定制搜索条件"""
        return self.db_condition

    def get_queryset_or_tuple(self, model_class, request, *args, **kwargs):
        """
        根据字段获取数据库关联的数据
        :return:
        """
        field_obj = model_class._meta.get_field(self.field)
        title = field_obj.verbose_name
        # related.RelatedField 可判断该字段是否关联表 用于一对多 多对多
        # field_obj.related_model 获取关联的表对象
        if isinstance(field_obj, related.RelatedField):
            db_condition = self.get_db_condition(request, *args, **kwargs)
            # 获取关联表中的数据 Queryset
            return SearchGroupRow(title, field_obj.related_model.objects.filter(**db_condition), self, request.GET)
        else:
            #  获取choice中的数据 元组
            self.is_choice = True
            return SearchGroupRow(title, field_obj.choices, self, request.GET)

    def get_text_func(self, field_object):
        """获取文本函数"""
        # 自定制
        if self.text_func:
            return self.text_func

        # 默认方法
        if self.is_choice:
            return field_object[1]

        return str(field_object)

    def get_value_func(self, field_object):
        """获取按钮值函数"""
        # 自定制
        if self.value_func:
            return self.value_func

        # 默认方法
        if self.is_choice:
            return field_object[0]  # (1,'男')

        return field_object.pk


class StarkModelForm(forms.ModelForm):
    """modelform基类"""

    def __init__(self, *args, **kwargs):
        super(StarkModelForm, self).__init__(*args, **kwargs)  # 继承父类方法

        for name, field in self.fields.items():  # name为字符串 field为各个字段生成的对象
            field.widget.attrs['class'] = 'form-control'  # 为所有的对象添加属性


class StarkForm(forms.Form):
    """form基类"""

    def __init__(self, *args, **kwargs):
        super(StarkForm, self).__init__(*args, **kwargs)  # 继承父类方法
        # 给form字段添加样式
        for name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control'


class StarkHandler(object):
    """
    视图函数的父类
    """
    list_display = []
    per_page_count = 10
    has_add_btn = True
    model_from_class = None
    order_list = []
    search_list = []
    action_list = []
    search_group = []

    list_template = None
    change_template = None
    add_template = None
    delete_template = None

    def __init__(self, model_class, prev, site):
        self.model_class = model_class
        self.prev = prev  # 获取前缀来区分别名
        self.site = site  # 将starksite对象传入 来获取名称空间 用于反向解析
        self.request = None

    def get_search_group(self):
        """得到搜索条件"""
        return self.search_group

    def get_search_group_condition(self, request):
        """
        获取组合搜索的条件
        :param request:
        :return:
        """
        condition = {}
        for option in self.get_search_group():
            if option.is_multi:  # 单选
                values_list = request.GET.getlist(option.field)  # 获取请求字段的值 使用getlist方法是为了适用与于多选
                if not values_list:
                    continue
                condition['%s__in' % option.field] = values_list
            else:  # 多选
                value = request.GET.get(option.field)  # 直接用get方法
                if not value:
                    continue
                condition[option.field] = value  # 直接查找字段
        return condition

    def multi_delete(self, request, *args, **kwargs):
        """
        批量删除 可以定制返回值 来跳转别的页面或者其他操作
        :return:
        """
        pk_list = request.POST.getlist('pk')
        self.model_class.objects.filter(id__in=pk_list).delete()
        # return redirect('http://www.baidu.com')

    multi_delete.text = '批量删除'

    def get_action_list(self):
        """批量操作"""
        return self.action_list

    def get_search_list(self):
        """模糊查找"""
        return self.search_list

    def get_order_list(self):
        """获取排序字段"""
        if self.order_list:
            return self.order_list
        return ['-id', ]

    def get_model_from(self, is_add, request, pk, *args, **kwargs):
        """
        定制添加和编辑页面ModelForm的定制
        :return:
        """
        if self.model_from_class:
            return self.model_from_class

        class DynamicForm(StarkModelForm):
            class Meta:
                model = self.model_class
                fields = '__all__'

        return DynamicForm

    def get_add_btn(self, request, *args, **kwargs):
        """根据别名反向生成添加页面的url"""
        if self.has_add_btn:
            return '<a class="btn btn-primary" href="%s">添加</a>' % self.reverse_add_url(*args, **kwargs)
        return None

    def display_checkbox(self, obj=None, is_head=None, *args, **kwargs):
        """
        生成下拉框
        :return:
        """
        if is_head:
            return '选择'
        return mark_safe("<input type='checkbox' name='pk' value='%s'>" % obj.pk)

    def display_edit(self, obj=None, is_head=None, *args, **kwargs):
        """
        编辑按钮
        :param obj:
        :param is_head:是否是表头
        :return:
        """
        if is_head:
            return '操作'
        return mark_safe("<a href='%s'>编辑</a>" % self.reverse_change_url(pk=obj.pk))
        # mark_safe可以是字符串形式的标签以标签形式显示出来
        # reverse 反向解析url

    def display_del(self, obj=None, is_head=None, *args, **kwargs):
        """
        删除按钮
        :param obj:
        :param is_head:
        :return:
        """
        if is_head:
            return '操作'
        return mark_safe("<a href='%s'>删除</a>" % self.reverse_delete_url(pk=obj.pk))

    def display_edit_del(self, obj=None, is_head=None, *args, **kwargs):
        """删除编辑在一栏中"""
        if is_head:
            return '操作'
        return mark_safe("<a href='%s'>编辑</a> <a href='%s'>删除</a>" %
                         (self.reverse_change_url(pk=obj.pk), self.reverse_delete_url(pk=obj.pk)))

    def get_list_display(self, request, *args, **kwargs):
        """
        获取页面上应该显示的列，预留自定义扩展，即可根据不同用户展示出不同的列
        :return:
        """
        value = []
        if self.list_display:
            value.extend(self.list_display)  # 如果直接子类没有handler方法 则直接拿取子类的list_display
            value.append(type(self).display_edit_del)  # 默认每张表生成编辑删除功能
        return value

    def get_queryset(self, request, *args, **kwargs):
        """可对数据进行自定制过滤"""
        return self.model_class.objects

    def list_view(self, request, *args, **kwargs):
        """
        列表展示页面
        :param request:
        :return:
        """

        #######################批量操作#############################
        # 如果直接往模板中传入函数 传入的函数会自动执行 所以用字典的形式传送过去
        action_list = self.get_action_list()
        action_dict = {func.__name__: func.text for func in action_list}  # func.__name__可以通过函数得到函数名

        if request.method == 'POST':
            action_func_name = request.POST.get('action')
            if action_func_name and action_func_name in action_dict:  # 防止用户修改函数名传入后台
                action_response = getattr(self, action_func_name)(request, *args, **kwargs)
                if action_response:
                    return action_response  # 如果批量操作后想要跳转别的页面 可通过返回值

        # 模糊查找(条件是__contains 为模糊查找，如果为字段则是精确查找,查找字段与ORM模糊查找的规定方式相同)
        search_list = self.get_search_list()
        search_value = request.GET.get('q', '')
        conn = Q()  # filter是and型的查找  如果想用复杂的查找条件 要用Q()
        conn.connector = 'OR'
        if search_value:
            for item in search_list:
                conn.children.append((item, search_value))

        prev_queryset = self.get_queryset(request, *args, **kwargs)
        query_set = prev_queryset.filter(conn)  # 如果有条件 根据条件查找  没有条件则查找全部

        ################################## 处理分页##############################
        all_count = query_set.count()
        query_params = request.GET.copy()  # ?page=1&level=2  此对象默认不可以被修改
        query_params._mutable = True  # 使其可以被修改

        pager = Pagination(
            current_page=request.GET.get('page'),
            all_count=all_count,
            base_url=request.path_info,
            per_page=self.per_page_count,
            query_params=query_params,
        )

        ############################## 处理表的内容###############################
        list_display = self.get_list_display(request, *args, **kwargs)

        # 得到表头的各项名称
        list_title = []
        if list_display:
            for func_or_name in list_display:  # 判断要展示的是属性还是函数
                if isinstance(func_or_name, FunctionType):  # 如果是函数就直接执行
                    verbose_name = func_or_name(self, obj=None, is_head=True)
                else:
                    verbose_name = self.model_class._meta.get_field(func_or_name).verbose_name  # 得到所需字段的verbose_name
                list_title.append(verbose_name)
        else:  # 如果直接继承的是父类，List_display未定义则 表头直接取表名称
            list_title.append(self.model_class._meta.model_name)

        ############################################## 按照指定字段排序 并对数据做切片 控制每页显示的数据#############
        search_group_condition = self.get_search_group_condition(request)
        # **condition 根据字典搜索条件
        data_list_obj = query_set.filter(**search_group_condition).order_by(*self.get_order_list())[pager.start:pager.end]

        # 处理表中的数据
        data_list = []
        for obj in data_list_obj:
            tr_list = []  # 一行记录对应的数据
            if list_display:
                for func_or_name in list_display:
                    if isinstance(func_or_name, FunctionType):  # 判断是属性还是函数
                        data = func_or_name(self, obj, is_head=False, *args, **kwargs)  # 如果是函数就直接执行
                    else:
                        data = getattr(obj, str(func_or_name))  # 通过反射 查找对象的属性
                    tr_list.append(data)
            else:  # 如果list_display未定义 表数据直接取对象
                tr_list.append(obj)
            data_list.append(tr_list)

        # 获取添加按钮
        add_btn = self.get_add_btn(request, *args, **kwargs)

        #  组合搜索
        search_group_row_list = []
        for option_object in self.get_search_group():
            row = option_object.get_queryset_or_tuple(self.model_class, request, *args, **kwargs)
            search_group_row_list.append(row)

        return render(
            request,
            self.list_template or 'stark/list_view.html',
            {
                'data_list_obj': data_list_obj,
                'data_list': data_list,
                'list_title': list_title,
                'pager': pager,
                'add_btn': add_btn,
                'search_list': search_list,
                'search_value': search_value,
                'action_dict': action_dict,
                'search_group_row_list': search_group_row_list,
            }
        )

    def add_view(self, request, *args, **kwargs):
        """添加"""
        model_form_class = self.get_model_from(True, request, None, *args, **kwargs)
        if request.method == 'GET':
            form = model_form_class()
            return render(request, self.add_template or 'stark/change.html', {'form': form})

        form = model_form_class(data=request.POST)
        if form.is_valid():
            response = self.save(request, form, False, *args, **kwargs)
            return response or redirect(self.reverse_list_url(*args, **kwargs))
        return render(request, self.add_template or 'stark/change.html', {'form': form})

    def get_change_object(self, request, pk, *args, **kwargs):
        return self.model_class.objects.all().filter(pk=pk).first()

    def change_view(self, request, pk, *args, **kwargs):
        """编辑"""
        current_change_object = self.get_change_object(request, pk, *args, **kwargs)
        if not current_change_object:
            return HttpResponse('要修改的数据不存在，请重新选择！')

        model_form_class = self.get_model_from(False, request, pk, *args, **kwargs)
        if request.method == 'GET':
            form = model_form_class(instance=current_change_object)  # 传入对象获取各个属性的值
            return render(request, self.change_template or 'stark/change.html', {'form': form})

        form = model_form_class(data=request.POST, instance=current_change_object)  # 修改时也需要传入对象
        if form.is_valid():
            response = self.save(request, form, True, *args, **kwargs)
            return response or redirect(self.reverse_list_url(*args, **kwargs))
        return render(request, self.change_template or 'stark/change.html', {'form': form})

    def delete_object(self, request, pk, *args, **kwargs):
        self.model_class.objects.filter(pk=pk).delete()

    def del_view(self, request, pk, *args, **kwargs):
        """删除"""
        origin_url = self.reverse_list_url(*args, **kwargs)
        if request.method == 'GET':
            return render(request, self.delete_template or 'stark/delete.html', {'cancel': origin_url})
        response = self.delete_object(request, pk, *args, **kwargs)
        return response or redirect(origin_url)

    def save(self, request, form, is_update, *args, **kwargs):
        """
        在使用ModelForm保存数据前预留的钩子方法
        :param form:
        :param is_update:
        :return:
        """
        form.save()

    def get_url_name(self, params):
        """
        对url的别名进行拼接 使每个url有唯一的别名  别名可用于反向生成url
        :param params:
        :return:
        """
        app_name, model_name = self.model_class._meta.app_label, self.model_class._meta.model_name
        if self.prev:
            return '%s_%s_%s_%s' % (app_name, model_name, self.prev, params)  # 含前缀，则将前缀加入别名
        else:
            return '%s_%s_%s' % (app_name, model_name, params)

    @property
    def get_list_url_name(self):
        return self.get_url_name('list')

    @property
    def get_add_url_name(self):
        return self.get_url_name('add')

    @property
    def get_change_url_name(self):
        return self.get_url_name('change')

    @property
    def get_delete_url_name(self):
        return self.get_url_name('delete')

    def reverse_common_url(self, name, *args, **kwargs):
        """反向生成url"""
        name = '%s:%s' % (self.site.namespace, name)
        base_url = reverse(name, args=args, kwargs=kwargs)
        if not self.request.GET:
            add_url = base_url
        else:
            """如果请求后面携带参数 则保留该参数"""
            param = self.request.GET.urlencode()  # 对后面的参数中的特殊符号进行转义 将后面的所有参数打包成一个值
            new_query_dict = QueryDict(mutable=True)  # 表示可以修改
            new_query_dict['_filter'] = param
            add_url = '%s?%s' % (base_url, new_query_dict.urlencode())
        return add_url

    def reverse_add_url(self, *args, **kwargs):
        """反向解析url 并判断是否带有参数 如果后面带有参数则保留"""
        return self.reverse_common_url(self.get_add_url_name, *args, **kwargs)

    def reverse_list_url(self, *args, **kwargs):
        """反向生成跳转回list页面的url 有参数则保留参数"""
        return self.reverse_common_url(self.get_list_url_name, *args, **kwargs)

    def reverse_change_url(self, *args, **kwargs):
        """反向解析编辑页面Url 并判断是否带有参数 如果后面带有参数则保留"""
        return self.reverse_common_url(self.get_change_url_name, *args, **kwargs)

    def reverse_delete_url(self, *args, **kwargs):
        """反向解析删除页面Url 并判断是否带有参数 如果后面带有参数则保留"""
        return self.reverse_common_url(self.get_delete_url_name, *args, **kwargs)

    def wrapper(self, func):
        """通过闭包 扩展函数的功能"""

        @functools.wraps(func)  # 保留原函数的原信息
        def inner(request, *args, **kwargs):
            self.request = request  # 每个函数获取request对象
            return func(request, *args, **kwargs)
        return inner

    def get_urls(self):
        """
        固定生成四个url以及别名
        :return:
        """
        patterns = [
            url(r'^list/$', self.wrapper(self.list_view), name=self.get_list_url_name),
            url(r'^add/$', self.wrapper(self.add_view), name=self.get_add_url_name),
            url(r'^change/(?P<pk>\d+)/$', self.wrapper(self.change_view), name=self.get_change_url_name),
            url(r'^delete/(?P<pk>\d+)/$', self.wrapper(self.del_view), name=self.get_delete_url_name),
        ]
        patterns.extend(self.extra_urls())  # self是指当前对象 所以会先到当前对象的handler当中找
        return patterns

    def extra_urls(self):
        return []


class StarkSite(object):
    def __init__(self):
        self._registry = []
        self.app_name = 'stark'
        self.namespace = 'stark'

    def register(self, model_class, handler_class=None, prev=None):
        """
        对表的类和相应的处理视图函数的类进行注册
        :param model_class: models对应表所在的类
        :param handler_class: 处理对应视图函数的类
        :return:
        """
        if not handler_class:  # 默认为StarkHandler
            handler_class = StarkHandler
        self._registry.append(
            {'model_class': model_class, 'handler': handler_class(model_class, prev, self), 'prev': prev})

    def get_urls(self):
        """
        使每个表对应的类自动生成增删改查的url 并自动对应上相应的视图函数
        #  model_class._meta.app_label 返回类对应的app名
        #  model_class._meta.model_name 返回类对应的表名
        :return:
        """
        patterns = []
        for item in self._registry:
            model_class = item['model_class']
            handler = item['handler']
            prev = item['prev']
            app_name, model_name = model_class._meta.app_label, model_class._meta.model_name
            if prev:
                # patterns.append(url('%s/%s/%s/list/$' % (app_name, model_name, prev), handler.changelist_view))
                # patterns.append(url('%s/%s/%s/add/$' % (app_name, model_name, prev), handler.add_view))
                # patterns.append(url('%s/%s/%s/change/$' % (app_name, model_name, prev), handler.change_view))
                patterns.append(url('%s/%s/%s/' % (app_name, model_name, prev), (handler.get_urls(), None, None)))
                # 对app/mode_name/prev/ 再做一次路由分发
            else:
                # patterns.append(url('%s/%s/list/$' % (app_name, model_name), handler.changelist_view))
                # patterns.append(url('%s/%s/add/$' % (app_name, model_name), handler.add_view))
                # patterns.append(url('%s/%s/change/$' % (app_name, model_name), handler.change_view))
                patterns.append(url('%s/%s/' % (app_name, model_name), (handler.get_urls(), None, None)))

        return patterns

    @property
    def urls(self):
        """
        路由分发本质上就是返回一个元组([url], app_name, namespace)
        :return:
        """
        return self.get_urls(), self.app_name, self.namespace


site = StarkSite()
