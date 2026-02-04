import yfinance as yf
import pandas as pd

def compute_rsi(series, period=14):
    delta = series.diff()
    gain = (delta.where(delta > 0, 0)).rolling(period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(period).mean()
    rs = gain / loss
    return 100 - (100 / (1 + rs))

def get_stock_data(symbol, period="2y"):
    df = yf.download(symbol, period=period)

    df["Price"] = df["Close"]
    df["Return"] = df["Price"].pct_change()
    df["Volatility"] = df["Return"].rolling(5).std()
    df["Momentum"] = df["Price"].pct_change(5)

    # --- New Indicators ---
    df["MA20"] = df["Price"].rolling(20).mean()
    df["MA50"] = df["Price"].rolling(50).mean()
    df["RSI"] = compute_rsi(df["Price"])

    ema12 = df["Price"].ewm(span=12, adjust=False).mean()
    ema26 = df["Price"].ewm(span=26, adjust=False).mean()
    df["MACD"] = ema12 - ema26

    df["Volume_Change"] = df["Volume"].pct_change()

    # Targets
    df["Future_Return"] = df["Return"].shift(-1)
    df["Future_Volatility"] = df["Return"].rolling(10).std().shift(-1)

    df = df.dropna()
    return df
