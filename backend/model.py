import xgboost as xgb
from sklearn.preprocessing import StandardScaler

def train_model(df):
    features = [
        "Return", "Volatility", "Momentum",
        "MA20", "MA50", "RSI", "MACD", "Volume_Change"
    ]

    X = df[features]
    y_return = df["Future_Return"]
    y_vol = df["Future_Volatility"]

    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)

    model_return = xgb.XGBRegressor(
        n_estimators=300,
        max_depth=4,
        learning_rate=0.05,
        subsample=0.8,
        colsample_bytree=0.8,
        random_state=42
    )

    model_vol = xgb.XGBRegressor(
        n_estimators=200,
        max_depth=3,
        learning_rate=0.05,
        subsample=0.8,
        colsample_bytree=0.8,
        random_state=42
    )

    model_return.fit(X_scaled, y_return)
    model_vol.fit(X_scaled, y_vol)

    latest_data = scaler.transform(X.iloc[-1:].values)

    predicted_return = model_return.predict(latest_data)[0]
    predicted_volatility = model_vol.predict(latest_data)[0]

    # Convert return prediction into probability (smooth logistic transform)
    probability_up = 1 / (1 + pow(2.71828, -predicted_return * 60))

    return predicted_return, predicted_volatility, probability_up
