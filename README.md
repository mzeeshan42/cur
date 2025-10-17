# USDC/SOL Real-time Price Tracker

A Flask web application that fetches real-time USDC/USDT price data from the MEXC API and displays it on an interactive chart with comprehensive market statistics.

## Features

- **Real-time Price Updates**: Fetches price data every 5 seconds from MEXC API
- **Interactive Chart**: Beautiful line chart showing price history (last 100 updates)
- **Comprehensive Statistics**: Displays all related market data including:
  - Current price and 24h change
  - High/Low prices
  - Volume and trade count
  - Bid/Ask prices
  - Open price
- **WebSocket Integration**: Real-time updates without page refresh
- **Responsive Design**: Modern UI with Bootstrap styling
- **Connection Status**: Visual indicators for connection state

## Installation

1. Install the required dependencies:
```bash
pip install -r requirements.txt
```

2. Run the application:
```bash
python app.py
```

3. Open your browser and navigate to:
```
http://localhost:5000
```

## API Integration

The application uses the MEXC API endpoints:
- **24hr Ticker**: `https://api.mexc.com/api/v3/ticker/24hr`
- **Klines**: `https://api.mexc.com/api/v3/klines`

## Data Fields Displayed

- **Symbol**: Trading pair (USDC/USDT)
- **Price**: Current market price
- **Price Change**: 24h price change in USD and percentage
- **High Price**: 24h highest price
- **Low Price**: 24h lowest price
- **Volume**: 24h trading volume
- **Quote Volume**: 24h quote asset volume
- **Trade Count**: Number of trades in 24h
- **Bid Price**: Current best bid price
- **Ask Price**: Current best ask price
- **Open Price**: 24h opening price
- **Timestamp**: Last update time

## Technical Details

- **Backend**: Flask with Flask-SocketIO for WebSocket support
- **Frontend**: HTML5, Bootstrap 5, Chart.js
- **Real-time Updates**: WebSocket connection for live data
- **Data Storage**: In-memory storage for price history (last 100 points)
- **Update Frequency**: 5 seconds

## Requirements

- Python 3.7+
- Flask 2.3.3
- Flask-SocketIO 5.3.6
- requests 2.31.0
- eventlet 0.33.3

## Usage

The application automatically starts fetching data when launched. The chart will populate with historical data and continue updating in real-time. All market statistics are displayed in a responsive grid layout below the chart.