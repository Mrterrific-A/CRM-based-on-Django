from stark.service.v1 import StarkHandler, StarkModelForm
from django.conf.urls import url
from web import models
from .base import PermissionHandler


class ScoreRecordModelForm(StarkModelForm):
    class Meta:
        model = models.ScoreRecord
        fields = ['content', 'score', ]


class ScoreRecordHandler(PermissionHandler, StarkHandler):
    model_from_class = ScoreRecordModelForm
    list_display = ['content', 'score', 'user']

    def get_list_display(self, request, *args, **kwargs):
        """
        获取页面上应该显示的列，预留自定义扩展，即可根据不同用户展示出不同的列
        :return:
        """
        value = []
        value.extend(self.list_display)  # 如果直接子类没有handler方法 则直接拿取子类的list_display
        return value

    def get_urls(self):
        """
        积分不能编辑修改
        :return:
        """
        patterns = [
            url(r'^list/(?P<student_id>\d+)/$', self.wrapper(self.list_view), name=self.get_list_url_name),
            url(r'^add/(?P<student_id>\d+)/$', self.wrapper(self.add_view), name=self.get_add_url_name),
        ]
        patterns.extend(self.extra_urls())  # self是指当前对象 所以会先到当前对象的handler当中找
        return patterns

    def get_queryset(self, request, *args, **kwargs):
        student_id = kwargs.get('student_id')
        return self.model_class.objects.filter(student_id=student_id)  # 无顾问时为公户

    def save(self, request, form, is_update, *args, **kwargs):
        student_id = kwargs.get('student_id')
        current_user_id = request.session['user_info']['id']
        form.instance.student_id = student_id
        form.instance.user_id = current_user_id
        form.save()

        score = form.instance.score
        if score >= 0:
            form.instance.student.score += abs(score)
        else:
            form.instance.student.score -= abs(score)
        form.instance.student.save()
