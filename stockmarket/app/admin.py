from django.contrib import admin
from django.contrib.auth.models import User

from .models import UserStocks, UserInfo, Stocks

# Register your models here.

admin.site.register(UserStocks)
admin.site.register(Stocks)
admin.site.register(UserInfo)
