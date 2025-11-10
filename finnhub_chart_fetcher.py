import requests
import json
import sys
from datetime import datetime, timedelta
import time

def fetch_chart_data_finnhub(ticker, api_key, interval='D', days=365):
    """
    Fetch OHLCV data from Finnhub

    Args:
        ticker: Stock ticker symbol
        api_key: Finnhub API key
        interval: Data interval (1, 5, 15, 30, 60, D, W, M)
        days: Number of days of historical data
    """
    try:
        # Calculate timestamps
        end_time = int(time.time())
        start_time = end_time - (days * 24 * 60 * 60)

        # Map interval to Finnhub format
        resolution = interval

        # Fetch candle data
        url = f"https://finnhub.io/api/v1/stock/candle"
        params = {
            'symbol': ticker,
            'resolution': resolution,
            'from': start_time,
            'to': end_time,
            'token': api_key
        }

        response = requests.get(url, params=params)
        data = response.json()

        if data.get('s') != 'ok':
            return {
                'success': False,
                'error': 'No data available for this ticker'
            }

        # Convert to candlestick format
        candlesticks = []
        volume_data = []

        for i in range(len(data['t'])):
            timestamp = data['t'][i]
            open_price = round(float(data['o'][i]), 2)
            high_price = round(float(data['h'][i]), 2)
            low_price = round(float(data['l'][i]), 2)
            close_price = round(float(data['c'][i]), 2)
            volume = float(data['v'][i])

            candlesticks.append({
                'time': timestamp,
                'open': open_price,
                'high': high_price,
                'low': low_price,
                'close': close_price
            })

            volume_data.append({
                'time': timestamp,
                'value': volume,
                'color': '#26a69a' if close_price >= open_price else '#ef5350'
            })

        # Calculate indicators
        indicators = calculate_indicators(data)

        return {
            'success': True,
            'ticker': ticker,
            'interval': interval,
            'candlesticks': candlesticks,
            'volume': volume_data,
            'indicators': indicators,
            'currentPrice': round(float(data['c'][-1]), 2) if data['c'] else 0
        }

    except Exception as e:
        return {
            'success': False,
            'error': str(e)
        }

