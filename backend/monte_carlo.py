import numpy as np

def monte_carlo_simulation(last_price, returns, days=30, sims=500):
    returns = returns.dropna()
    returns = returns[(returns > -0.2) & (returns < 0.2)]

    mu = returns.mean()
    sigma = returns.std()

    simulations = np.zeros((sims, days))

    for i in range(sims):
        price = last_price
        for d in range(days):
            shock = np.random.normal(mu, sigma)
            price *= (1 + shock)
            simulations[i, d] = price

    avg_path = simulations.mean(axis=0)
    lower_band = np.percentile(simulations, 10, axis=0)
    upper_band = np.percentile(simulations, 90, axis=0)

    return avg_path.tolist(), lower_band.tolist(), upper_band.tolist()
