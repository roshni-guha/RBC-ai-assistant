#  AI Research Analyst

An AI-assisted research analyst tool that automates financial data collection for investment research. Input a ticker symbol and get comprehensive financial metrics from Yahoo Finance, SEC filings, and financial news sources.

## Features

### Yahoo Finance Data
- **Sales Growth (Y/Y)** - Last 3 quarters with comparative analysis
- **Free Cash Flow Growth** - Last 4 quarters with growth percentages
- **Gross Margins** - Last 4 quarters profitability metrics
- **Earnings Surprise History** - Last 4 earnings vs. estimates
- **Short Interest** - Current short positions and metrics
- **Earnings Dates** - Previous and next earnings release dates

### SEC Filing Data
- Official 10-Q filing data directly from SEC Edgar
- Sales Growth (Y/Y) from official filings
- Earnings Growth (Y/Y) from official filings
- EBITDA Margins (when available)

### Financial News
- Latest news articles for any stock (powered by NewsAPI)
- Filtered by ticker symbol and company name
- Full article links with publication dates
- Source attribution and author information

### Modern Web Interface
- Clean, professional gradient design
- Real-time data fetching with loading indicators
- Tabbed interface for organized data viewing
- Mobile responsive layout
- Error handling and user-friendly messages

## Quick Start

### Prerequisites

Before you begin, ensure you have the following installed:

