from web import models
from django.conf.urls import url
from stark.service.v1 import StarkHandler, get_choice_text, StarkModelForm, StarkForm, Option
from django.shortcuts import render, HttpResponse, redirect
from web.utils.md5 import gen_md5
from django.utils.safestring import mark_safe
from django import forms
from django.core.exceptions import ValidationError
from .base import PermissionHandler


class UserInfoAddModelForm(StarkModelForm):
    """自定义添加编辑页面显示字段的顺序"""
    confirm_password = forms.CharField(label='确认密码')
    class Meta:
        model = models.UserInfo
        fields = ['name', 'password', 'confirm_password', 'nickname', 'gender', 'email', 'phone', 'depart', 'roles']

    def clean_confirm_password(self):
        """校验密码与确认密码"""
        password = self.cleaned_data['password']
        confirm_password = self.cleaned_data['confirm_password']
        if password != confirm_password:
            raise ValidationError('密码输入不一致')
        return confirm_password

    def clean(self):
        """ 密码加密"""
        password = self.cleaned_data['password']
        self.cleaned_data['password'] = gen_md5(password)
        return self.cleaned_data


class UserInfoChangeModelForm(PermissionHandler, StarkModelForm):
    """自定义添加编辑页面显示字段的顺序"""
    class Meta:
        model = models.UserInfo
        fields = ['name', 'nickname', 'gender', 'email', 'phone', 'depart', 'roles']


class UserInfoResetPasswordForm(StarkForm):
    password = forms.CharField(label='密码', widget=forms.PasswordInput)
    confirm_password = forms.CharField(label='确认密码', widget=forms.PasswordInput)

    def clean_confirm_password(self):
        """校验密码与确认密码"""
        password = self.cleaned_data['password']
        confirm_password = self.cleaned_data['confirm_password']
        if password != confirm_password:
            raise ValidationError('密码输入不一致')
        return confirm_password

    def clean(self):
        """ 密码加密"""
        password = self.cleaned_data['password']
        self.cleaned_data['password'] = gen_md5(password)
        return self.cleaned_data


class UserInfoHandler(StarkHandler):

    def display_reset_pwd(self, obj=None, is_head=False, *args, **kwargs):
        """展示密码管理"""
        if is_head:
            return '密码管理'
        return mark_safe("<a href='%s'>重置密码</a>" % self.reverse_reset_pwd_url(pk=obj.pk))

    def reverse_reset_pwd_url(self, *args, **kwargs):
        """反向解析编辑页面Url"""
        return self.reverse_common_url(self.get_reset_pwd_url_name, *args, **kwargs)

    @property
    def get_reset_pwd_url_name(self):
        """获取别名"""
        return self.get_url_name('reset_pwd')

    def reset_password(self, request, pk):
        """重置密码"""
        user_object = models.UserInfo.objects.filter(pk=pk).first()
        if not user_object:
            return HttpResponse('用户不存在，无法重置密码')
        if request.method == 'GET':
            form = UserInfoResetPasswordForm()
            return render(request, 'stark/change.html', {'form': form})
        form = UserInfoResetPasswordForm(data=request.POST)
        if form.is_valid():  # 校验
            user_object.password = form.cleaned_data['password']
            user_object.save()
            return redirect(self.reverse_list_url())
        return render(request, 'stark/change.html', {'form': form})

    def extra_urls(self):
        """增加额外的Url"""
        patterns = [
            url(r'^reset_pwd/(?P<pk>\d+)/$', self.wrapper(self.reset_password), name=self.get_reset_pwd_url_name),
        ]
        return patterns

    list_display = ['nickname', get_choice_text('性别', 'gender'), 'phone',
                    'email', 'depart', StarkHandler.display_edit, display_reset_pwd
                    ]

    search_list = ['nickname__contains', 'name__contains']
    search_group = [
        Option(field='gender'),
        Option(field='depart')
    ]

    def get_model_from(self, request, pk, is_add=False, *args, **kwargs):
        """判断添加和编辑页面的modelform"""
        if is_add:
            return UserInfoAddModelForm
        return UserInfoChangeModelForm