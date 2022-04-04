from rbac import models
from django import forms

class RoleModelForm(forms.ModelForm):
    """
    该组件可以自动渲染出输入框并对页面中的字段进行校验
    """
    class Meta:
        model = models.Role  # 指定表
        fields = ['title',]  # 字段
        widgets = {
            'title': forms.TextInput(attrs={'class':'form-control'})  # 对渲染出的输入框添加属性
        }