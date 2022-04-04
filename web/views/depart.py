from stark.service.v1 import StarkHandler
from .base import PermissionHandler


class DepartHandler(PermissionHandler, StarkHandler):
    list_display = ['title']