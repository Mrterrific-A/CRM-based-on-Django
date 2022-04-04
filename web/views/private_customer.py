from stark.service.v1 import StarkHandler, get_choice_text, get_m2m_text, StarkModelForm
from django.utils.safestring import mark_safe
from django.urls import reverse
from web import models
from .base import PermissionHandler


class PrivateCustomerModelForm(StarkModelForm):
    class Meta:
        model = models.Customer
        exclude = ['consultant']


class PrivateCustomerHandler(PermissionHandler, StarkHandler):

    def display_record(self, obj=None, is_head=False, *args, **kwargs):
        """展示跟进记录"""
        if is_head:
            return '跟进记录'

        record_url = reverse('stark:web_consultrecord_list', kwargs={'customer_id': obj.pk})  # 使用reverse 不使用保留原参数的功能
        return mark_safe("<a target='_blank'  href='%s'>查看记录</a>" % record_url)  # target  点击时 再开一个网页

    def display_payment_record(self, obj=None, is_head=False, *args, **kwargs):
        """展示缴费记录"""
        if is_head:
            return '缴费记录'

        record_url = reverse('stark:web_paymentrecord_list', kwargs={'customer_id': obj.pk})  # 使用reverse 不使用保留原参数的功能
        return mark_safe("<a target='_blank'  href='%s'>缴费记录</a>" % record_url)  # target  点击时 再开一个网页

    model_from_class = PrivateCustomerModelForm
    list_display = [StarkHandler.display_checkbox, 'name', 'qq', get_m2m_text('咨询课程', 'course'), display_record,
                    display_payment_record, display_payment_record, get_choice_text('状态', 'status')]

    def get_queryset(self, request, *args, **kwargs):
        """只展示私户的客户"""
        current_user_id = request.session['user_info']['id']
        return self.model_class.objects.filter(consultant_id=current_user_id)  # 无顾问时为公户

    def save(self, request, form, is_update, *args, **kwargs):
        """私户添加时不用选择自己"""
        current_user_id = request.session['user_info']['id']
        form.instance.consultant_id = current_user_id
        form.save()

    def multi_delete(self, request, *args, **kwargs):
        """
        批量移除到共户
        :return:
        """
        current_user_id = request.session['user_info']['id']
        pk_list = request.POST.getlist('pk')
        self.model_class.objects.filter(id__in=pk_list, consultant_id=current_user_id).update(consultant_id=None)

    multi_delete.text = '批量移除到共户'

    action_list = [multi_delete, ]
