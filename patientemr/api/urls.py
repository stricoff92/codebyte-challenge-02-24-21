from django.conf.urls import url, include
from django.urls import path

from api import views

urlpatterns = [
    path("policy-data/", views.policy_data, name="policy-data")
]
