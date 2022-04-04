from stark.service.v1 import StarkHandler, StarkModelForm
from django.shortcuts import HttpResponse
from django.conf.urls import url
from django.utils.safestring import mark_safe
from web import models


class ConsultRecordModelForm(StarkModelForm):
    class Meta:
        model = models.ConsultRecord
        fields = ['note']


class ConsultRecordHandler(StarkHandler):
    model_from_class = ConsultRecordModelForm
    list_display = ['note', 'consultant', 'date']

    list_template = 'consult_record.html'

    def display_edit_del(self, obj=None, is_head=None, *args, **kwargs):
        """删除编辑在一栏中"""
        if is_head:
            return '操作'

        customer_id = kwargs.get('customer_id')
        tql = "<a href='%s'>编辑</a> <a href='%s'>删除</a>" % (
            (self.reverse_change_url(pk=obj.pk, customer_id=customer_id),
             self.reverse_delete_url(pk=obj.pk, customer_id=customer_id))
        )
        return mark_safe(tql)

    def get_urls(self):
        """
        固定生成四个url以及别名 自定义传入的参数 比如list需要传入顾问的id
        :return:
        """
        patterns = [
            url(r'^list/(?P<customer_id>\d+)/$', self.wrapper(self.list_view), name=self.get_list_url_name),
            url(r'^add/(?P<customer_id>\d+)/$', self.wrapper(self.add_view), name=self.get_add_url_name),
            url(r'^change/(?P<customer_id>\d+)/(?P<pk>\d+)/$', self.wrapper(self.change_view),
                name=self.get_change_url_name),
            url(r'^delete/(?P<customer_id>\d+)/(?P<pk>\d+)/$', self.wrapper(self.del_view),
                name=self.get_delete_url_name),
        ]
        patterns.extend(self.extra_urls())  # self是指当前对象 所以会先到当前对象的handler当中找
        return patterns

    def get_queryset(self, request, *args, **kwargs):
        """只展示私户的客户的跟进记录"""
        customer_id = kwargs.get('customer_id')
        current_user_id = request.session['user_info']['id']

        # 顾客的顾问id等于当前用户的id  防止别的顾问来访问你的信息
        return self.model_class.objects.filter(customer_id=customer_id, customer__consultant_id=current_user_id)

    def save(self, request, form, is_update, *args, **kwargs):
        """对内容进行绑定客户以及跟进人"""
        customer_id = kwargs.get('customer_id')
        current_user_id = request.session['user_info']['id']

        # 防止对不属于自己的私户添加跟进记录
        object_exists = models.Customer.objects.filter(id=customer_id,
                                                       consultant_id=current_user_id).exists()
        if not object_exists:
            return HttpResponse('非法操作')

        if not is_update:
            form.instance.consultant_id = current_user_id
            form.instance.customer_id = customer_id
        form.save()

    def get_change_object(self, request, pk, *args, **kwargs):
        customer_id = kwargs['customer_id']
        current_user_id = request.session['user_info']['id']
        return self.model_class.objects.all().filter(pk=pk, customer_id=customer_id,
                                                     customer__consultant_id=current_user_id
                                                     ).first()

    def delete_object(self, request, pk, *args, **kwargs):
        customer_id = kwargs['customer_id']
        current_user_id = request.session['user_info']['id']
        record_queryset = models.ConsultRecord.objects.filter(pk=pk, customer_id=customer_id,
                                                              customer__consultant_id=current_user_id
                                                              )
        if not record_queryset.exists():
            return HttpResponse('要删除的记录不存在,请重新选择！')
        record_queryset.delete()
