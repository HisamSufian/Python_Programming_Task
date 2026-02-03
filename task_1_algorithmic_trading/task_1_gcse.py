# -*- coding: utf-8 -*-
"""TASK_1 GcSe.ipynb

Implements a moving-average crossover trading strategy
using historical stock data from Yahoo Finance.

Original file is located at
    https://colab.research.google.com/drive/1B8oM_B2WRsr_UacVEUPOHoqiwVyE4X-Q
"""

# !python --version
# !pip show pandas
# !pip show yfinance
# !pip show matplotlib

# Install yfinance (needed to fetch market data from Yahoo Finance).
# Run once per Colab session. The --quiet flag hides verbose install logs.
!pip install yfinance --quiet

# Core imports:
# - yfinance: to download historical price data
# - pandas: for data manipulation
# - matplotlib: for plotting charts
import yfinance as yf
import pandas as pd
import matplotlib.pyplot as plt

# Optional: make pandas output easier to read in Colab cells
pd.set_option('display.max_columns', None)   # show all columns
pd.set_option('display.width', 120)          # prevent line-wrapping in wide tables

print("Setup complete.")

class TradingStrategy:
    """
    A simple, modular backtesting engine that:
    - downloads price data
    - cleans/fills it
    - adds moving averages (MA50/MA200)
    - generates crossover signals
    - executes trades using a buy/sell simulation
    - evaluates final results
    """

    def __init__(self, symbol, start_date, end_date, budget=5000):
        # User inputs
        self.symbol = symbol
        self.start_date = start_date
        self.end_date = end_date
        self.budget = budget

        # Internal state
        self.data = None            # will hold the price DataFrame
        self.cash = budget          # available cash to buy shares
        self.position = 0           # current number of shares held
        self.trades = []            # list of trade dictionaries

    def get_data(self):
        """Download OHLCV data using yfinance."""
        self.data = yf.download(self.symbol, start=self.start_date, end=self.end_date, auto_adjust=False)
        return self.data

    def clean_data(self):
        """Remove duplicate dates and forward-fill missing values."""
        if self.data is not None:
            self.data = self.data[~self.data.index.duplicated(keep='first')]
            self.data = self.data.ffill()
        return self.data

    def add_indicators(self):
        """Add 50-day and 200-day moving averages."""
        if self.data is not None:
            self.data['MA50'] = self.data['Close'].rolling(window=50).mean()
            self.data['MA200'] = self.data['Close'].rolling(window=200).mean()
        return self.data

    def generate_signals(self):
        """
        Generate trading signals from MA crossover:
        - Signal = 1 when MA50 > MA200 (bullish), else 0
        - Position = diff of Signal; +1 = buy trigger, -1 = sell trigger
        """
        if self.data is not None:
            self.data['Signal'] = (self.data['MA50'] > self.data['MA200']).astype(int)
            self.data['Position'] = self.data['Signal'].diff()
        return self.data

    def execute_trades(self):
        """
        Simulate buying and selling based on MA crossover signals.
        Ensures values are scalars (not Series) to avoid FutureWarning/ValueError.
        """
        if self.data is None:
          return self.trades

        last_buy_price = None

        for date, row in self.data.iterrows():
        # --- Ensure scalar values ---
          price_val = row["Close"]
          if hasattr(price_val, "item"):
            price_val = price_val.item()
          elif hasattr(price_val, "iloc"):
            price_val = price_val.iloc[0]
          price = float(price_val)

          pos_val = row["Position"]
          if hasattr(pos_val, "item"):
            pos_val = pos_val.item()
          elif hasattr(pos_val, "iloc"):
            pos_val = pos_val.iloc[0]

          # Skip if signal is missing
          if pd.isna(pos_val): continue

          position_signal = int(pos_val)

          # --- BUY ---
          if position_signal == 1 and self.position == 0:
              shares_to_buy = int(self.cash // price)
              if shares_to_buy > 0:
                  self.position = shares_to_buy
                  self.cash -= shares_to_buy * price
                  last_buy_price = price
                  self.trades.append({
                      "Date": date,
                      "Action": "BUY",
                      "Shares": shares_to_buy,
                      "Price": price,
                      "Remaining_Budget": round(self.cash, 2)
                  })

          # --- SELL ---
          elif position_signal == -1 and self.position > 0:
              proceeds = self.position * price
              profit_loss = proceeds - (self.position * last_buy_price)
              self.cash += proceeds
              self.trades.append({
                "Date": date,
                "Action": "SELL",
                "Shares": self.position,
                "Price": price,
                "Profit_Loss": round(profit_loss, 2),
                "Remaining_Budget": round(self.cash, 2)
            })
              self.position = 0
              last_buy_price = None

        # --- Forced SELL at the end ---
        if self.position > 0:
            last_price_val = self.data["Close"].iloc[-1]
            if hasattr(last_price_val, "item"):
                last_price_val = last_price_val.item()
            last_price = float(last_price_val)

            proceeds = self.position * last_price
            profit_loss = proceeds - (self.position * last_buy_price)
            self.cash += proceeds
            self.trades.append({
                "Date": self.data.index[-1],
                "Action": "FORCED SELL",
                "Shares": self.position,
                "Price": last_price,
                "Profit_Loss": round(profit_loss, 2),
                "Remaining_Budget": round(self.cash, 2)
            })
            self.position = 0

        return self.trades


    def evaluate(self):
        """Summarize end-of-run results."""
        profit_loss = self.cash - self.budget
        return {
            "Initial Budget": round(self.budget, 2),
            "Final Portfolio Value": round(self.cash, 2),
            "Total Profit/Loss": round(profit_loss, 2),
            "Number of Trades": len(self.trades),
            "Trade History": self.trades
        }

    def run(self):
        """Full pipeline: fetch data, clean, add indicators, generate signals, trade, evaluate."""
        self.get_data()
        self.clean_data()
        self.add_indicators()
        self.generate_signals()
        self.execute_trades()
        return self.evaluate()

def print_trade_report_with_details(results):
    """
    Print a human-friendly summary of the run:
    - Per-trade Profit/Loss (only on SELL/FORCED SELL)
    - Cumulative P/L: running total across closed trades
    - P/L PerTd: average profit per closed trade (cumulative / count)
    """
    print("Trading strategy execution finished.\n")
    print("--- Trading Results ---")
    print(f"✅Initial Budget: ${results['Initial Budget']:.2f}")
    print(f"✅Final Portfolio Value: ${results['Final Portfolio Value']:.2f}")
    print(f"💰Total Profit/Loss: ${results['Total Profit/Loss']:.2f}")
    print(f"📈Number of Trades: {results['Number of Trades']}")
    print(f"📈Average Profit/Loss per Trade: ${results['Total Profit/Loss'] / results['Number of Trades']:.2f}")

    # Calculate and print Profit Percentage
    initial_budget = results['Initial Budget']
    total_profit_loss = results['Total Profit/Loss']
    profit_percentage = (total_profit_loss / initial_budget) * 100 if initial_budget > 0 else 0
    print(f"Profit Percentage: {profit_percentage:.2f}%")
    print("---------------------\n")

    print("Detailed Trade History:")
    cumulative_pl = 0      # running sum of Profit_Loss over closed trades
    closed_trades = 0      # counter for SELL / FORCED SELL
    for trade in results["Trade History"]:
        date = trade["Date"].strftime("%Y-%m-%d")
        action = trade["Action"]
        shares = trade["Shares"]
        price = trade["Price"]
        budget = trade["Remaining_Budget"]

        if action == "BUY":
            # BUY doesn’t have Profit_Loss because the position is opened, not closed
            print(f"{date} → BUY {shares} shares @ ${price:.2f}, \n💰Remaining budget: ${budget:.2f}")
        else:
            # For SELL and FORCED SELL, compute metrics
            pl = trade.get("Profit_Loss", 0)
            cumulative_pl += pl
            closed_trades += 1
            avg_pl = cumulative_pl / closed_trades if closed_trades > 0 else 0
            emoji = "🟢" if pl >= 0 else "🔴"

            print(f"{date} → {action} {shares} shares @ ${price:.2f}, "
                  f"{emoji} Profit/Loss: {pl:.2f}, "          # trade-specific P/L
                  f"P/L PerTd: {avg_pl:.2f}, "                 # average P/L so far
                  f"Cumulative P/L: {cumulative_pl:.2f}, "     # running total
                  f"\n💰Remaining budget: ${budget:.2f}")

def plot_trades(strategy):
    """
    Plot:
    - Close price series
    - MA50 and MA200 lines
    - Buy markers (green upward triangles)
    - Sell/Forced Sell markers (red downward triangles)
    """
    data = strategy.data
    trades = strategy.trades

    plt.figure(figsize=(12,6))
    plt.plot(data.index, data['Close'], label="Close Price", color="blue", alpha=0.6)
    plt.plot(data.index, data['MA50'], label="50-day MA", color="orange")
    plt.plot(data.index, data['MA200'], label="200-day MA", color="green")

    # Add trade markers
    for trade in trades:
        if trade["Action"] == "BUY":
            plt.scatter(trade["Date"], trade["Price"], marker="^", color="green", s=100, label="Buy")
        elif trade["Action"] in ["SELL", "FORCED SELL"]:
            plt.scatter(trade["Date"], trade["Price"], marker="v", color="red", s=100, label="Sell")

    # Avoid duplicate legend entries by collapsing labels
    handles, labels = plt.gca().get_legend_handles_labels()
    by_label = dict(zip(labels, handles))
    plt.legend(by_label.values(), by_label.keys())

    plt.title(f"{strategy.symbol} Trading Strategy")
    plt.xlabel("Date")
    plt.ylabel("Price ($)")
    plt.grid(True)
    plt.show()

def plot_equity_curve(results):
    """
    Build and plot the equity curve:
    - Only SELL and FORCED SELL trades contribute Profit_Loss
    - cumulative list is the running sum over time
    """
    # Filter trades that have Profit_Loss (i.e., closed trades)
    trades = [t for t in results["Trade History"] if "Profit_Loss" in t]

    cumulative = []
    total = 0
    dates = []
    for t in trades:
        total += t["Profit_Loss"]   # add current trade P/L to running total
        cumulative.append(total)    # store cumulative value
        dates.append(t["Date"])     # track the trade date

    # Plot the cumulative P/L over time
    plt.figure(figsize=(10,5))
    plt.plot(dates, cumulative, marker="o", linestyle="-", color="purple", label="Cumulative P/L")
    plt.axhline(0, color="black", linewidth=1, linestyle="--")  # breakeven line
    plt.title("Equity Curve (Cumulative Profit Over Time)")
    plt.xlabel("Trade Date")
    plt.ylabel("Cumulative Profit ($)")
    plt.grid(True)
    plt.legend()
    plt.show()

# Choose your inputs:
# - symbol: any ticker of yFinance (e.g., "AAPL", "MSFT","GOOGL", "^GSPC") / symbol = input("Enter symbol").upper().strip() or "AAPL"
# - date range: start/end strings in "YYYY-MM-DD" / date = input("Enter start date (YYYY-MM-DD): ").strip() or "2018-01-01"
# - budget: starting cash for the simulation

strategy = TradingStrategy("GOOGL", "2018-01-01", "2023-12-31", budget=5000)

# Run the full pipeline and capture evaluation summary + trade history
results = strategy.run()

# Print the detailed trade report
print_trade_report_with_details(results)

# Plot the price chart with buy/sell markers
plot_trades(strategy)

# Plot the equity curve (cumulative profit over time)
plot_equity_curve(results)
