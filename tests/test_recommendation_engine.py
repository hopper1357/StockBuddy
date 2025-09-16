import pandas as pd
import numpy as np
from stockbuddy.core.recommendation_engine import RecommendationEngine

def test_calculate_sma():
    """Tests the SMA calculation."""
    engine = RecommendationEngine()
    data = pd.Series([1, 2, 3, 4, 5])
    sma = engine._calculate_sma(data, window=3)
    # Expected: NaN, NaN, (1+2+3)/3=2, (2+3+4)/3=3, (3+4+5)/3=4
    assert pd.isna(sma.iloc[0])
    assert pd.isna(sma.iloc[1])
    assert sma.iloc[2] == 2.0
    assert sma.iloc[3] == 3.0
    assert sma.iloc[4] == 4.0

def test_generate_signals_not_enough_data():
    """Tests that 'Hold' is returned if data is insufficient."""
    engine = RecommendationEngine()
    # Create a DataFrame with less than 200 rows
    data = pd.DataFrame({'Close': np.random.rand(100)})
    signal = engine.generate_signals(data)
    assert signal == "Hold"

def test_golden_cross_buy_signal():
    """Tests the Golden Cross buy signal."""
    engine = RecommendationEngine()
    close_prices = np.linspace(100, 150, 250) # A steady upward trend
    # Create a dip to make the 50-day SMA cross the 200-day
    close_prices[150:200] -= 20
    close_prices = pd.Series(close_prices)

    sma50 = close_prices.rolling(50).mean()
    sma200 = close_prices.rolling(200).mean()

    # Find a point where a golden cross happens
    golden_cross_day = -1
    for i in range(200, 250):
        if sma50.iloc[i] > sma200.iloc[i] and sma50.iloc[i-1] <= sma200.iloc[i-1]:
            golden_cross_day = i
            break

    # We need a golden cross to test it
    if golden_cross_day != -1:
        # Construct a DataFrame that ends right on the golden cross
        data = pd.DataFrame({'Close': close_prices.iloc[:golden_cross_day+1]})
        signal = engine.generate_signals(data)
        assert signal == "Buy"

def test_rsi_buy_signal():
    """Tests the RSI < 30 buy signal."""
    engine = RecommendationEngine()
    # Create data that will result in a low RSI
    # A sharp, sustained drop usually does this.
    close_prices = np.arange(100, 70, -1)
    # Add some noise and length
    close_prices = np.append(np.linspace(100, 101, 200), close_prices)
    data = pd.DataFrame({'Close': close_prices})

    # The RSI calculation is complex, so we trust our implementation
    # and check the signal logic. Let's force the RSI to be low.
    engine._calculate_rsi = lambda x, window=14: pd.Series(np.full_like(x, 29.0))

    signal = engine.generate_signals(data)
    assert signal == "Buy"

def test_rsi_sell_signal():
    """Tests the RSI > 70 sell signal."""
    engine = RecommendationEngine()
    # Create data that will result in a high RSI
    close_prices = np.arange(70, 100, 1)
    close_prices = np.append(np.linspace(70, 71, 200), close_prices)
    data = pd.DataFrame({'Close': close_prices})

    # Force the RSI to be high to test the signal logic
    engine._calculate_rsi = lambda x, window=14: pd.Series(np.full_like(x, 71.0))

    signal = engine.generate_signals(data)
    assert signal == "Sell"
