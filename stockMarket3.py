import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from alpha_vantage.timeseries import TimeSeries
from alpha_vantage.techindicators import TechIndicators

import pandas_datareader.data as web
import time
import datetime as dt
from datetime import timedelta as td
from datetime import datetime
from dateutil.relativedelta import relativedelta
from matplotlib.ticker import Formatter
import matplotlib.dates as mdates
import mplcursors

api_key = "ZZUC2INZGM6ELMZ6"
ts = TimeSeries(key=api_key, output_format="pandas")

ti = TechIndicators(key=api_key, output_format="pandas")

############# Let User Choose Stock and Timeframe  #############

# ticker_input = input("Ticker: ")
ticker_input = "BA"
timeframe = "5 days"
# timeframe = input("Timeframe (1 day/5 days/1 month/3 months/1 year/5 years/max)")


if timeframe == "1 day":
    slice_date = 16 * 60
    interval_input = "1min"
elif timeframe == "5 days":
    slice_date = 16 * 4 * 5
    interval_input = "15min"
elif timeframe == "1 month":
    slice_date = 16 * 30
    interval_input = "60min"
elif timeframe == "3 months":
    slice_date = 30 * 3
    interval_input = "1day"
elif timeframe == "1 year":
    slice_date = 52
    interval_input = "1week"
elif timeframe == "5 years":
    slice_date = 52 * 5
    interval_input = "1week"
elif timeframe == "max":
    ss = ts.get_weekly(symbol=ticker_input)
    slice_date = 2500
    interval_input = "1week"
else:
    print("Please select a valid timeframe")

############# Getting data for ticker and timeframe  #############
if "min" in interval_input:
    df, meta_data = ts.get_intraday(
        symbol=ticker_input, interval=interval_input, outputsize="full"
    )
    df["5. adjusted close"] = df["4. close"]
    df["6. volume"] = df["5. volume"]
elif "day" in interval_input:
    df, meta_data = ts.get_daily_adjusted(symbol=ticker_input)
elif "week" in interval_input:
    df, meta_data = ts.get_weekly_adjusted(symbol=ticker_input)
else:
    timeframe = input("Timeframe (1 day/5 days/1 month/3 months/1 year/5 years/max)")

df = df.iloc[::-1]
df["100ma"] = df["5. adjusted close"].rolling(window=10, min_periods=0).mean()
df["Date"] = df.index

############# formatting time to make it responsive to different timeframes  #############
class MyFormatter(Formatter):
    def __init__(self, dates, fmt="%m-%d %H:%M", fmt1="%Y-%m-%d"):
        self.dates = dates
        self.fmt = fmt
        self.fmt1 = fmt1

    def __call__(self, x, pos=0):
        "Return the label for time x at position pos"
        ind = int(np.round(x))
        if ind >= len(self.dates) or ind < 0:
            return ""
        if timeframe == "1 day" or timeframe =="5 days":
            return self.dates[ind].strftime(self.fmt)
        else:
            return self.dates[ind].strftime(self.fmt1)


############# Setting up Matplotlib canvas  #############
formatter = MyFormatter(df.index)
fig = plt.figure(figsize=(10, 8))
ax1 = plt.subplot2grid((7, 1), (0, 0), rowspan=5, colspan=1)
plt.title(f'{ticker_input} over {timeframe}')
ax2 = plt.subplot2grid((6, 1), (5, 0), rowspan=2, colspan=2, sharex = ax1)
ax1.xaxis.set_major_formatter(formatter)


############# Determining the range of data used  #############
i = len(df.index)
if timeframe == "1 day":
    xmax = len(df.index)
    xmin = len(df.index) - 16 * 60 - 30
    ax1.set_facecolor("xkcd:blue")
    ax1.patch.set_alpha(0.3)

elif timeframe == "5 days":
    xmax = i
    xmin = i - 16 * 4 * 5
    ax1.set_facecolor("xkcd:blue")
    ax1.patch.set_alpha(0.3)
elif timeframe == "1 month":
    xmax = i
    xmin = i - 16 * 5
elif timeframe == "3 months":
    xmax = i
    xmin = i - 30.42 * 3
elif timeframe == "1 year":
    xmax = i
    xmin = i - 52
elif timeframe == "5 years":
    xmax = len(df.index)
    xmin = len(df.index) - 52 * 5

#############  Determining Percentages for Color of Line  #############
print(df["5. adjusted close"])
perc_change = (
    round(
        (df["5. adjusted close"][int(xmax) - 1] - df["5. adjusted close"][int(xmin)])
        / df["5. adjusted close"][int(xmin)]
        * 1000
    )
) / 10

if perc_change > 0:
    lines = ax1.plot(np.arange(len(df)), df["5. adjusted close"], color="green")
elif perc_change < 0:
    lines = ax1.plot(np.arange(len(df)), df["5. adjusted close"], color="red")
else:
    lines = ax1.plot(np.arange(len(df)), df["5. adjusted close"])

ax1.plot(np.arange(len(df)), df["100ma"], linewidth=0.5)


plt.xticks(rotation=30)
ax2.bar(np.arange(len(df)), df["6. volume"])

print(xmax)
############# Lines for smaller time ranges  #############
xspan_min = []
xspan_max = []
if "day" in timeframe:
    for i in range(0, int(xmax)):
        if "16:00:00" in str(df.index[i]):
            xspan_min.append(i)
        elif "09:30:00" in str(df.index[i]):
            xspan_max.append(i)
        if "20:00:00" in str(df.index[i]):
            ax1.axvline(i, alpha=0.5)
print(xspan_min, xspan_max)

if "day" in timeframe:
    for i, j in zip(xspan_max, xspan_min):
        print(i, j)
        ax1.axvspan(i, j, ymin=0, ymax=1, color="white")


min_range = df["5. adjusted close"][int(xmax) - 1]
for i in range(int(xmin), int(xmax)):
    if df["5. adjusted close"][i] < min_range:
        min_range = df["5. adjusted close"][i]
max_range = min_range
for i in range(int(xmin), int(xmax)):
    if df["5. adjusted close"][i] > max_range:
        max_range = df["5. adjusted close"][i]

ax1.set_xlim(xmin, xmax)
ax1.set_ylim(min_range - min_range * 0.05, max_range + max_range * 0.05)
print(min_range, max_range)

min_range = 0
max_range = min_range
for i in range(int(xmin), int(xmax)):
    if df["6. volume"][i] > max_range:
        max_range = df["6. volume"][i]

ax2.set_ylim(0, max_range + max_range * 0.1)

mplcursors.cursor(lines, hover=True)


plt.show()
