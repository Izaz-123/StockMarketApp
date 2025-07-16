from django.contrib.auth.models import User
from django.db import models

# Create your models here.

class Stocks(models.Model):
    ticker   =  models.CharField(max_length=10, unique=True)
    name =  models.CharField(max_length=300)
    description  =  models.CharField(max_length =5000)
    curr_price =  models.FloatField()

    def __str__(self):
        return  self.name


# ImageFiled in Models
#  pip  install pillow
#  media url in setting
#  static url  in urls.py


class UserInfo(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    email = models.CharField(max_length=100, unique=True)
    phone = models.CharField(max_length=100)
    profile_pic = models.ImageField(upload_to='profile_pic', null=True, blank=True)
    pancard_pic = models.ImageField(upload_to='pancard_pic', null=True, blank=True)


    def __str__(self):
        return self.user.username

class UserStocks(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    stock = models.ForeignKey(Stocks, on_delete=models.CASCADE)
    buy_price = models.FloatField()
    buy_quantity = models.IntegerField()

    def __str__(self):
        return self.stock.ticker

