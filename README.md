# SOL/USDC Real-time Trading Platform

A professional-grade real-time cryptocurrency trading platform built with Flask and WebSockets, featuring live price updates, interactive charts, order book visualization, and market statistics for SOL/USDC trading pairs.

## 🚀 Features

### Real-time Data
- **Live Price Updates**: Real-time SOL/USDC price data from MEXC API
- **WebSocket Integration**: Instant price updates using Flask-SocketIO
- **Auto-reconnection**: Automatic reconnection on connection loss
- **Background Threading**: Non-blocking price data fetching

### Professional Trading Interface
- **Interactive Charts**: Real-time price charts with Chart.js
- **Order Book**: Live bid/ask order book visualization
- **Recent Trades**: Real-time trade history display
- **Market Statistics**: 24h high/low, volume, trade count, and more
- **Responsive Design**: Mobile-friendly interface

### Advanced UI/UX
- **Dark Theme**: Professional dark trading interface
- **Real-time Indicators**: Live connection status and update timestamps
- **Smooth Animations**: Fluid chart updates and transitions
- **Professional Styling**: Modern, clean trading platform design

## 🛠️ Technology Stack

- **Backend**: Flask, Flask-SocketIO
- **Frontend**: HTML5, CSS3, JavaScript (ES6+)
- **Charts**: Chart.js with date adapters
- **Styling**: Bootstrap 5, Custom CSS
- **Icons**: Font Awesome 6
- **API**: MEXC Exchange API

## 📦 Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd sol-usdc-trading-platform
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the application**
   ```bash
   python app.py
   ```

4. **Access the platform**
   Open your browser and navigate to `http://localhost:5000`

## 🔧 Configuration

### API Configuration
The platform uses MEXC API endpoints for real-time data:
- **Ticker Endpoint**: `https://api.mexc.com/api/v3/ticker/24hr`
- **Klines Endpoint**: `https://api.mexc.com/api/v3/klines`
- **Symbol**: SOLUSDC (Solana/USDC)

### WebSocket Settings
- **Port**: 5000
- **CORS**: Enabled for all origins
- **Async Mode**: Threading (compatible with Python 3.13+)

## 📊 API Endpoints

### WebSocket Events
- `connect`: Client connection established
- `disconnect`: Client disconnection
- `price_update`: Real-time price data update
- `request_history`: Request historical price data
- `price_history`: Historical price data response

### HTTP Routes
- `GET /`: Main trading platform interface

## 🎨 UI Components

### Header Section
- Live price display with change indicators
- Connection status indicator
- Last update timestamp

### Chart Section
- Interactive price chart
- Timeframe controls (1m, 5m, 15m, 1h)
- Real-time data visualization

### Trading Panel
- Order book with bid/ask levels
- Color-coded price levels
- Real-time updates

### Statistics Grid
- 24h high/low prices
- Volume metrics
- Trade count and statistics
- Bid/ask prices

### Recent Trades
- Live trade history
- Color-coded buy/sell indicators
- Timestamp and volume data

## 🔄 Real-time Data Flow

1. **Background Thread**: Continuously fetches price data every 5 seconds
2. **WebSocket Emission**: Sends updates to all connected clients
3. **Client Updates**: Frontend receives and displays real-time data
4. **Chart Animation**: Smooth chart updates with animations
5. **Status Indicators**: Live connection and update status

## 🎯 Key Features

### Professional Trading Interface
- **Order Book Visualization**: Real-time bid/ask levels
- **Price Charts**: Interactive, responsive charts
- **Market Depth**: Visual representation of market liquidity
- **Trade History**: Recent trades with timestamps

### Real-time Updates
- **Live Price Feed**: 5-second update intervals
- **WebSocket Communication**: Instant data transmission
- **Auto-reconnection**: Handles connection drops gracefully
- **Background Processing**: Non-blocking data fetching

### Responsive Design
- **Mobile Optimized**: Works on all device sizes
- **Dark Theme**: Professional trading interface
- **Smooth Animations**: Fluid user experience
- **Modern UI**: Clean, professional design

## 🚀 Performance

- **Lightweight**: Minimal dependencies
- **Fast Updates**: 5-second refresh rate
- **Efficient**: Background threading for data fetching
- **Responsive**: Smooth UI updates and animations

## 🔒 Security

- **CORS Enabled**: Cross-origin requests allowed
- **Input Validation**: Safe data handling
- **Error Handling**: Graceful error management
- **Rate Limiting**: API rate limiting considerations

## 📱 Browser Support

- Chrome 80+
- Firefox 75+
- Safari 13+
- Edge 80+

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## ⚠️ Disclaimer

This is a demonstration trading platform for educational purposes. It does not provide real trading functionality and should not be used for actual cryptocurrency trading without proper security measures and compliance with financial regulations.

## 🆘 Support

For support, please open an issue in the GitHub repository or contact the development team.

---

**Built with ❤️ for the crypto trading community**