import asyncio
import websockets
import json
import time
import requests
import hmac
import hashlib
import base64
from datetime import datetime
from flask import Flask, render_template
import threading

app = Flask(__name__)

# MEXC API credentials
MEXC_ACCESS_KEY = "mx0vglwzZ8bMfu6q15"
MEXC_SECRET_KEY = "94c3f7cca16243c792a0f5691dccb924"

# MEXC WebSocket API endpoints
MEXC_WS_URL = "wss://contract.mexc.com/edge"
MEXC_REST_URL = "https://api.mexc.com"

# Global variables for storing price data
current_price_data = {}
price_history = []
max_history = 1000
connected_clients = set()

def create_mexc_signature(params, secret_key):
    """Create MEXC API signature for futures WebSocket"""
    query_string = '&'.join([f"{k}={v}" for k, v in sorted(params.items())])
    signature = hmac.new(
        secret_key.encode('utf-8'),
        query_string.encode('utf-8'),
        hashlib.sha256
    ).hexdigest()
    return signature

def create_mexc_auth_params():
    """Create authentication parameters for MEXC futures WebSocket"""
    req_time = str(int(time.time() * 1000))
    params = {
        'apiKey': MEXC_ACCESS_KEY,
        'reqTime': req_time
    }
    signature = create_mexc_signature(params, MEXC_SECRET_KEY)
    return {
        'apiKey': MEXC_ACCESS_KEY,
        'signature': signature,
        'reqTime': req_time
    }

