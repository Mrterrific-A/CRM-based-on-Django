from stark.service.v1 import StarkHandler, StarkModelForm, get_datetime_text
from django.conf.urls import url
from django.shortcuts import HttpResponse, render
from django.utils.safestring import mark_safe
from django.forms.models import modelformset_factory
from django.urls import reverse
from web import models
from .base import PermissionHandler


class CourseRecordModelForm(StarkModelForm):
    class Meta:
        model = models.CourseRecord
        fields = ['day_num', 'teacher']


class StudyRecordModelForm(StarkModelForm):
    class Meta:
        model = models.StudyRecord
        fields = ['record', ]


class CourseRecordHandler(PermissionHandler, StarkHandler):
    """上课记录管理"""

    def display_attendance(self, obj=None, is_head=None, *args, **kwargs):
        """反向生成"""
        if is_head:
            return '考勤管理'

        name = '%s:%s' % (self.site.namespace, self.get_url_name('attendance'))
        attendance_url = reverse(name, kwargs={'course_record_id': obj.pk})
        tql = "<a target='_blank' href='%s'>考勤</a>" % attendance_url
        return mark_safe(tql)

    model_from_class = CourseRecordModelForm
    list_display = [StarkHandler.display_checkbox, 'class_object', 'day_num', 'teacher',
                    get_datetime_text('时间', 'date'), display_attendance]

    def display_edit_del(self, obj=None, is_head=None, *args, **kwargs):
        """删除编辑在一栏中"""
        if is_head:
            return '操作'

        class_id = kwargs.get('class_id')
        tql = "<a href='%s'>编辑</a> <a href='%s'>删除</a>" % (
            (self.reverse_change_url(pk=obj.pk, class_id=class_id),
             self.reverse_delete_url(pk=obj.pk, class_id=class_id))
        )
        return mark_safe(tql)

    def get_urls(self):
        """
        固定生成四个url以及别名 自定义传入的参数 比如list需要传入顾问的id
        :return:
        """
        patterns = [
            url(r'^list/(?P<class_id>\d+)/$', self.wrapper(self.list_view), name=self.get_list_url_name),
            url(r'^add/(?P<class_id>\d+)/$', self.wrapper(self.add_view), name=self.get_add_url_name),
            url(r'^change/(?P<class_id>\d+)/(?P<pk>\d+)/$', self.wrapper(self.change_view),
                name=self.get_change_url_name),
            url(r'^delete/(?P<class_id>\d+)/(?P<pk>\d+)/$', self.wrapper(self.del_view),
                name=self.get_delete_url_name),
            url(r'^attendance/(?P<course_record_id>\d+)$', self.wrapper(self.attendance_view),
                name=self.get_url_name('attendance'))
        ]
        patterns.extend(self.extra_urls())  # self是指当前对象 所以会先到当前对象的handler当中找
        return patterns

    def get_queryset(self, request, *args, **kwargs):
        class_id = kwargs.get('class_id')
        return self.model_class.objects.filter(class_object_id=class_id)

    def save(self, request, form, is_update, *args, **kwargs):
        class_id = kwargs.get('class_id')

        if not is_update:
            form.instance.class_object_id = class_id
        form.save()

    def action_multi_init(self, request, *args, **kwargs):
        """批量初始化考勤"""
        course_record_id_list = request.POST.getlist('pk')
        class_id = kwargs.get('class_id')
        # 判断班级是否存在
        class_object = models.ClassList.objects.filter(id=class_id).first()
        if not class_object:
            return HttpResponse('班级不存在')

        student_object_list = class_object.student_set.all()
        print(student_object_list)

        for course_record_id in course_record_id_list:
            # 判断上课记录是非合法
            course_record_object = self.model_class.objects.filter(id=class_id).first()
            if not course_record_object:
                continue

            # 判断考勤记录是否存在
            study_record_exists = models.StudyRecord.objects.filter(course_record=course_record_object).exists()
            if study_record_exists:
                continue

            # 为每个学生创建考勤记录
            study_record_object_list = [models.StudyRecord(student_id=student.id, course_record_id=course_record_id)
                                        for student in student_object_list]
            # 一次批量生成多个表项
            models.StudyRecord.objects.bulk_create(study_record_object_list, batch_size=50)

    action_multi_init.text = '批量初始化考勤'

    action_list = [action_multi_init]

    def attendance_view(self, request, course_record_id, *args, **kwargs):
        """
        批量考勤管理
        :param request:
        :param course_record_id:
        :param args:
        :param kwargs:
        :return:
        """

        # modelformset 生成多个表单
        study_record_object_list = models.StudyRecord.objects.filter(course_record_id=course_record_id)
        study_model_formset = modelformset_factory(models.StudyRecord, form=StudyRecordModelForm, extra=0)

        if request.method == 'POST':
            formset = study_model_formset(queryset=study_record_object_list, data=request.POST)
            if formset.is_valid():
                formset.save()
                return render(request, 'attendance.html', {'formset': formset})

        formset = study_model_formset(queryset=study_record_object_list)

        return render(request, 'attendance.html', {'formset': formset})
