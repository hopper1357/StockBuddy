# StockBuddy

StockBuddy is a desktop application designed for retail investors to get stock market insights, recommendations, and portfolio projections. It provides a clean and intuitive graphical user interface to track stocks, manage watchlists, and analyze market data.

## Features

*   Live market index tracking (S&P 500, Dow Jones, Nasdaq, Russell 2000).
*   Real-time and historical stock data fetching.
*   Sidebar navigation for easy access to Dashboard, Watchlist, Presets, and Settings.
*   (Upcoming) Customizable recommendation engine.
*   (Upcoming) Portfolio tracking and projection modeling.

## Requirements

*   Python 3.8+
*   Dependencies listed in `requirements.txt`:
    *   `PyQt5`
    *   `yfinance`
    *   `matplotlib`
    *   `plotly`
    *   `pytest` (for development)

## Installation

1.  **Clone the repository:**
    ```bash
    git clone <repository-url>
    cd stockbuddy
    ```

2.  **Create and activate a virtual environment (recommended):**
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
    ```

3.  **Install the dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

## How to Use

To run the application, execute the following command from the root directory of the project:

```bash
python stockbuddy/main.py
```

This will launch the main application window.

---
*This application is for educational purposes only and does not constitute financial advice.*
