from stark.service.v1 import StarkHandler
from .base import PermissionHandler

class SchoolHandler(PermissionHandler, StarkHandler):
    list_display = ['title']