def fetch_usdc_sol_price():
    """Fetch USDC/SOL price data from MEXC REST API"""
    try:
        # Fetch 24hr ticker data
        ticker_response = requests.get(f"{MEXC_REST_URL}/api/v3/ticker/24hr?symbol=SOLUSDC", timeout=10)
        ticker_data = ticker_response.json()
        
        # Fetch klines for additional data
        klines_response = requests.get(f"{MEXC_REST_URL}/api/v3/klines?symbol=SOLUSDC&interval=1m&limit=1", timeout=10)
        klines_data = klines_response.json()
        
        if ticker_response.status_code == 200 and klines_response.status_code == 200 and ticker_data and klines_data:
            # Extract price data
            price_data = {
                'symbol': ticker_data.get('symbol', 'SOLUSDC'),
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
            return None
            
    except Exception as e:
        print(f"Error fetching price data: {e}")
        return None

async def mexc_websocket_client():
    """Connect to MEXC futures WebSocket API and subscribe to SOL/USDC data"""
    global current_price_data, price_history
    
    # First, get initial data from REST API
    initial_data = fetch_usdc_sol_price()
    if initial_data:
        initial_data['server_time'] = int(time.time() * 1000)
        current_price_data = initial_data
        price_history.append(initial_data)
        await broadcast_to_clients(initial_data)
    
    while True:
        try:
            print("Connecting to MEXC futures WebSocket...")
            
            # Connect to MEXC futures WebSocket
            async with websockets.connect(MEXC_WS_URL) as websocket:
                print("Connected to MEXC futures WebSocket")
                
                # Set up ping timer - send ping every 30 seconds
                last_ping_time = time.time()
                ping_interval = 30  # 30 seconds
                pong_timeout = 1    # 1 second timeout for pong
                waiting_for_pong = False
                pong_received_time = None
                
                # Send initial ping
                ping_message = {"method": "ping"}
                await websocket.send(json.dumps(ping_message))
                print("Sent initial ping message")
                
                # Try public channels first (no authentication required)
                # Subscribe to ticker for SOL_USDC
                ticker_subscribe = {
                    "method": "sub.ticker",
                    "param": {
                        "symbol": "SOL_USDC"
                    }
                }
                await websocket.send(json.dumps(ticker_subscribe))
                print("Sent subscription request for SOL_USDC ticker")
                
                # Subscribe to deals for recent trades
                deals_subscribe = {
                    "method": "sub.deal",
                    "param": {
                        "symbol": "SOL_USDC"
                    }
                }
                await websocket.send(json.dumps(deals_subscribe))
                print("Sent subscription request for SOL_USDC deals")
                
                # Listen for messages
                async for message in websocket:
                    try:
                        data = json.loads(message)
                        print(f"Received MEXC data: {data}")
                        
                        # Handle pong responses
                        if data.get('channel') == 'pong':
                            print("Received pong")
                            waiting_for_pong = False
                            pong_received_time = time.time()
                            continue
                        
                        # Handle subscription confirmations
                        if data.get('channel') == 'rs.sub.ticker' and data.get('data') == 'success':
                            print("Ticker subscription successful!")
                            continue
                        elif data.get('channel') == 'rs.sub.deal' and data.get('data') == 'success':
                            print("Deals subscription successful!")
                            continue
                        
                        # Handle ticker data
                        if data.get('channel') == 'push.ticker' and 'data' in data:
                            ticker_data = data['data']
                            if isinstance(ticker_data, dict) and 'lastPrice' in ticker_data:
                                price_data = {
                                    'symbol': ticker_data.get('symbol', 'SOLUSDC'),
                                    'price': float(ticker_data.get('lastPrice', 0)),
                                    'price_change': float(ticker_data.get('riseFallValue', 0)),
                                    'price_change_percent': float(ticker_data.get('riseFallRate', 0)) * 100,
                                    'open_price': float(ticker_data.get('lower24Price', 0)),
                                    'high_price': float(ticker_data.get('high24Price', 0)),
                                    'low_price': float(ticker_data.get('lower24Price', 0)),
                                    'close_price': float(ticker_data.get('lastPrice', 0)),
                                    'volume': float(ticker_data.get('volume24', 0)),
                                    'quote_volume': float(ticker_data.get('volume24', 0)),
                                    'count': 0,
                                    'bid_price': float(ticker_data.get('bid1', 0)),
                                    'ask_price': float(ticker_data.get('ask1', 0)),
                                    'timestamp': int(ticker_data.get('timestamp', 0)),
                                    'datetime': datetime.fromtimestamp(int(ticker_data.get('timestamp', 0)) / 1000).strftime('%Y-%m-%d %H:%M:%S') if ticker_data.get('timestamp') else datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                                    'server_time': int(time.time() * 1000)
                                }
                                
                                # Update current price data for 10Hz processor
                                current_price_data = price_data
                                
                                # Log WebSocket data reception (not broadcasting here)
                                print(f"WebSocket: Received price - ${price_data['price']}")
                        
                        # Handle deals data
                        elif data.get('channel') == 'push.deal' and 'data' in data:
                            deals_data = data['data']
                            if isinstance(deals_data, list) and len(deals_data) > 0:
                                latest_deal = deals_data[0]
                                deal_price = float(latest_deal.get('p', 0))
                                deal_volume = float(latest_deal.get('v', 0))
                                deal_side = 'buy' if latest_deal.get('T', 0) == 1 else 'sell'
                                
                                print(f"Latest deal: Price ${deal_price}, Volume {deal_volume}, Side {deal_side}")
                                
                                # Update current price data with deal information
                                if current_price_data:
                                    current_price_data['deal_price'] = deal_price
                                    current_price_data['deal_amount'] = deal_volume
                                    current_price_data['deal_side'] = deal_side
                                    current_price_data['deal_timestamp'] = int(time.time() * 1000)
                            
                    except json.JSONDecodeError as e:
                        print(f"JSON decode error: {e}")
                    except Exception as e:
                        print(f"Error processing message: {e}")
                    
                    # Check if it's time to send ping (every 30 seconds)
                    current_time = time.time()
                    if current_time - last_ping_time >= ping_interval:
                        if not waiting_for_pong:
                            # Send ping
                            await websocket.send(json.dumps(ping_message))
                            print("Sent ping (30s interval)")
                            last_ping_time = current_time
                            waiting_for_pong = True
                        else:
                            # Check if pong timeout exceeded (1 second)
                            if current_time - last_ping_time >= pong_timeout:
                                print("Pong timeout - reconnecting...")
                                break  # Break out of message loop to reconnect
                        
        except websockets.exceptions.ConnectionClosed:
            print("MEXC futures WebSocket connection closed, reconnecting in 5 seconds...")
            await asyncio.sleep(5)
        except Exception as e:
            print(f"MEXC futures WebSocket error: {e}")
            await asyncio.sleep(5)

async def high_frequency_data_processor():
    """Process data at 10Hz (100ms intervals) for consistent updates"""
    global current_price_data, price_history
    
    print("Starting 10Hz data processor...")
    last_broadcast_time = 0
    broadcast_interval = 0.1  # 100ms = 10Hz
    
    while True:
        try:
            current_time = time.time()
            
            # Only broadcast if we have data and enough time has passed
            if current_price_data and (current_time - last_broadcast_time) >= broadcast_interval:
                # Create a high-frequency data point
                hf_data = current_price_data.copy()
                hf_data['server_time'] = int(current_time * 1000)
                hf_data['frequency'] = '10Hz'
                
                # Add to history
                price_history.append(hf_data)
                
                # Keep only the last max_history data points
                if len(price_history) > max_history:
                    price_history = price_history[-max_history:]
                
                # Broadcast to all connected clients
                await broadcast_to_clients(hf_data)
                last_broadcast_time = current_time
                
                # Log every 10th update to avoid spam
                if len(price_history) % 10 == 0:
                    print(f"10Hz: Broadcasting update #{len(price_history)} - ${hf_data['price']}")
            
            # Sleep for 10ms to maintain high frequency
            await asyncio.sleep(0.01)
            
        except Exception as e:
            print(f"10Hz processor error: {e}")
            await asyncio.sleep(0.1)

async def fallback_data_fetcher():
    """REST API fallback disabled - using WebSocket only"""
    print("REST API fallback disabled - using WebSocket only for real-time data")
    # Keep the function running but don't fetch data
    while True:
        await asyncio.sleep(60)  # Sleep for 1 minute

async def broadcast_to_clients(data):
    """Broadcast data to all connected WebSocket clients"""
    global connected_clients
    print(f"Broadcasting to {len(connected_clients)} clients: {data}")
    if connected_clients:
        message = json.dumps(data)
        disconnected_clients = set()
        
        for client in connected_clients:
            try:
                await client.send(message)
            except websockets.exceptions.ConnectionClosed:
                disconnected_clients.add(client)
            except Exception as e:
                print(f"Error sending to client: {e}")
                disconnected_clients.add(client)
        
        # Remove disconnected clients
        connected_clients -= disconnected_clients

async def handle_client(websocket):
    """Handle WebSocket client connections"""
    global connected_clients
    print(f"Client connected: {websocket.remote_address}")
    connected_clients.add(websocket)
    
    try:
        # Send current data to newly connected client
        if current_price_data:
            await websocket.send(json.dumps(current_price_data))
        
        # Send price history
        if price_history:
            history_data = {
                'type': 'history',
                'data': price_history
            }
            await websocket.send(json.dumps(history_data))
        
        # Keep connection alive
        async for message in websocket:
            try:
                data = json.loads(message)
                if data.get('type') == 'request_history':
                    history_data = {
                        'type': 'history',
                        'data': price_history
                    }
                    await websocket.send(json.dumps(history_data))
            except json.JSONDecodeError:
                pass
            except Exception as e:
                print(f"Error handling client message: {e}")
                
    except websockets.exceptions.ConnectionClosed:
        print(f"Client disconnected: {websocket.remote_address}")
    except Exception as e:
        print(f"Error handling client: {e}")
    finally:
        connected_clients.discard(websocket)

async def start_websocket_server():
    """Start the WebSocket server"""
    print("Starting WebSocket server on ws://localhost:8765")
    await websockets.serve(handle_client, "localhost", 8765)

@app.route('/')
def index():
    """Main page"""
    return render_template('index.html')

def run_flask():
    """Run Flask app in a separate thread"""
    app.run(host='0.0.0.0', port=5000, debug=True, use_reloader=False)

async def main():
    """Main async function"""
    # Start Flask in a separate thread
    flask_thread = threading.Thread(target=run_flask, daemon=True)
    flask_thread.start()
    
    # Start WebSocket server, MEXC client, 10Hz processor, and fallback fetcher
    await asyncio.gather(
        start_websocket_server(),
        mexc_websocket_client(),
        high_frequency_data_processor(),
        fallback_data_fetcher()
    )

if __name__ == '__main__':
    print("Starting SOL/USDC Trading Platform with native WebSockets...")
    asyncio.run(main())