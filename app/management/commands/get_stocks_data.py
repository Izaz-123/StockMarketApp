import threading
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.core.mail import send_mail
from django.core.management import BaseCommand
from django.core.paginator import Paginator
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from ...models import *
import requests



def update_stocks() :
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
        url = f"https://api.tiingo.com/tiingo/daily/{ticker}?token={token}"
        priceurl = f"https://api.tiingo.com/tiingo/daily/{ticker}/prices?token={token}"

        try:
            requestResponse = requests.get(url, headers=headers)
            Metadata = requestResponse.json()

            priceResponse = requests.get(priceurl, headers=headers)
            priceJson = priceResponse.json()

            # Debug prints for development
            print(f"Metadata for {ticker}: {Metadata}")
            print(f"Price data for {ticker}: {priceJson}")

            if isinstance(priceJson, list) and len(priceJson) > 0 and 'close' in priceJson[0]:
                close_price = priceJson[0]['close']

                Stocks.objects.update_or_create(
                    ticker=Metadata.get('ticker', ticker),
                    defaults={
                        'name': Metadata.get('name', ''),
                        'description': Metadata.get('description', ''),
                        'curr_price': close_price
                    }
                )
            else:
                print(f"⚠️ Price data for {ticker} is empty or invalid: {priceJson}")

        except Exception as e:
            print(f"❌ Error processing ticker {ticker}: {e}")


    nasdaq_tickers =  nasdaq_tickers[:50]
    for i in nasdaq_tickers :
        getStock(i)





class Command(BaseCommand):
    help = 'Get stockmarkett data from Tiingo API'
    def handle(self, *args, **options):
        update_stocks()
        self.stdout.write("Stocks Data Downloaded")

