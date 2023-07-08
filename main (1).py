import numpy as np
import pandas as pd


# Stochastic market simulation
def simulate_market(prices, noise_level, days):
    returns = np.diff(np.log(prices))
    mu, sigma = np.mean(returns), np.std(returns)
    simulated_returns = np.random.normal(mu, sigma, days - 1)
    simulated_returns = np.insert(simulated_returns, 0, 0)
    noise = np.random.normal(0, noise_level, days)
    simulated_prices = np.exp(np.cumsum(simulated_returns + noise)) * prices[0]
    return simulated_prices

# Resilience index calculation
def resilience_index(profitable_trades, max_drawdown, sharpe_ratio):
    return (profitable_trades - max_drawdown) * sharpe_ratio

# Trading Strategies

def moving_average_crossover(prices, short_window=5, long_window=30):
    short_ma = pd.Series(prices).rolling(window=short_window).mean()
    long_ma = pd.Series(prices).rolling(window=long_window).mean()

    signal = 0
    position = None
    buy_price = 0
    total_profit = 0

    for i in range(long_window, len(prices)):
        if short_ma[i] > long_ma[i] and signal != 1:
            signal = 1
            position = 'Long'
            buy_price = prices[i]
        elif short_ma[i] < long_ma[i] and signal != -1:
            signal = -1
            if position == 'Long':
                total_profit += prices[i] - buy_price
            position = None

    return total_profit

def mean_reversion(prices, window=5, threshold=1.5):
    mean = pd.Series(prices).rolling(window=window).mean()
    std = pd.Series(prices).rolling(window=window).std()

    position = None
    buy_price = 0
    total_profit = 0

    for i in range(window, len(prices)):
        if prices[i] < mean[i] - threshold * std[i]:
            if position is None:
                position = 'Long'
                buy_price = prices[i]
        elif prices[i] > mean[i] + threshold * std[i]:
            if position == 'Long':
                total_profit += prices[i] - buy_price
                position = None

    return total_profit

def momentum(prices, window=5):
    returns = pd.Series(prices).pct_change()
    momentum_signal = returns.rolling(window=window).mean()

    position = None
    buy_price = 0
    total_profit = 0

    for i in range(window, len(prices)):
        if momentum_signal[i] > 0 and position is None:
            position = 'Long'
            buy_price = prices[i]
        elif momentum_signal[i] < 0 and position == 'Long':
            total_profit += prices[i] - buy_price
            position = None

    return total_profit

# Replace the existing trading_strategy function with the following:

def trading_strategy(prices, strategy):
    if strategy == 'moving_average_crossover':
        return moving_average_crossover(prices)
    elif strategy == 'mean_reversion':
        return mean_reversion(prices)
    elif strategy == 'momentum':
        return momentum(prices)
    else:
        raise ValueError('Invalid trading strategy')

# Update the evaluate_trading_strategy function by adding a strategy parameter:

def evaluate_trading_strategy(strategy_name, prices, noise_levels, num_simulations):
    profitable_trades = []
    max_drawdowns = []
    sharpe_ratios = []

    for noise_level in noise_levels:
        profits = []
        for _ in range(num_simulations):
            simulated_prices = simulate_market(prices, noise_level, len(prices))
            profit = trading_strategy(simulated_prices, strategy_name)
            profits.append(profit)

        profitable_trades.append(np.mean(profits))
        max_drawdowns.append(np.max(prices) - np.min(prices))
        sharpe_ratios.append(np.mean(profits) / np.std(profits))

    return profitable_trades, max_drawdowns, sharpe_ratios


# Main function to run the simulation and evaluation
def main():
    # Load historical prices for the Bristol Stock Exchange system (replace this with actual data)
    prices = np.random.rand(100)
    noise_levels = [0.01, 0.05, 0.1, 0.2]

    num_simulations = 1000
    strategies = ['moving_average_crossover', 'mean_reversion', 'momentum']

    for strategy_name in strategies:
        print(f"Evaluating {strategy_name} strategy")
        profitable_trades, max_drawdowns, sharpe_ratios = evaluate_trading_strategy(strategy_name, prices, noise_levels,
                                                                                    num_simulations)

        resilience_indices = [resilience_index(pt, md, sr) for pt, md, sr in
                              zip(profitable_trades, max_drawdowns, sharpe_ratios)]

        results = pd.DataFrame({
            'Noise Level': noise_levels,
            'Profitable Trades': profitable_trades,
            'Max Drawdown': max_drawdowns,
            'Sharpe Ratio': sharpe_ratios,
            'Resilience Index': resilience_indices
        })

        print(results)


if __name__ == "__main__":
    main()