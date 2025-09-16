import pandas as pd

class RecommendationEngine:
    def _calculate_sma(self, data, window):
        """Calculates the Simple Moving Average."""
        return data.rolling(window=window).mean()

    def _calculate_rsi(self, data, window=14):
        """Calculates the Relative Strength Index."""
        delta = data.diff()
        gain = (delta.where(delta > 0, 0)).ewm(alpha=1/window, adjust=False).mean()
        loss = (-delta.where(delta < 0, 0)).ewm(alpha=1/window, adjust=False).mean()

        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        return rsi

    def generate_signals(self, historical_data):
        """
        Generates buy/sell/hold signals based on historical data.
        'historical_data' is a pandas DataFrame from yfinance.
        """
        if historical_data is None or len(historical_data) < 200:
            # Not enough data to calculate 200-day SMA
            return "Hold"

        close_prices = historical_data['Close']

        # Calculate indicators
        sma50 = self._calculate_sma(close_prices, 50)
        sma200 = self._calculate_sma(close_prices, 200)
        rsi = self._calculate_rsi(close_prices)

        # Get the most recent values
        last_sma50 = sma50.iloc[-1]
        last_sma200 = sma200.iloc[-1]
        last_rsi = rsi.iloc[-1]

        # Previous day's values for cross check
        prev_sma50 = sma50.iloc[-2]
        prev_sma200 = sma200.iloc[-2]

        # --- Strategy Logic ---
        # Priority: Sell signals, then Buy signals. Default is Hold.

        # RSI Overbought (Sell Signal)
        if last_rsi > 70:
            return "Sell"

        # Death Cross (Sell Signal)
        if last_sma50 < last_sma200 and prev_sma50 >= prev_sma200:
            return "Sell"

        # RSI Oversold (Buy Signal)
        if last_rsi < 30:
            return "Buy"

        # Golden Cross (Buy Signal)
        if last_sma50 > last_sma200 and prev_sma50 <= prev_sma200:
            return "Buy"

        return "Hold"
