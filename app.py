from flask import Flask, render_template
from flask_socketio import SocketIO, emit
import requests
import json
import time
import threading
from datetime import datetime

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-here'
socketio = SocketIO(app, cors_allowed_origins="*")

# MEXC API endpoints
MEXC_BASE_URL = "https://api.mexc.com"
TICKER_URL = f"{MEXC_BASE_URL}/api/v3/ticker/24hr"
KLINES_URL = f"{MEXC_BASE_URL}/api/v3/klines"

# Global variables for storing price data
current_price_data = {}
price_history = []
max_history = 100  # Keep last 100 data points

def fetch_usdc_sol_price():
    """Fetch USDC/SOL price data from MEXC API"""
    try:
        # Fetch 24hr ticker data
        ticker_response = requests.get(f"{TICKER_URL}?symbol=USDCUSDT", timeout=10)
        ticker_data = ticker_response.json()
        
        # Fetch klines for additional data
        klines_response = requests.get(f"{KLINES_URL}?symbol=USDCUSDT&interval=1m&limit=1", timeout=10)
        klines_data = klines_response.json()
        
        if ticker_response.status_code == 200 and klines_response.status_code == 200 and ticker_data and klines_data:
            # Extract price data
            price_data = {
                'symbol': ticker_data.get('symbol', 'USDCUSDT'),
                'price': float(ticker_data.get('lastPrice', 0)),
                'price_change': float(ticker_data.get('priceChange', 0)),
                'price_change_percent': float(ticker_data.get('priceChangePercent', 0)),
                'open_price': float(ticker_data.get('openPrice', 0)),
                'high_price': float(ticker_data.get('highPrice', 0)),
                'low_price': float(ticker_data.get('lowPrice', 0)),
                'close_price': float(ticker_data.get('lastPrice', 0)),
                'volume': float(ticker_data.get('volume', 0)),
                'quote_volume': float(ticker_data.get('quoteVolume', 0)),
                'count': int(ticker_data.get('count', 0)) if ticker_data.get('count') is not None else 0,
                'bid_price': float(ticker_data.get('bidPrice', 0)),
                'ask_price': float(ticker_data.get('askPrice', 0)),
                'timestamp': int(ticker_data.get('closeTime', 0)) if ticker_data.get('closeTime') is not None else 0,
                'datetime': datetime.fromtimestamp(int(ticker_data.get('closeTime', 0)) / 1000).strftime('%Y-%m-%d %H:%M:%S') if ticker_data.get('closeTime') is not None else datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'open_time': int(klines_data[0][0]) if klines_data and len(klines_data) > 0 else 0,
                'close_time': int(klines_data[0][6]) if klines_data and len(klines_data) > 0 else 0
            }
            
            return price_data
        else:
            print(f"API Error: Ticker status {ticker_response.status_code}, Klines status {klines_response.status_code}")
            print(f"Ticker data: {ticker_data}")
            print(f"Klines data: {klines_data}")
            return None
            
    except Exception as e:
        print(f"Error fetching price data: {e}")
        return None

def update_price_data():
    """Background thread to continuously update price data"""
    global current_price_data, price_history
    
    while True:
        price_data = fetch_usdc_sol_price()
        if price_data:
            current_price_data = price_data
            price_history.append(price_data)
            
            # Keep only the last max_history data points
            if len(price_history) > max_history:
                price_history = price_history[-max_history:]
            
            # Emit updated data to all connected clients
            socketio.emit('price_update', price_data)
            
        time.sleep(5)  # Update every 5 seconds

@app.route('/')
def index():
    """Main page"""
    return render_template('index.html')

@socketio.on('connect')
def handle_connect():
    """Handle client connection"""
    print('Client connected')
    # Send current data to newly connected client
    if current_price_data:
        emit('price_update', current_price_data)

@socketio.on('disconnect')
def handle_disconnect():
    """Handle client disconnection"""
    print('Client disconnected')

@socketio.on('request_history')
def handle_request_history():
    """Send price history to client"""
    emit('price_history', price_history)

if __name__ == '__main__':
    # Start background thread for price updates
    price_thread = threading.Thread(target=update_price_data, daemon=True)
    price_thread.start()
    
    # Run the Flask-SocketIO app
    socketio.run(app, debug=True, host='0.0.0.0', port=5000, allow_unsafe_werkzeug=True)