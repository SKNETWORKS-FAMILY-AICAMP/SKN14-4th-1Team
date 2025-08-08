from django.urls import path
from . import views

app_name = 'app'

urlpatterns = [

    path('', views.home, name='home'),
    path('main', views.main, name='main'),
    path('chat', views.chat_recommand, name='chat_recommand'),
    path('serach', views.search, name='search'),
]