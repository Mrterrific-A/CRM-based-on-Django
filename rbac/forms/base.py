from django import forms


class BootStrapModelForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(BootStrapModelForm, self).__init__(*args, **kwargs)  # 继承父类方法

        for name, field in self.fields.items():  # name为字符串 field为各个字段生成的对象
            field.widget.attrs['class'] = 'form-control'  # 为所有的对象添加属性