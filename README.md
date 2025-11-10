# AI Research Analyst

An AI-assisted research analyst tool that automates financial data collection for investment research. Input a ticker symbol and get comprehensive financial metrics from both Yahoo Finance and SEC filings.

## Features

- **Yahoo Finance Data**
  - Sales Growth (Y/Y) - Last 3 quarters
  - Free Cash Flow Growth (Y/Y) - Last 4 quarters
  - Gross Margins - Last 4 quarters
  - Earnings Surprise History - Last 4 earnings
  - Short Interest metrics
  - Earnings Dates (previous & next)

- **SEC Filing Data**
  - Sales Growth (Y/Y) from official 10-Q filings
  - Earnings Growth (Y/Y) from official 10-Q filings
  - EBITDA Margins (when available)

- **Financial News** (powered by NewsAPI)
  - Latest news articles for any stock
  - Filtered by ticker and company name
  - Links to full articles
  - Published dates and sources

- **Web Interface**
  - Clean, modern UI
  - Real-time data fetching
  - Tabbed interface for different data sources
  - Mobile responsive design

## Prerequisites

Before running this application, make sure you have:

- **Python 3.8+** installed
- **Node.js 14+** installed
- **npm** (comes with Node.js)
- **NewsAPI Key** (free at [newsapi.org](https://newsapi.org/))

## Installation

### 1. Clone the Repository

```bash
git clone https://github.com/roshni-guha/RBC-ai-assistant.git
cd RBC-ai-assistant
```

### 2. Install Python Dependencies

```bash
pip install yfinance pandas numpy sec-edgar-downloader requests newsapi-python
```

Or if you have a `requirements.txt`:

```bash
pip install -r requirements.txt
```

### 3. Install Node.js Dependencies

```bash
npm install
```

This will install:
- Express.js (web server)
- CORS (cross-origin support)
- dotenv (environment variables)

### 4. Set Up NewsAPI Key

1. Get a free API key from [newsapi.org](https://newsapi.org/)
2. Create a `.env` file in the project root:

```bash
cp .env.example .env
```

3. Edit `.env` and add your API key:

```
NEWS_API_KEY=your_api_key_here
```

**Note:** The free tier allows 100 requests per day, which is sufficient for development and testing.

## Running the Application

### Start the Server

```bash
npm start
```

You should see:
```
Server running on http://localhost:3000
```

### Access the Web Interface

Open your browser and navigate to:
```
http://localhost:3000
```

### Using the Application

1. Enter a ticker symbol in the search box (e.g., `AAPL`, `PLTR`, `MSFT`)
2. Click one of the buttons:
   - **Yahoo Finance Data** - Get real-time market data
   - **SEC Data** - Get official SEC filing data
   - **Financial News** - Get latest news articles
3. View results in the formatted output area
4. Switch between tabs to compare different data sources

## Project Structure

```
RBC-ai-assistant/
├── main.py                  # Yahoo Finance data fetcher
├── sec_data_fetcher.py      # SEC Edgar API data fetcher
├── news_fetcher.py          # NewsAPI data fetcher
├── server.js                # Node.js Express backend
├── package.json             # Node.js dependencies
├── .env.example             # Environment variable template
├── .env                     # Your API keys (create this)
├── public/
│   └── index.html          # Frontend web interface
└── README.md               # This file
```

## How It Works

### Backend (Node.js)

The Express server (`server.js`) provides three API endpoints:

- `POST /api/stock-data` - Executes `main.py` with the provided ticker
- `POST /api/sec-data` - Executes `sec_data_fetcher.py` with the provided ticker
- `POST /api/news` - Executes `news_fetcher.py` with the provided ticker

### Python Scripts

- **main.py**: Uses `yfinance` library to fetch data from Yahoo Finance
- **sec_data_fetcher.py**: Uses SEC Edgar API to fetch official filing data
- **news_fetcher.py**: Uses NewsAPI to fetch financial news articles

### Frontend

A single-page HTML application with:
- Clean, gradient UI design
- Real-time API calls to the backend
- Loading states and error handling
- Tabbed interface for different data sources

## Supported Tickers

The SEC data fetcher has built-in support for these tickers:
- AAPL (Apple)
- MSFT (Microsoft)
- GOOGL/GOOG (Google)
- TSLA (Tesla)
- META (Facebook/Meta)
- AMZN (Amazon)
- NVDA (Nvidia)
- PLTR (Palantir)

To add more tickers, edit the `cikMapping` dictionary in `sec_data_fetcher.py`.

## Troubleshooting

### Port Already in Use

If port 3000 is already in use, edit `server.js` and change:
```javascript
const PORT = 3000;
```
to another port number.

### Python Not Found

Make sure Python is in your PATH. Try:
```bash
python --version
# or
python3 --version
```

If using `python3`, update `server.js` to use `python3` instead of `python`.

### Module Not Found Errors

Make sure all Python packages are installed:
```bash
pip install yfinance pandas numpy sec-edgar-downloader requests
```

### SEC Data Not Available

Some companies may not have their CIK mapped. To add a new ticker:

1. Find the company's CIK at [sec.gov](https://www.sec.gov/edgar/searchedgar/companysearch.html)
2. Add it to the `cikMapping` dictionary in `sec_data_fetcher.py`

## Development

### Running Python Scripts Standalone

You can also run the Python scripts directly:

```bash
# Yahoo Finance data
python main.py

# SEC data
python sec_data_fetcher.py
```

### Stopping the Server

Press `Ctrl+C` in the terminal where the server is running.

## Future Enhancements

- Add more SEC metrics (EBITDA, operating margins, etc.)
- Export data to CSV/Excel
- Historical trend charts
- Save favorite tickers
- Comparison between multiple stocks
- Database integration for caching
- User authentication
- API rate limiting

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

ISC

## Contact

For questions or issues, please open an issue on GitHub.

---

Built with Python, Node.js, Express, and Yahoo Finance API
