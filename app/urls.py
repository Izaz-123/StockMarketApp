from django.urls import path
from .views import *

urlpatterns = [
    path('', indexView, name='index'),
    path('market/', stocks, name='market'),
    path('data/', getData, name='data')   ,
    path('login/', loginView, name='login'),
    path('logout/', logoutView, name='logout'),
    path('register/', registerView, name='register'),
    path('profile/', profileView, name='profile'),
    path('buy/<int:id>/', buyView, name='buy'),
    path('sell/<int:id>/', sellView, name='sell'),




]