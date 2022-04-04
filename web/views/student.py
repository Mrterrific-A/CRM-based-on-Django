from stark.service.v1 import StarkHandler, get_choice_text, StarkModelForm, get_m2m_text, Option
from django.conf.urls import url
from web import models
from django.utils.safestring import mark_safe
from django.urls import reverse
from .base import PermissionHandler


class StudentModelForm(StarkModelForm):
    class Meta:
        model = models.Student
        fields = ['qq', 'mobile', 'emergency_contract', 'memo']


class StudentHandler(PermissionHandler, StarkHandler):
    def display_score_record(self, obj=None, is_head=False, *args, **kwargs):
        """展示跟进记录"""
        if is_head:
            return '积分管理'

        record_url = reverse('stark:web_scorerecord_list', kwargs={'student_id': obj.pk})  # 使用reverse 不使用保留原参数的功能
        return mark_safe("<a target='_blank'  href='%s'>%s</a>" % (record_url, obj.score))  # target  点击时 再开一个网页

    model_from_class = StudentModelForm
    list_display = ['customer', 'mobile', 'emergency_contract', get_m2m_text('班级', 'class_list'), display_score_record,
                    get_choice_text('学员状态', 'student_status')]

    def get_add_btn(self, request, *args, **kwargs):
        """不能添加"""
        return None

    def get_list_display(self, request, *args, **kwargs):
        """
        获取页面上应该显示的列，预留自定义扩展，即可根据不同用户展示出不同的列
        :return:
        """
        value = []
        value.extend(self.list_display)  # 如果直接子类没有handler方法 则直接拿取子类的list_display
        value.append(type(self).display_edit)  # 默认每张表生成编辑删除功能
        return value

    def get_urls(self):
        """
        只能查看
        :return:
        """
        patterns = [
            url(r'^list/$', self.wrapper(self.list_view), name=self.get_list_url_name),
            url(r'^change/(?P<pk>\d+)/$', self.wrapper(self.change_view), name=self.get_change_url_name),
        ]
        patterns.extend(self.extra_urls())  # self是指当前对象 所以会先到当前对象的handler当中找
        return patterns

    search_list = ['customer__name', 'qq', 'mobile']

    search_group = {
        # Option('class_list', text_func=lambda x: '%s-%s' % (x.school.title, str(x)))
        Option('class_list')
    }