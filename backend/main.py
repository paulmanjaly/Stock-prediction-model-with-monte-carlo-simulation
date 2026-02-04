from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pathlib import Path
from data import get_stock_data
from model import train_model
from monte_carlo import monte_carlo_simulation
import requests

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------- PREDICTION ENDPOINT ----------
@app.get("/predict/{symbol}")
def predict_stock(symbol: str):
    df = get_stock_data(symbol)

    predicted_return, predicted_volatility, prob_up = train_model(df)
    last_price = df["Price"].iloc[-1]

    # Monte Carlo with confidence bands
    mc_avg, mc_lower, mc_upper = monte_carlo_simulation(last_price, df["Return"])

    # Historical last 30 prices for sparkline
    historical_prices = df["Price"].tail(30).tolist()

    # Estimated tomorrow price from ML model
    predicted_price_tomorrow = last_price * (1 + predicted_return)

    # Expected return from Monte Carlo average path
    expected_return_mc = (mc_avg[-1] - last_price) / last_price if last_price != 0 else 0

    return {
        "symbol": symbol,
        "last_price": float(last_price),
        "predicted_price_tomorrow": float(predicted_price_tomorrow),
        "predicted_return_pct": float(predicted_return * 100),
        "predicted_volatility_pct": float(predicted_volatility * 100),
        "probability_up_tomorrow": float(prob_up),
        "monte_carlo_avg_path": mc_avg,
        "mc_lower_band": mc_lower,
        "mc_upper_band": mc_upper,
        "historical_prices": historical_prices,
        "expected_return": float(expected_return_mc)
    }


# ---------- AUTOCOMPLETE SEARCH ENDPOINT ----------
@app.get("/search/{query}")
def search_stocks(query: str):
    url = f"https://query1.finance.yahoo.com/v1/finance/search?q={query}"
    headers = {"User-Agent": "Mozilla/5.0"}

    r = requests.get(url, headers=headers)
    data = r.json()

    results = []
    for q in data.get("quotes", [])[:6]:
        results.append({
            "symbol": q.get("symbol"),
            "name": q.get("shortname") or q.get("longname")
        })

    return results


# Mount frontend static files (must be after API routes)
frontend_path = Path(__file__).parent.parent / "frontend"
app.mount("/", StaticFiles(directory=frontend_path, html=True), name="frontend")
