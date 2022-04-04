from stark.service.v1 import StarkHandler, get_choice_text, get_datetime_text
from django.conf.urls import url


class CheckPaymentRecordHandler(StarkHandler):
    order_list = ['-id', 'confirm_status']
    list_display = [StarkHandler.display_checkbox,'customer', 'consultant', get_choice_text('费用类型', 'pay_type'), 'paid_fee', 'class_list',
                    get_datetime_text('申请时间', 'apply_date'), get_choice_text('确认状态', 'confirm_status')]

    def get_list_display(self, request, *args, **kwargs):
        """
        不能编辑修改
        :return:
        """
        value = []
        value.extend(self.list_display)  # 如果直接子类没有handler方法 则直接拿取子类的list_display
        return value

    def get_urls(self):
        """
        只能查看
        :return:
        """
        patterns = [
            url(r'^list/$', self.wrapper(self.list_view), name=self.get_list_url_name),
        ]
        patterns.extend(self.extra_urls())  # self是指当前对象 所以会先到当前对象的handler当中找
        return patterns

    def get_add_btn(self, request, *args, **kwargs):
        """不能添加"""
        return None

    def action_multi_confirm(self, request, *args, **kwargs):
        """批量确认"""
        pk_list = request.POST.getlist('pk')

        for pk in pk_list:
            payment_object = self.model_class.objects.filter(id=pk, confirm_status=1).first()
            if not payment_object:
                continue

            # 修改各个表的状态信息
            payment_object.confirm_status = 2
            payment_object.save()

            payment_object.customer.status = 1
            payment_object.customer.save()

            payment_object.customer.student.student_status = 2  # 通过OneToOne反向关联
            payment_object.customer.student.save()

    action_multi_confirm.text = '批量确认'

    def action_multi_cancel(self, request, *args, **kwargs):
        """批量驳回"""
        pk_list = request.POST.getlist('pk')
        self.model_class.objects.filter(id__in=pk_list, confirm_status=1).update(confirm_status=3)

    action_multi_cancel.text = '批量驳回'

    action_list = [action_multi_confirm, action_multi_cancel]
