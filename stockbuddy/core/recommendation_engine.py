import pandas as pd

class RecommendationEngine:
    def _calculate_sma(self, data, window):
        return data.rolling(window=window).mean()

    def _calculate_rsi(self, data, window=14):
        delta = data.diff()
        gain = (delta.where(delta > 0, 0)).ewm(alpha=1/window, adjust=False).mean()
        loss = (-delta.where(delta < 0, 0)).ewm(alpha=1/window, adjust=False).mean()
        rs = gain / loss
        return 100 - (100 / (1 + rs))

    def _calculate_macd(self, data, fast_period=12, slow_period=26, signal_period=9):
        ema_fast = data.ewm(span=fast_period, adjust=False).mean()
        ema_slow = data.ewm(span=slow_period, adjust=False).mean()
        macd_line = ema_fast - ema_slow
        signal_line = macd_line.ewm(span=signal_period, adjust=False).mean()
        return macd_line, signal_line

    def _calculate_bollinger_bands(self, data, window=20, std_dev=2):
        sma = self._calculate_sma(data, window)
        std = data.rolling(window=window).std()
        upper_band = sma + (std * std_dev)
        lower_band = sma - (std * std_dev)
        return upper_band, lower_band

    def _calculate_stochastic_oscillator(self, historical_data, k_period=14, d_period=3):
        low_min = historical_data['Low'].rolling(window=k_period).min()
        high_max = historical_data['High'].rolling(window=k_period).max()
        k_percent = 100 * ((historical_data['Close'] - low_min) / (high_max - low_min))
        d_percent = self._calculate_sma(k_percent, d_period)
        return k_percent, d_percent

    def generate_signals(self, historical_data, rules):
        if historical_data is None or rules is None:
            return "Hold"

        # Prioritize sell signals
        for rule in rules:
            if rule.get("action") == "Sell":
                signal = self._evaluate_rule(historical_data, rule)
                if signal != "Hold":
                    return signal

        # Then check for buy signals
        for rule in rules:
            if rule.get("action") == "Buy":
                signal = self._evaluate_rule(historical_data, rule)
                if signal != "Hold":
                    return signal

        return "Hold"

    def _evaluate_rule(self, historical_data, rule):
        indicator = rule.get("indicator")
        close_prices = historical_data['Close']

        try:
            if indicator == "SMA":
                if len(close_prices) < rule['period']: return "Hold"
                sma = self._calculate_sma(close_prices, rule['period'])
                if rule['condition'] == '>' and sma.iloc[-1] > close_prices.iloc[-1]: return rule['action']
                if rule['condition'] == '<' and sma.iloc[-1] < close_prices.iloc[-1]: return rule['action']

            elif indicator == "RSI":
                if len(close_prices) < rule['period']: return "Hold"
                rsi = self._calculate_rsi(close_prices, rule['period'])
                if rule['condition'] == '>' and rsi.iloc[-1] > rule['value']: return rule['action']
                if rule['condition'] == '<' and rsi.iloc[-1] < rule['value']: return rule['action']

            elif indicator in ["Golden Cross", "Death Cross"]:
                short_sma = self._calculate_sma(close_prices, rule['short_period'])
                long_sma = self._calculate_sma(close_prices, rule['long_period'])

                if indicator == "Golden Cross" and short_sma.iloc[-2] <= long_sma.iloc[-2] and short_sma.iloc[-1] > long_sma.iloc[-1]:
                    return rule['action']
                if indicator == "Death Cross" and short_sma.iloc[-2] >= long_sma.iloc[-2] and short_sma.iloc[-1] < long_sma.iloc[-1]:
                    return rule['action']

            elif indicator == "MACD":
                macd_line, signal_line = self._calculate_macd(close_prices, rule['fast_period'], rule['slow_period'], rule['signal_period'])
                if rule['condition'] == 'crosses_above_signal' and macd_line.iloc[-2] <= signal_line.iloc[-2] and macd_line.iloc[-1] > signal_line.iloc[-1]:
                    return rule['action']

            elif indicator == "Bollinger Bands":
                upper, lower = self._calculate_bollinger_bands(close_prices, rule['period'], rule['std_dev'])
                if rule['condition'] == 'price_crosses_below_lower_band' and close_prices.iloc[-2] > lower.iloc[-2] and close_prices.iloc[-1] < lower.iloc[-1]:
                    return rule['action']

            elif indicator == "Stochastic Oscillator":
                k, d = self._calculate_stochastic_oscillator(historical_data, rule['k_period'], rule['d_period'])
                if rule['condition'] == '<' and k.iloc[-1] < rule['value'] and d.iloc[-1] < rule['value']:
                    return rule['action']

        except (KeyError, IndexError):
            # Handles missing keys in rule or not enough data for iloc
            return "Hold"

        return "Hold"