def calculate_indicators(data):
    """Calculate technical indicators from Finnhub data"""
    indicators = {}
    closes = data['c']

    try:
        # Simple Moving Averages
        indicators['sma20'] = []
        indicators['sma50'] = []
        indicators['sma200'] = []

        if len(closes) >= 20:
            for i in range(19, len(closes)):
                sma20 = sum(closes[i-19:i+1]) / 20
                indicators['sma20'].append({
                    'time': data['t'][i],
                    'value': round(sma20, 2)
                })

        if len(closes) >= 50:
            for i in range(49, len(closes)):
                sma50 = sum(closes[i-49:i+1]) / 50
                indicators['sma50'].append({
                    'time': data['t'][i],
                    'value': round(sma50, 2)
                })

        if len(closes) >= 200:
            for i in range(199, len(closes)):
                sma200 = sum(closes[i-199:i+1]) / 200
                indicators['sma200'].append({
                    'time': data['t'][i],
                    'value': round(sma200, 2)
                })

        # Exponential Moving Averages
        indicators['ema12'] = []
        indicators['ema26'] = []

        if len(closes) >= 26:
            # Calculate EMA12
            multiplier12 = 2 / (12 + 1)
            ema12 = sum(closes[:12]) / 12

            for i in range(12, len(closes)):
                ema12 = (closes[i] - ema12) * multiplier12 + ema12
                indicators['ema12'].append({
                    'time': data['t'][i],
                    'value': round(ema12, 2)
                })

            # Calculate EMA26
            multiplier26 = 2 / (26 + 1)
            ema26 = sum(closes[:26]) / 26

            for i in range(26, len(closes)):
                ema26 = (closes[i] - ema26) * multiplier26 + ema26
                indicators['ema26'].append({
                    'time': data['t'][i],
                    'value': round(ema26, 2)
                })

        # RSI (14-period)
        indicators['rsi'] = []
        if len(closes) >= 15:
            gains = []
            losses = []

            for i in range(1, len(closes)):
                change = closes[i] - closes[i-1]
                gains.append(max(change, 0))
                losses.append(max(-change, 0))

            for i in range(13, len(gains)):
                avg_gain = sum(gains[i-13:i+1]) / 14
                avg_loss = sum(losses[i-13:i+1]) / 14

                if avg_loss == 0:
                    rsi = 100
                else:
                    rs = avg_gain / avg_loss
                    rsi = 100 - (100 / (1 + rs))

                indicators['rsi'].append({
                    'time': data['t'][i+1],
                    'value': round(rsi, 2)
                })

        # MACD
        indicators['macd'] = []
        indicators['macdSignal'] = []
        indicators['macdHistogram'] = []

        if len(closes) >= 26:
            # Calculate EMA12 and EMA26 for MACD
            multiplier12 = 2 / (12 + 1)
            multiplier26 = 2 / (26 + 1)

            ema12_vals = [sum(closes[:12]) / 12]
            ema26_vals = [sum(closes[:26]) / 26]

            for i in range(12, len(closes)):
                ema12_vals.append((closes[i] - ema12_vals[-1]) * multiplier12 + ema12_vals[-1])

            for i in range(26, len(closes)):
                ema26_vals.append((closes[i] - ema26_vals[-1]) * multiplier26 + ema26_vals[-1])

            # Calculate MACD line
            macd_vals = []
            for i in range(len(ema26_vals)):
                macd_val = ema12_vals[i+14] - ema26_vals[i]
                macd_vals.append(macd_val)

            # Calculate Signal line (9-period EMA of MACD)
            if len(macd_vals) >= 9:
                multiplier9 = 2 / (9 + 1)
                signal = sum(macd_vals[:9]) / 9

                for i in range(9, len(macd_vals)):
                    signal = (macd_vals[i] - signal) * multiplier9 + signal
                    histogram = macd_vals[i] - signal

                    indicators['macd'].append({
                        'time': data['t'][i+26],
                        'value': round(macd_vals[i], 4)
                    })

                    indicators['macdSignal'].append({
                        'time': data['t'][i+26],
                        'value': round(signal, 4)
                    })

                    indicators['macdHistogram'].append({
                        'time': data['t'][i+26],
                        'value': round(histogram, 4),
                        'color': '#26a69a' if histogram >= 0 else '#ef5350'
                    })

        # Bollinger Bands (20-period, 2 std dev)
        indicators['bbUpper'] = []
        indicators['bbMiddle'] = []
        indicators['bbLower'] = []

        if len(closes) >= 20:
            for i in range(19, len(closes)):
                window = closes[i-19:i+1]
                sma = sum(window) / 20
                variance = sum((x - sma) ** 2 for x in window) / 20
                std_dev = variance ** 0.5

                indicators['bbUpper'].append({
                    'time': data['t'][i],
                    'value': round(sma + (std_dev * 2), 2)
                })

                indicators['bbMiddle'].append({
                    'time': data['t'][i],
                    'value': round(sma, 2)
                })

                indicators['bbLower'].append({
                    'time': data['t'][i],
                    'value': round(sma - (std_dev * 2), 2)
                })

    except Exception as e:
        print(f"Error calculating indicators: {e}", file=sys.stderr)

    return indicators

if __name__ == '__main__':
    if len(sys.argv) < 3:
        print(json.dumps({'success': False, 'error': 'Ticker and API key required'}))
        sys.exit(1)

    ticker = sys.argv[1].strip().upper()
    api_key = sys.argv[2].strip()

    # Map timeframe to Finnhub resolution and days
    interval_map = {
        '1d': ('D', 365),
        '5d': ('5', 5),
        '1mo': ('60', 30),
        '3mo': ('D', 90),
        '1y': ('D', 365),
        '5y': ('W', 1825),
        'max': ('M', 3650)
    }

    period = sys.argv[3] if len(sys.argv) > 3 else '1y'
    resolution, days = interval_map.get(period, ('D', 365))

    result = fetch_chart_data_finnhub(ticker, api_key, resolution, days)
    print(json.dumps(result))
