const express = require('express');
const cors = require('cors');
const { spawn } = require('child_process');
const path = require('path');
require('dotenv').config();

const app = express();
const PORT = process.env.PORT || 3000;

// Middleware
app.use(cors());
app.use(express.json());
app.use(express.static('public'));

// Helper function to run Python scripts
function runPythonScript(scriptPath, args = [], input = null) {
    return new Promise((resolve, reject) => {
        const pythonProcess = spawn('python', [scriptPath, ...args], {
            stdio: ['pipe', 'pipe', 'pipe']
        });

        let outputData = '';
        let errorData = '';

        // Send input if provided
        if (input) {
            pythonProcess.stdin.write(input + '\n');
            pythonProcess.stdin.end();
        }

        // Collect output
        pythonProcess.stdout.on('data', (data) => {
            outputData += data.toString();
        });

        pythonProcess.stderr.on('data', (data) => {
            errorData += data.toString();
        });

        pythonProcess.on('close', (code) => {
            if (code !== 0) {
                reject(new Error(errorData || `Process exited with code ${code}`));
            } else {
                resolve(outputData);
            }
        });

        pythonProcess.on('error', (error) => {
            reject(new Error(`Failed to start Python: ${error.message}`));
        });
    });
}

// API endpoint to get Yahoo Finance stock data
app.post('/api/stock-data', async (req, res) => {
    const { ticker } = req.body;

    if (!ticker) {
        return res.status(400).json({ error: 'Ticker is required' });
    }

    try {
        console.log(`Fetching Yahoo Finance data for ${ticker}...`);
        const output = await runPythonScript('main.py', [ticker]);
        
        res.json({
            success: true,
            data: output
        });
    } catch (error) {
        console.error('Error fetching stock data:', error);
        res.status(500).json({
            error: 'Error fetching stock data',
            details: error.message
        });
    }
});

// API endpoint to get SEC data
app.post('/api/sec-data', async (req, res) => {
    const { ticker } = req.body;

    if (!ticker) {
        return res.status(400).json({ error: 'Ticker is required' });
    }

    try {
        console.log(`Fetching SEC data for ${ticker}...`);
        const output = await runPythonScript('sec_data_fetcher.py', [], ticker);
        
        res.json({
            success: true,
            data: output
        });
    } catch (error) {
        console.error('Error fetching SEC data:', error);
        res.status(500).json({
            error: 'Error fetching SEC data',
            details: error.message
        });
    }
});

// API endpoint to get financial news
app.post('/api/news', async (req, res) => {
    const { ticker, companyName } = req.body;

    if (!ticker) {
        return res.status(400).json({ error: 'Ticker is required' });
    }

    const apiKey = process.env.NEWS_API_KEY;

    if (!apiKey) {
        return res.status(500).json({
            error: 'NEWS_API_KEY not configured. Please add it to your .env file',
            articles: []
        });
    }

    try {
        console.log(`Fetching news for ${ticker}...`);
        
        const pythonCode = `
from news_fetcher import NewsFetcher
import json

try:
    apiKey = "${apiKey.replace(/"/g, '\\"')}"
    ticker = "${ticker.replace(/"/g, '\\"')}"
    companyName = "${(companyName || '').replace(/"/g, '\\"')}"

    fetcher = NewsFetcher(apiKey)
    articles = fetcher.getStockNews(ticker, companyName if companyName else None, 10)
    print(json.dumps(articles))
except Exception as e:
    print(json.dumps({"error": str(e)}))
`;

        const output = await runPythonScript('-c', [pythonCode]);
        const articles = JSON.parse(output);

        if (articles.error) {
            throw new Error(articles.error);
        }

        res.json({
            success: true,
            articles: articles
        });
    } catch (error) {
        console.error('Error fetching news:', error);
        res.json({
            success: false,
            error: 'Error fetching news (continuing without news data)',
            articles: []
        });
    }
});

// Health check endpoint
app.get('/api/health', (req, res) => {
    res.json({ status: 'ok', message: 'Server is running' });
});

// Serve the frontend
app.get('/', (req, res) => {
    res.sendFile(path.join(__dirname, 'public', 'index.html'));
});

// Start server
app.listen(PORT, () => {
    console.log(`
╔════════════════════════════════════════════════════════╗
║                                                        ║
║     AI Research Analyst Server                         ║
║                                                        ║
║     Server running on http://localhost:${PORT}          ║
║                                                        ║
║     Ready to analyze stocks!                           ║
║                                                        ║
╚════════════════════════════════════════════════════════╝
    `);
});

// Handle graceful shutdown
process.on('SIGTERM', () => {
    console.log('SIGTERM received, shutting down gracefully...');
    process.exit(0);
});

process.on('SIGINT', () => {
    console.log('\nSIGINT received, shutting down gracefully...');
    process.exit(0);
});