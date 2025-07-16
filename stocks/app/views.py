import threading
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.core.mail import send_mail
from django.core.paginator import Paginator
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .models import Stocks, UserInfo, UserStocks
import requests



# # Create your views here.
def getData(request) :
    nasdaq_tickers = [
        "AAPL",  # Apple Inc.
        "MSFT",  # Microsoft Corporation
        "GOOGL",  # Alphabet Inc. (Class A)
        "GOOG",  # Alphabet Inc. (Class C)
        "AMZN",  # Amazon.com Inc.
        "META",  # Meta Platforms Inc.
        "NVDA",  # NVIDIA Corporation
        "TSLA",  # Tesla Inc.
        "PEP",  # PepsiCo Inc.
        "INTC",  # Intel Corporation
        "CSCO",  # Cisco Systems Inc.
        "ADBE",  # Adobe Inc.
        "CMCSA",  # Comcast Corporation
        "AVGO",  # Broadcom Inc.
        "COST",  # Costco Wholesale Corporation
        "TMUS",  # T-Mobile US Inc.
        "TXN",  # Texas Instruments Inc.
        "AMGN",  # Amgen Inc.
        "QCOM",  # Qualcomm Incorporated
        "INTU",  # Intuit Inc.
        "PYPL",  # PayPal Holdings Inc.
        "BKNG",  # Booking Holdings Inc.
        "GILD",  # Gilead Sciences Inc.
        "SBUX",  # Starbucks Corporation
        "MU",  # Micron Technology Inc.
        "ADP",  # Automatic Data Processing Inc.
        "MDLZ",  # Mondelez International Inc.
        "ISRG",  # Intuitive Surgical Inc.
        "ADI",  # Analog Devices Inc.
        "MAR",  # Marriott International Inc.
        "LRCX",  # Lam Research Corporation
        "REGN",  # Regeneron Pharmaceuticals Inc.
        "ATVI",  # Activision Blizzard Inc.
        "ILMN",  # Illumina Inc.
        "WDAY",  # Workday Inc.
        "SNPS",  # Synopsys Inc.
        "ASML",  # ASML Holding N.V.
        "EBAY",  # eBay Inc.
        "ROST",  # Ross Stores Inc.
        "CTAS",  # Cintas Corporation
        "BIIB",  # Biogen Inc.
        "MELI",  # MercadoLibre Inc.
        "ORLY",  # O'Reilly Automotive Inc.
        "VRTX",  # Vertex Pharmaceuticals Inc.
        "DLTR",  # Dollar Tree Inc.
        "KHC",  # The Kraft Heinz Company
        "EXC",  # Exelon Corporation
        "FAST",  # Fastenal Company
        "JD",  # JD.com Inc.
        "CRWD"  # CrowdStrike Holdings Inc.
    ]

    headers = {
        'Content-Type': 'application/json'
    }
    token  =  "c49fcd942798abe37ee4b9b2d971058db6fe6bb2"
    def getStock(ticker):
        url  = f"https://api.tiingo.com/tiingo/daily/{ticker}?token={token}"
        priceurl  =  f"https://api.tiingo.com/tiingo/daily/{ticker}/prices?token={token}"
        requestResponse = requests.get(url, headers=headers )
        Metadata  = requestResponse.json()
        print(Metadata)
        priceData  = requests.get(priceurl , headers=headers)
        print(priceData.json())
        priceData =  priceData.json()[0]['close']

        # insert into SQL
        stock = Stocks(ticker  = Metadata['ticker']  , name  =  Metadata['name'] ,  description =  Metadata['description'] , curr_price  = priceData)
        stock.save()

    nasdaq_tickers =  nasdaq_tickers[:10]
    for i in nasdaq_tickers :
        getStock(i)


    return HttpResponse("Stock Data Downloaded")


@login_required
def stocks(request):
    user_stocks = UserStocks.objects.filter(user=request.user, buy_quantity__gt=0).select_related("stock")
    query = request.GET.get('q')

    if query:
        stocks_list = Stocks.objects.filter(name__icontains=query)
    else:
        stocks_list = Stocks.objects.all()

    paginator = Paginator(stocks_list, 10)  # 10 stocks per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'data': page_obj,
        'query': query,
        'user_stocks': user_stocks,
    }
    return render(request, 'market.html', context)



