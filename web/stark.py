from web import models
from stark.service.v1 import site

from web.views.school import SchoolHandler
from web.views.depart import DepartHandler
from web.views.userinfo import UserInfoHandler
from web.views.course import CourseHandler
from web.views.class_list import ClassListHandler
from web.views.public_customer import PublicCustomerHandler
from web.views.private_customer import PrivateCustomerHandler
from web.views.consult_record import ConsultRecordHandler
from web.views.payment_record import PaymentRecordHandler
from web.views.check_payment_record import CheckPaymentRecordHandler
from web.views.student import StudentHandler
from web.views.score_record import ScoreRecordHandler
from web.views.course_record import CourseRecordHandler

site.register(models.School, SchoolHandler)
site.register(models.Depart, DepartHandler)
site.register(models.UserInfo, UserInfoHandler)
site.register(models.Course, CourseHandler)
site.register(models.ClassList, ClassListHandler)
site.register(models.Customer, PublicCustomerHandler, 'pub')
site.register(models.Customer, PrivateCustomerHandler, 'priv')
site.register(models.ConsultRecord, ConsultRecordHandler)
site.register(models.PaymentRecord, PaymentRecordHandler)
site.register(models.PaymentRecord, CheckPaymentRecordHandler, 'check')
site.register(models.Student, StudentHandler)
site.register(models.ScoreRecord, ScoreRecordHandler)
site.register(models.CourseRecord, CourseRecordHandler)