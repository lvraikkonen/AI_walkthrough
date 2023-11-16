# filename: stock_plot.py

import yfinance as yf
import matplotlib.pyplot as plt
from PIL import Image
from datetime import datetime

# fetch data
nvda = yf.Ticker("NVDA")
tsla = yf.Ticker("TSLA")

# get historical market data
today = datetime.today().strftime('%Y-%m-%d')
start_of_year = f"{datetime.today().year}-01-01"
nvda_hist = nvda.history(start=start_of_year, end=today)
tsla_hist = tsla.history(start=start_of_year, end=today)

# data visualization
plt.figure(figsize=(14, 7))

plt.title('NVDA vs TSLA YTD Stock Price')
plt.plot(nvda_hist.index, nvda_hist["Close"], label='NVDA')
plt.plot(tsla_hist.index, tsla_hist["Close"], label='TSLA')

plt.xlabel('Date')
plt.ylabel('Closing Price ($)')
plt.legend()

plt.savefig('stock_prices.png')

# Display the saved image
img = Image.open('stock_prices.png')
img.show()