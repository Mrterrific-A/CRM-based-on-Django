from stark.service.v1 import StarkHandler, get_choice_text, get_m2m_text, StarkModelForm
from web.models import Customer
from django.utils.safestring import mark_safe
from django.conf.urls import url
from django.shortcuts import render, HttpResponse
from django.db import transaction
from web import models
from .base import PermissionHandler


class PublicCustomerModelForm(StarkModelForm):
    """公户无顾问"""
    class Meta:
        model = Customer
        exclude = ['consultant']


class PublicCustomerHandler(PermissionHandler, StarkHandler):
    def display_record(self, obj=None, is_head=False, *args, **kwargs):
        """展示密码管理"""
        if is_head:
            return '跟进记录'

        record_url = self.reverse_common_url(self.get_url_name('record_view'), pk=obj.pk)
        return mark_safe("<a href='%s'>查看记录</a>" % record_url)

    list_display = [StarkHandler.display_checkbox, 'name', 'qq', get_m2m_text('咨询课程', 'course'), display_record, get_choice_text('状态', 'status')]

    def get_queryset(self, request, *args, **kwargs):
        return self.model_class.objects.filter(consultant__isnull=True)  # 无顾问时为公户

    def extra_urls(self):
        """增加额外的Url"""
        patterns = [
            url(r'^record/(?P<pk>\d+)/$', self.wrapper(self.record_view),
                name=self.get_url_name('record_view')),
        ]
        return patterns

    def record_view(self, request, pk):
        """查看跟进记录的视图"""
        record_list = models.ConsultRecord.objects.filter(id=pk)
        return render(request, 'record_view.html', {'record_list': record_list})

    def multi_apply(self, request, *args, **kwargs):
        """
        批量添加到私户
        :return:
        """
        current_user_id = request.session['user_info']['id']
        pk_list = request.POST.getlist('pk')

        # 申请到私户的客户不能超过一定数量
        private_customer_count = models.Customer.objects.filter(consultant_id=current_user_id, status=2).count()
        if private_customer_count > models.Customer.MAX_PRIVATE_CUSTOMER_COUNT:
            return HttpResponse('私户中已有%s个客户,你还可以在申请%s个' %
                                (private_customer_count,
                                                    models.Customer.MAX_PRIVATE_CUSTOMER_COUNT-private_customer_count))

        # 数据库中加锁，避免同时添加同一个客户
        flag = False
        with transaction.atomic():
            origin_queryset = models.Customer.objects.filter(pk__in=pk_list, status=2,
                                                             consultant__isnull=True).select_for_update()

            if len(origin_queryset) == len(pk_list):
                models.Customer.objects.filter(pk__in=pk_list, status=2, consultant__isnull=True).update(
                    consultant_id=current_user_id
                )
                flag = True

        if not flag:
            return HttpResponse('选中的客户已被他人申请，请重新申请')

        # return redirect('http://www.baidu.com')

    multi_apply.text = '申请到我的私户'

    action_list = [multi_apply, ]

    model_from_class = PublicCustomerModelForm


