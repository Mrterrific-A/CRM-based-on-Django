from rbac import models
from django import forms
from django.core.exceptions import ValidationError

class UserModelForm(forms.ModelForm):
    """
    该组件可以自动渲染出输入框并对页面中的字段进行校验
    """
    confirm_password = forms.CharField(label='确认密码')  # 如果需要别的字段可以 自定义并在fields中添加

    class Meta:
        model = models.UserInfo  # 指定表
        fields = ['name', 'email', 'password', 'confirm_password']  # 字段

    def __init__(self, *args, **kwargs):
        super(UserModelForm,self).__init__(*args,**kwargs)  # 继承父类方法

        for name, field in self.fields.items():  # name为字符串 field为各个字段生成的对象
            field.widget.attrs['class'] = 'form-control'  # 为所有的对象添加属性

    def clean_confirm_password(self):  # 局部钩子  作密码校验
        try:
            password = self.cleaned_data['password']
        except KeyError:
            raise ValidationError('请输入密码')
        confirm_password = self.cleaned_data['confirm_password']
        if password != confirm_password:
            raise ValidationError('两次密码输入不一致')
        return confirm_password


class UpdateUserModelForm(forms.ModelForm):
    """
    该组件可以自动渲染出输入框并对页面中的字段进行校验
    """

    class Meta:
        model = models.UserInfo  # 指定表
        fields = ['name', 'email']  # 字段

    def __init__(self, *args, **kwargs):
        super(UpdateUserModelForm, self).__init__(*args, **kwargs)  # 继承父类方法

        for name, field in self.fields.items():  # name为字符串 field为各个字段生成的对象
            field.widget.attrs['class'] = 'form-control'  # 为所有的对象添加属性


class ResetpwdUserModelForm(forms.ModelForm):
    """
    该组件可以自动渲染出输入框并对页面中的字段进行校验
    """
    confirm_password = forms.CharField(label='确认密码')  # 如果需要别的字段可以 自定义并在fields中添加

    class Meta:
        model = models.UserInfo  # 指定表
        fields = ['password', 'confirm_password']  # 字段

    def __init__(self, *args, **kwargs):
        super(ResetpwdUserModelForm,self).__init__(*args,**kwargs)  # 继承父类方法

        for name, field in self.fields.items():  # name为字符串 field为各个字段生成的对象
            field.widget.attrs['class'] = 'form-control'  # 为所有的对象添加属性

    def clean_confirm_password(self):  # 局部钩子  作密码校验
        try:
            password = self.cleaned_data['password']
        except KeyError:
            raise ValidationError('请输入密码')
        confirm_password = self.cleaned_data['confirm_password']
        if password != confirm_password:
            raise ValidationError('两次密码输入不一致')
        return confirm_password