def loginView(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            return redirect("index")
        else:
            messages.error(request, "Invalid username or password")
    return render(request, 'login.html')

def logoutView(request):
    logout(request)
    return redirect("login")


def registerView(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        email = request.POST.get("email")
        phone = request.POST.get("phone")
        profile_pic = request.FILES.get("profile_pic")
        pancard_pic = request.FILES.get("pancard_pic")

        if User.objects.filter(username = username).exists():
            messages.error(request, "Username already exists")
            return redirect("register")
        user = User(username = username, email = email)
        user.set_password(password)
        user.save()
        user_info = UserInfo(
            user = user,
            email = email,
            phone = phone,
            pancard_pic = pancard_pic,
            profile_pic = profile_pic,
        )
        user_info.save()

        login(request, user)
        t1 = threading.Thread(
            target=send_email_async,
            kwargs={
                "subject": " Registration sucessfull",
                "message": f"Dear {user, username} welcome to our platfrom ",
                "from_email": None,
                "recipient_list": [user.email],
            }
        )
        t1.start()
        return redirect('index')
    return render(request, 'register.html')



@login_required
def profileView(request):
    return render(request, 'profile.html')

@login_required
def buyView(request,id):
    stock = get_object_or_404(Stocks, id=id)
    user = request.user
    buy_price = stock.curr_price
    buy_quantity = int(request.POST.get("quantity"))


    user_stocks = UserStocks.objects.filter(stock = stock, user = user).first()

    if user_stocks:
        total_quantity = buy_quantity + user_stocks.buy_quantity

        user_stocks.buy_price =( ((buy_price * user_stocks.buy_quantity) +  (user_stocks.buy_quantity * user_stocks.buy_price )) / total_quantity )
        user_stocks.buy_quantity = total_quantity
        user_stocks.save()
    else:
        user_stocks=UserStocks(user=user, stock=stock, buy_quantity=buy_quantity, buy_price=buy_price)
        user_stocks.save()
        send_mail(
            subject="Stock Purchase Confirmation",
            message=f"Hi {user.username},\n\nYou successfully bought {buy_quantity} shares of {stock.name} at ₹{buy_price} each.\n\nThank you for investing with us!",
            from_email="izazdemo@gmail.com",
            recipient_list=[user.email],
            fail_silently=False,
        )
    messages.success(request, f"You successfully bought {buy_quantity} of {stock.name}!")
    t1 = threading.Thread(
        target=send_email_async,
        kwargs={
            "subject": "Buy Option executed successfully",
            "message": f"Your purchase of stock {stock.name} was successful",
            "from_email": None,
            "recipient_list": [user.email],
        }
    )
    t1.start()
    return redirect('index')



def sellView(request,id):
    stock = get_object_or_404(Stocks, id=id)
    user = request.user
    sell_quantity = int(request.POST.get("quantity"))

    user_stocks = UserStocks.objects.filter(stock = stock, user = user).first()

    if user_stocks.buy_quantity < sell_quantity:
        messages.error(request, "Sorry, you do not have enough stocks to sell!")
        return redirect("market")
    user_stocks.buy_quantity -= sell_quantity
    user_stocks.save()
    t1 = threading.Thread(
        target=send_email_async,
        kwargs={
            "subject": "Sell Option executed successfully",
            "message": f"Your sale of stock {stock.name} was successful",
            "from_email": None,
            "recipient_list": [user.email],
        }
    )
    t1.start()

    return redirect('index')




@login_required
def indexView(request):
    user_stocks = UserStocks.objects.filter(user=request.user, buy_quantity__gt=0).select_related("stock")

    total_value = 0
    invested_amount = 0

    for i in user_stocks:
        stock_value = i.buy_quantity * i.stock.curr_price
        invested_value = i.buy_quantity * i.buy_price
        total_value += stock_value
        invested_amount += invested_value
        i.stock_value = stock_value  # You can display this in the card

    gains = ((total_value - invested_amount) / invested_amount) * 100 if invested_amount != 0 else 0

    context = {
        'user_stocks': user_stocks,
        'total_value': round(total_value, 2),
        'invested': round(invested_amount, 2),
        'gains': round(gains, 2),
    }

    return render(request, 'index.html', context)

def send_email_async(subject  ,  message  ,  from_email , recipient_list ) :
    send_mail(subject  =  subject ,  message =  message ,  from_email= from_email , recipient_list = recipient_list )



