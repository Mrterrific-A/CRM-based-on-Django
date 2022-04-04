from django.apps import AppConfig
from django.utils.module_loading import autodiscover_modules


class StarkConfig(AppConfig):
    name = 'stark'

    def ready(self):
        """
        通过此方法 在url加载前 在每一个已经注册的app中寻找stark文件并执行
        :return:
        """
        autodiscover_modules('stark')