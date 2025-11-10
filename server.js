const express = require('express');
const cors = require('cors');
const { spawn } = require('child_process');
const path = require('path');
require('dotenv').config();

const app = express();
const PORT = 3000;

// Middleware
app.use(cors());
app.use(express.json());
app.use(express.static('public'));

// API endpoint to get stock data
app.post('/api/stock-data', (req, res) => {
    const { ticker } = req.body;

    if (!ticker) {
        return res.status(400).json({ error: 'Ticker is required' });
    }

    // Run the Python script with ticker as argument
    const pythonProcess = spawn('python', ['main.py', ticker], {
        stdio: ['pipe', 'pipe', 'pipe']
    });

    let outputData = '';
    let errorData = '';

    // Collect output
    pythonProcess.stdout.on('data', (data) => {
        outputData += data.toString();
    });

    pythonProcess.stderr.on('data', (data) => {
        errorData += data.toString();
    });

    pythonProcess.on('close', (code) => {
        if (code !== 0) {
            return res.status(500).json({
                error: 'Error running Python script',
                details: errorData
            });
        }

        res.json({
            success: true,
            data: outputData
        });
    });
});

// API endpoint to get SEC data
app.post('/api/sec-data', (req, res) => {
    const { ticker } = req.body;

    if (!ticker) {
        return res.status(400).json({ error: 'Ticker is required' });
    }

    // Run the SEC Python script
    const pythonProcess = spawn('python', ['sec_data_fetcher.py'], {
        stdio: ['pipe', 'pipe', 'pipe']
    });

    let outputData = '';
    let errorData = '';

    // Send ticker to Python script
    pythonProcess.stdin.write(ticker + '\n');
    pythonProcess.stdin.end();

    // Collect output
    pythonProcess.stdout.on('data', (data) => {
        outputData += data.toString();
    });

    pythonProcess.stderr.on('data', (data) => {
        errorData += data.toString();
    });

    pythonProcess.on('close', (code) => {
        if (code !== 0) {
            return res.status(500).json({
                error: 'Error running SEC Python script',
                details: errorData
            });
        }

        res.json({
            success: true,
            data: outputData
        });
    });
});

// API endpoint to get chart data
app.post('/api/chart-data', (req, res) => {
    const { ticker, interval, period } = req.body;

    if (!ticker) {
        return res.status(400).json({ error: 'Ticker is required' });
    }

    const intervalParam = interval || '1d';
    const periodParam = period || '1y';

    // Run the chart data fetcher Python script
    const pythonProcess = spawn('python', ['chart_data_fetcher.py', ticker, intervalParam, periodParam], {
        stdio: ['pipe', 'pipe', 'pipe']
    });

    let outputData = '';
    let errorData = '';

    // Collect output
    pythonProcess.stdout.on('data', (data) => {
        outputData += data.toString();
    });

    pythonProcess.stderr.on('data', (data) => {
        errorData += data.toString();
    });

    pythonProcess.on('close', (code) => {
        if (code !== 0) {
            return res.status(500).json({
                error: 'Error fetching chart data',
                details: errorData
            });
        }

        try {
            const chartData = JSON.parse(outputData);
            res.json(chartData);
        } catch (error) {
            res.status(500).json({
                error: 'Error parsing chart data',
                details: error.message
            });
        }
    });
});

// API endpoint to get news
app.post('/api/news', (req, res) => {
    const { ticker, companyName } = req.body;

    if (!ticker) {
        return res.status(400).json({ error: 'Ticker is required' });
    }

    const apiKey = process.env.NEWS_API_KEY;

    if (!apiKey) {
        return res.status(500).json({
            error: 'NEWS_API_KEY not configured. Please add it to your .env file'
        });
    }

    // Run the news fetcher Python script
    const pythonProcess = spawn('python', ['-c', `
from news_fetcher import NewsFetcher
import json

apiKey = "${apiKey}"
ticker = "${ticker}"
companyName = "${companyName || ''}"

fetcher = NewsFetcher(apiKey)
articles = fetcher.getStockNews(ticker, companyName if companyName else None, 10)
print(json.dumps(articles))
    `], {
        stdio: ['pipe', 'pipe', 'pipe']
    });

    let outputData = '';
    let errorData = '';

    // Collect output
    pythonProcess.stdout.on('data', (data) => {
        outputData += data.toString();
    });

    pythonProcess.stderr.on('data', (data) => {
        errorData += data.toString();
    });

    pythonProcess.on('close', (code) => {
        if (code !== 0) {
            return res.status(500).json({
                error: 'Error fetching news',
                details: errorData
            });
        }

        try {
            const articles = JSON.parse(outputData);
            res.json({
                success: true,
                articles: articles
            });
        } catch (error) {
            res.status(500).json({
                error: 'Error parsing news data',
                details: error.message
            });
        }
    });
});

// Start server
app.listen(PORT, () => {
    console.log(`Server running on http://localhost:${PORT}`);
});
