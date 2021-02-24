
from decimal import Decimal

from django.test import TestCase
from django.test import Client as TestClient
from django.contrib.auth.models import User

""" If child class has its own setUp/tearDown methods,
    the child class MUST call `super().setUp()` and `super().tearDown()`
"""

class BaseTestBase(TestCase):

    PASSWORD_FACTORY = "password-yo"
    ADMIN_USER_NAME = "foobar-admin"
    USER_NAME = "foobar"
    OTHER_USER_NAME = "foobar2"


    def round_float(self, value:float) -> Decimal:
        return Decimal(value).quantize(Decimal("0.0000"))


    def setUp(self):
        self.client = TestClient()

        self.user = User.objects.create_user(
            username=self.USER_NAME,
            email=f'{self.USER_NAME}@mail.com',
            password=self.PASSWORD_FACTORY)

        self.other_user = User.objects.create_user(
            username=self.OTHER_USER_NAME,
            email=f'{self.OTHER_USER_NAME}@mail.com',
            password=self.PASSWORD_FACTORY)


    def tearDown(self):
        self.client.logout()

