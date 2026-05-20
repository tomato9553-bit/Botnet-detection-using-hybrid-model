from django.contrib import admin
from django.urls import path

import views

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", views.home, name="home"),
    path("register/", views.register, name="register"),
    path("login/", views.login_view, name="login"),
    path("logout/", views.logout_view, name="logout"),
    path("upload/", views.Upload_data, name="upload"),
    path("train/", views.HybridModel, name="train"),
    path("rnn/", views.RNNModel, name="rnn"),
    path("predict/", views.prediction, name="predict"),
]
