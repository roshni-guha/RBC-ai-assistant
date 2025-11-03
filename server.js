const express = require('express');
const cors = require('cors');
const { spawn } = require('child_process');
const path = require('path');

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

    // Run the Python script
    const pythonProcess = spawn('python', ['main.py'], {
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

// Start server
app.listen(PORT, () => {
    console.log(`Server running on http://localhost:${PORT}`);
});
