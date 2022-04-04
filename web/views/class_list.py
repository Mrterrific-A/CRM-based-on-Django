from web import models
from stark.service.v1 import StarkHandler, StarkModelForm, Option
from stark.service.v1 import get_datetime_text, get_m2m_text
from stark.forms.widgets.datetimepicker import DateTimePickerInput
from django.utils.safestring import mark_safe
from django.urls import reverse


class ClassListModelForm(StarkModelForm):
    class Meta:
        model = models.ClassList
        fields = '__all__'
        widgets = {
            'start_date': DateTimePickerInput,
            'graduate_date': DateTimePickerInput,
        }


class ClassListHandler(StarkHandler):

    def display_course_record(self, obj=None, is_head=None, *args, **kwargs):
        if is_head:
            return '上课记录'

        record_url = reverse('stark:web_courserecord_list', kwargs={'class_id': obj.pk})  # 使用reverse 不使用保留原参数的功能
        return mark_safe("<a target='_blank'  href='%s'>上课记录</a>" % record_url)  # target  点击时 再开一个网页

    def display_course(self, obj=None, is_head=None, *args, **kwargs):
        if is_head:
            return '班级'

        return "%s %s期" % (obj.course.title, obj.semester)
    list_display = ['school', display_course, 'price', get_datetime_text('开始日期', 'start_date'),
                    'class_teacher', get_m2m_text('任课老师', 'tech_teacher'), display_course_record]

    search_list = ['course__title__contains', ]
    search_group = [
        Option('school'),
        Option('course')
    ]

    model_from_class = ClassListModelForm
