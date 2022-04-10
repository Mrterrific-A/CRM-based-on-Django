关于stark组件的使用
当你想要快速对一张表进行增删改查以实现一些功能时，采取如下步骤：
1. 创建一个新的视图函数，创建一个Handler类，并继承StarkHandler
    from stark.service.v1 import StarkHandler
    
    class CourseHandler(StarkHandler):
        list_display = ['title']
        
2. 在stark.py中 
    from stark.service.v1 import site
    导入Handler对象 from web.views.course import CourseHandler
    site.register(表对象, CourseHandler)

3.关于display
    1. list_display = ['表的字段名称] 可自定制展示在主页面上的列
    如果表字段是多对多的关系，可用get_m2m_text(title, field, *args, **kwargs)
    如果表字段是一个选项，可用get_choice_text(title, field, *args, **kwargs)
    若表字段是时间，想要将其变为指定的格式，可用 get_datetime_text(title, field, format_type='%Y-%m-%d', *args, **kwargs)
    format_type 可指定格式

    2.此函数会在主页面展示时自动生成删除、编辑按钮  
        def get_list_display(self, request, *args, **kwargs):
            value = []
            if self.list_display:
                value.extend(self.list_display)  
                value.append(type(self).display_edit_del)  # 若不想要编辑删除，则删除此行
            return value
        如果只要编辑或删除，则将type(self).display_edit_del 替换为  type(self).display_del  type(self).display_edit
    
    3.若要在展示列中添加新的<a>来跳转
         def display_score_record(self, obj=None, is_head=False, *args, **kwargs):
            if is_head:
                return '标题'
            record_url = reverse('stark:别名', kwargs={需要传递的参数})  # 用于反向生成url
            return mark_safe("<a target='_blank'  href='%s'>%s</a>" % (record_url, obj.score))  
            
    最后在list_display中添加函数名
     
    4. StarkHandler.display_checkbox 放在list_display，可生成复选框
    
    5. 在展示时，需要对展示的数据进行查表，可自定值条件来查找指定数据
    ef get_queryset(self, request, *args, **kwargs):
        """只展示私户的客户的跟进记录"""
        customer_id = kwargs.get('customer_id')
        current_user_id = request.session['user_info']['id']

        # 顾客的顾问id等于当前用户的id  防止别的顾问来访问你的信息
        return self.model_class.objects.filter(customer_id=customer_id, 
                                                customer__consultant_id=current_user_id)
4. 对增加、删除页面的自定制，可自定制ModelForm并继承StarkModelForm
    from stark.service.v1 import StarkModelForm
    class ConsultRecordModelForm(StarkModelForm):
        class Meta:
            model = models.ConsultRecord
            fields = ['note']
            
    在自定值的Hanler中，需要指定 model_from_class = ConsultRecordModelForm
    
    当对编辑、添加页面进行自定制展示后，提交到数据库时需要保存那些没有展示的数据
    可重写
        def delete_object(self, request, pk, *args, **kwargs):
            self.model_class.objects.filter(pk=pk).delete()
            
        def get_change_object(self, request, pk, *args, **kwargs):
            return self.model_class.objects.all().filter(pk=pk).first()
    
 5. 关于url
 当对Handler注册完成后，会自动生成增删改查四个url,如果想要自定制
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
        patterns.extend(self.extra_urls())  
        return patterns
     
  若想要删除url则删除对应的行
  若想要增加url ，可通过extra_urls(self)来自定制
         def extra_urls(self):
            """增加额外的Url"""
            patterns = [
                url(r'^record/(?P<pk>\d+)/$', self.wrapper(self.record_view),
                    name=self.get_url_name('record_view')),  # get_url_name('name')可以生成对应的别名
            ]
            return patterns
   注：当url传入多个参数时，那么一些函数可能需要做出一些改变
     
6. 关于批量操作
   写一个批量操作的函数，将函数添加到action_list中， 函数名.text为批量操作的名称，默认已有multi_delete方法
        def multi_delete(self, request, *args, **kwargs):
        """
        批量删除 可以定制返回值 来跳转别的页面或者其他操作
        :return:
        """
        pk_list = request.POST.getlist('pk')
        self.model_class.objects.filter(id__in=pk_list).delete()

    multi_delete.text = '批量移除到共户'

    action_list = [multi_delete, ]
    
7.模糊搜索
search_list = [字段名,] 可通过字段的内容对记录进行精确查找搜索，search_list = [字段名__contains,] 可进行模糊查找

8.组合搜索
from stark.service.v1 import Option
search_group = {
        Option('class_list')  # Option('class_list', text_func=默认方法)  
    } 
可对指定字段生成组合搜索框， 可通过get_text_func来自定制显示的内容

9. 反向生成
反向生成有两种方法 StarkHandler的reverse_common_url，这种反向生成方法如果原来url携带有参数会保留参数
若不想保留，则用from django.urls import reverse