- **Python 3.8+** ([Download](https://www.python.org/downloads/))
- **Node.js 14+** ([Download](https://nodejs.org/))
- **npm** (comes with Node.js)

### Installation

#### 1. Install Python Dependencies

```bash
pip install -r requirements.txt
```

This installs:
- `yfinance` - Yahoo Finance data
- `pandas` - Data manipulation
- `numpy` - Numerical operations
- `sec-edgar-downloader` - SEC filing access
- `requests` - HTTP requests
- `newsapi-python` - News API integration

#### 2. Install Node.js Dependencies

```bash
npm install
```

This installs:
- `express` - Web server framework
- `cors` - Cross-origin support
- `dotenv` - Environment variable management

#### 3. Set Up NewsAPI Key (Optional but Recommended)

1. Get a **free** API key from [newsapi.org](https://newsapi.org/)
   - Free tier: 100 requests/day
   - Perfect for development and testing

2. Create a `.env` file in the project root:

```bash
cp .env.example .env
```

3. Edit `.env` and add your API key:

```
NEWS_API_KEY=your_actual_api_key_here
PORT=3000
```

**Note:** The application will work without news data if no API key is provided.

## Usage

### Starting the Server

```bash
npm start
```

You should see:

```
╔════════════════════════════════════════════════════════╗
║                                                        ║
║     AI Research Analyst Server                         ║
║                                                        ║
║     Server running on http://localhost:3000            ║
║                                                        ║
║     Ready to analyze stocks!                           ║
║                                                        ║
╚════════════════════════════════════════════════════════╝
```

### Accessing the Application

1. Open your browser
2. Navigate to: `http://localhost:3000`
3. Enter a ticker symbol (e.g., `AAPL`, `MSFT`, `PLTR`, `TSLA`)
4. Click "Analyze Stock"

## How It Works

### Backend Architecture

**Express.js Server** (`server.js`)
- Provides REST API endpoints
- Manages Python script execution
- Handles cross-origin requests
- Serves static frontend files

**API Endpoints:**
- `POST /api/stock-data` - Yahoo Finance metrics
- `POST /api/sec-data` - SEC filing data
- `POST /api/news` - Financial news articles
- `GET /api/health` - Server health check

### Python Scripts

1. **main.py** - Yahoo Finance Integration
   - Uses `yfinance` library
   - Fetches real-time market data
   - Calculates growth metrics
   - Handles earnings data

2. **sec_data_fetcher.py** - SEC Edgar API
   - Accesses official SEC filings
   - Parses 10-Q quarterly reports
   - Extracts financial metrics
   - Provides year-over-year comparisons

3. **news_fetcher.py** - News Integration
   - NewsAPI integration
   - Filters relevant articles
   - Formats publication data
   - Handles API rate limits

### Frontend

**Single-Page Application** (`public/index.html`)
- Vanilla JavaScript (no frameworks needed)
- Responsive CSS with modern gradients
- Tabbed interface for data organization
- Real-time API communication
- Loading states and error handling

## Available Metrics

### Fundamentals Tab
- Sales Growth Y/Y (last 3 quarters)
- Free Cash Flow Growth (last 4 quarters)
- Gross Margins (last 4 quarters)
- Short Interest metrics

### Earnings Tab
- Earnings Surprise History
- Reported vs. Estimated EPS
- Surprise percentage calculations

### SEC Filings Tab
- Official filing data
- Revenue from 10-Q reports
- Earnings from official sources
- EBITDA margins (when available)

### News Tab
- Recent financial news articles
- Source and publication date
- Article descriptions
- Direct links to full articles

##  Troubleshooting

### Port Already in Use

If port 3000 is occupied, change it in `.env`:

```
PORT=8080
```

### Python Command Not Found

Try using `python3` instead. Update `server.js`:

```javascript
const pythonProcess = spawn('python3', [scriptPath, ...args]);
```

### Module Not Found Errors

Reinstall Python packages:

```bash
pip install --force-reinstall -r requirements.txt
```

### SEC Data Not Available

Some tickers need CIK mapping. To add a new ticker:

1. Find CIK at [sec.gov](https://www.sec.gov/edgar/searchedgar/companysearch.html)
2. Edit `sec_data_fetcher.py`:

```python
cikMapping = {
    'YOUR_TICKER': '0000123456',  # Add your ticker here
    # ... existing mappings
}
```

### News API Issues

- **Rate Limit:** Free tier = 100 requests/day
- **No Key:** App works without news, just shows no articles
- **Invalid Key:** Check `.env` file for typos

### CORS Errors

Make sure the server is running on `localhost:3000` and you're accessing the frontend from the same origin.

## Development

### Running in Development Mode

For automatic server restarts on file changes:

```bash
npm run dev
```

### Testing Python Scripts Standalone

You can test individual Python scripts:

```bash
# Test Yahoo Finance data
python main.py AAPL

# Test SEC data
python sec_data_fetcher.py
# Then enter ticker when prompted

# Test news fetcher
python news_fetcher.py
# Follow the prompts
```

### Debugging

1. Check browser console (F12) for frontend errors
2. Check terminal for backend/Python errors
3. Test API endpoints with curl:

```bash
# Test Yahoo Finance endpoint
curl -X POST http://localhost:3000/api/stock-data \
  -H "Content-Type: application/json" \
  -d '{"ticker":"AAPL"}'

# Test health check
curl http://localhost:3000/api/health
```

## Future Enhancements

Potential features to add:

- [ ] More SEC metrics (EBITDA, operating margins)
- [ ] Export data to CSV/Excel
- [ ] Historical trend charts
- [ ] Comparison between multiple stocks
- [ ] Database integration for caching
- [ ] User authentication and saved searches
- [ ] API rate limiting and request queuing
- [ ] Analyst estimates for future quarters
- [ ] Social sentiment analysis (Twitter/Reddit)
- [ ] Real-time stock price updates
- [ ] Custom metric calculations
- [ ] PDF report generation

## Contributing

Contributions are welcome! To contribute:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## License

ISC License - See LICENSE file for details

## Support

For questions, issues, or feature requests:
- Open an issue on GitHub
- Check existing issues for solutions
- Review troubleshooting section above

## Acknowledgments

Built with:
- Python & yfinance library
- Node.js & Express
- SEC Edgar API
- NewsAPI
- Yahoo Finance API

---

**Happy Analyzing!**
