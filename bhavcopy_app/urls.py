from django.urls import path
from . import views

urlpatterns = {
    path('', views.display_bhavcopy, name="display_bhavcopy"),
}
