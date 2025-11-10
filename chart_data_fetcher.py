import yfinance as yf
import json
import sys
from datetime import datetime, timedelta

def fetch_chart_data(ticker, interval='1d', period='1y'):
    """
    Fetch OHLCV data for charting

    Args:
        ticker: Stock ticker symbol
        interval: Data interval (1m, 5m, 15m, 30m, 1h, 1d, 1wk, 1mo)
        period: Data period (1d, 5d, 1mo, 3mo, 6mo, 1y, 2y, 5y, 10y, ytd, max)
    """
    try:
        stock = yf.Ticker(ticker)

        # Fetch historical data
        hist = stock.history(period=period, interval=interval)

        if hist.empty:
            return {
                'success': False,
                'error': 'No data available for this ticker'
            }

        # Convert to list of candlesticks
        candlesticks = []
        volume_data = []

        for index, row in hist.iterrows():
            timestamp = int(index.timestamp())

            candlesticks.append({
                'time': timestamp,
                'open': round(float(row['Open']), 2),
                'high': round(float(row['High']), 2),
                'low': round(float(row['Low']), 2),
                'close': round(float(row['Close']), 2)
            })

            volume_data.append({
                'time': timestamp,
                'value': float(row['Volume']),
                'color': '#26a69a' if row['Close'] >= row['Open'] else '#ef5350'
            })

        # Calculate technical indicators
        indicators = calculate_indicators(hist)

        return {
            'success': True,
            'ticker': ticker,
            'interval': interval,
            'candlesticks': candlesticks,
            'volume': volume_data,
            'indicators': indicators,
            'currentPrice': round(float(hist['Close'].iloc[-1]), 2)
        }

    except Exception as e:
        return {
            'success': False,
            'error': str(e)
        }

def calculate_indicators(df):
    """Calculate technical indicators"""
    indicators = {}

    try:
        # Simple Moving Averages
        indicators['sma20'] = []
        indicators['sma50'] = []
        indicators['sma200'] = []

        if len(df) >= 20:
            sma20 = df['Close'].rolling(window=20).mean()
            for index, value in sma20.items():
                if not pd.isna(value):
                    indicators['sma20'].append({
                        'time': int(index.timestamp()),
                        'value': round(float(value), 2)
                    })

        if len(df) >= 50:
            sma50 = df['Close'].rolling(window=50).mean()
            for index, value in sma50.items():
                if not pd.isna(value):
                    indicators['sma50'].append({
                        'time': int(index.timestamp()),
                        'value': round(float(value), 2)
                    })

        if len(df) >= 200:
            sma200 = df['Close'].rolling(window=200).mean()
            for index, value in sma200.items():
                if not pd.isna(value):
                    indicators['sma200'].append({
                        'time': int(index.timestamp()),
                        'value': round(float(value), 2)
                    })

        # Exponential Moving Averages
        indicators['ema12'] = []
        indicators['ema26'] = []

        if len(df) >= 26:
            ema12 = df['Close'].ewm(span=12, adjust=False).mean()
            ema26 = df['Close'].ewm(span=26, adjust=False).mean()

            for index, value in ema12.items():
                if not pd.isna(value):
                    indicators['ema12'].append({
                        'time': int(index.timestamp()),
                        'value': round(float(value), 2)
                    })

            for index, value in ema26.items():
                if not pd.isna(value):
                    indicators['ema26'].append({
                        'time': int(index.timestamp()),
                        'value': round(float(value), 2)
                    })

        # RSI (14-period)
        indicators['rsi'] = []
        if len(df) >= 14:
            delta = df['Close'].diff()
            gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
            rs = gain / loss
            rsi = 100 - (100 / (1 + rs))

            for index, value in rsi.items():
                if not pd.isna(value):
                    indicators['rsi'].append({
                        'time': int(index.timestamp()),
                        'value': round(float(value), 2)
                    })

        # MACD
        indicators['macd'] = []
        indicators['macdSignal'] = []
        indicators['macdHistogram'] = []

        if len(df) >= 26:
            ema12 = df['Close'].ewm(span=12, adjust=False).mean()
            ema26 = df['Close'].ewm(span=26, adjust=False).mean()
            macd = ema12 - ema26
            signal = macd.ewm(span=9, adjust=False).mean()
            histogram = macd - signal

            for index, value in macd.items():
                if not pd.isna(value):
                    indicators['macd'].append({
                        'time': int(index.timestamp()),
                        'value': round(float(value), 4)
                    })

            for index, value in signal.items():
                if not pd.isna(value):
                    indicators['macdSignal'].append({
                        'time': int(index.timestamp()),
                        'value': round(float(value), 4)
                    })

            for index, value in histogram.items():
                if not pd.isna(value):
                    indicators['macdHistogram'].append({
                        'time': int(index.timestamp()),
                        'value': round(float(value), 4),
                        'color': '#26a69a' if value >= 0 else '#ef5350'
                    })

        # Bollinger Bands
        indicators['bbUpper'] = []
        indicators['bbMiddle'] = []
        indicators['bbLower'] = []

        if len(df) >= 20:
            sma20 = df['Close'].rolling(window=20).mean()
            std20 = df['Close'].rolling(window=20).std()
            upper = sma20 + (std20 * 2)
            lower = sma20 - (std20 * 2)

            for index, value in upper.items():
                if not pd.isna(value):
                    indicators['bbUpper'].append({
                        'time': int(index.timestamp()),
                        'value': round(float(value), 2)
                    })

            for index, value in sma20.items():
                if not pd.isna(value):
                    indicators['bbMiddle'].append({
                        'time': int(index.timestamp()),
                        'value': round(float(value), 2)
                    })

            for index, value in lower.items():
                if not pd.isna(value):
                    indicators['bbLower'].append({
                        'time': int(index.timestamp()),
                        'value': round(float(value), 2)
                    })

    except Exception as e:
        print(f"Error calculating indicators: {e}", file=sys.stderr)

    return indicators

if __name__ == '__main__':
    import pandas as pd

    if len(sys.argv) < 2:
        print(json.dumps({'success': False, 'error': 'Ticker required'}))
        sys.exit(1)

    ticker = sys.argv[1].strip().upper()
    interval = sys.argv[2] if len(sys.argv) > 2 else '1d'
    period = sys.argv[3] if len(sys.argv) > 3 else '1y'

    result = fetch_chart_data(ticker, interval, period)
    print(json.dumps(result))
