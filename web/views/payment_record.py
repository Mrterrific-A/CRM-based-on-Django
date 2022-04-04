from stark.service.v1 import StarkHandler, StarkModelForm, get_choice_text
from django.shortcuts import HttpResponse
from web import models
from django import forms
from django.conf.urls import url
from .base import PermissionHandler


class StudentModelForm(StarkModelForm):
    qq = forms.CharField(label='qq',max_length=32)
    mobile = forms.CharField(label='手机号', max_length=32)
    emergency_contract = forms.CharField(label='紧急联系人', max_length=32)

    class Meta:
        model = models.PaymentRecord
        fields = ['pay_type', 'paid_fee', 'class_list', 'note']


class PaymentRecordModelForm(StarkModelForm):
    class Meta:
        model = models.PaymentRecord
        fields = ['pay_type', 'paid_fee', 'class_list', 'note']


class PaymentRecordHandler(PermissionHandler, StarkHandler):
    model_from_class = PaymentRecordModelForm
    list_display = [get_choice_text('费用类型', 'pay_type'), 'paid_fee', 'class_list', 'consultant',
                    'apply_date', get_choice_text('确认状态', 'confirm_status')]

    def get_urls(self):
        """
        固定生成四个url以及别名 自定义传入的参数 比如list需要传入顾问的id
        :return:
        """
        patterns = [
            url(r'^list/(?P<customer_id>\d+)/$', self.wrapper(self.list_view), name=self.get_list_url_name),
            url(r'^add/(?P<customer_id>\d+)/$', self.wrapper(self.add_view), name=self.get_add_url_name),
        ]
        patterns.extend(self.extra_urls())  # self是指当前对象 所以会先到当前对象的handler当中找
        return patterns

    def get_queryset(self, request, *args, **kwargs):
        """只展示私户的客户的跟进记录"""
        customer_id = kwargs.get('customer_id')
        current_user_id = request.session['user_info']['id']

        return self.model_class.objects.filter(customer_id=customer_id, customer__consultant_id=current_user_id)

    def get_list_display(self, request, *args, **kwargs):
        """
        获取页面上应该显示的列，预留自定义扩展，即可根据不同用户展示出不同的列
        """
        value = []
        if self.list_display:
            value.extend(self.list_display)  # 如果直接子类没有handler方法 则直接拿取子类的list_display
        return value

    def get_model_from(self, is_add, request, pk, *args, **kwargs):
        """根据学生是否存在设置指定的modelform"""
        customer_id = kwargs.get('customer_id')
        student_exist = models.Student.objects.filter(customer_id=customer_id).exists()
        if student_exist:
            return PaymentRecordModelForm
        return StudentModelForm

    def save(self, request, form, is_update, *args, **kwargs):
        """保存缴费的默认信息"""

        customer_id = kwargs.get('customer_id')
        current_user_id = request.session['user_info']['id']

        object_exists = models.Customer.objects.filter(id=customer_id,
                                                       consultant_id=current_user_id).exists()
        if not object_exists:
            return HttpResponse('非法操作')

        # 添加缴费记录
        form.instance.consultant_id = current_user_id
        form.instance.customer_id = customer_id
        form.save()

        # 添加学员记录
        fetch_student_object = models.Student.objects.filter(customer_id=customer_id).first()
        class_list = form.cleaned_data['class_list']
        # 如果学员原来不存在
        if not fetch_student_object:
            qq = form.cleaned_data['qq']
            mobile = form.cleaned_data['mobile']
            emergency_contract = form.cleaned_data['emergency_contract']
            student_object = models.Student.objects.create(customer_id=customer_id, qq=qq, mobile=mobile, emergency_contract=emergency_contract)

            # 添加学员要报名的班级
            student_object.class_list.add(class_list)
        else:
            fetch_student_object.class_list.add(class_list)

