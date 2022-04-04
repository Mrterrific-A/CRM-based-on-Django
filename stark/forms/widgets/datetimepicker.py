from django import forms


class DateTimePickerInput(forms.TextInput):
    """使日期出现可选框"""
    template_name = 'stark/forms/widgets/datetime_picker.html'