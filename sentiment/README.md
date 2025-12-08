# Market Sentiment Analysis Pipeline

This project automates the process of tracking financial sentiment on X (formerly Twitter). It fetches recent posts from a curated list of macro-economists and traders, filters the data, and uses Google's Gemini AI to generate a daily market summary (Bullish/Bearish sentiment, key themes, and outliers).

## Features
* **Smart Fetching:** Pulls the last 3 posts from 17+ high-signal accounts (e.g., SpotGamma, ZeroHedge, FedGuy12).
* **Time Filtering:** Automatically excludes posts older than 24 hours.
* **Spam Protection:** Uses pagination to ensure "loud" accounts don't drown out quiet ones.
* **AI Analysis:** Uses Google Gemini 2.0 Flash to summarize the raw text into actionable market insights.
* **Secure:** Uses environment variables to keep API keys safe.

## Prerequisites

You need **Python 3.8+** and the following API keys:
1.  **X (Twitter) API:** Basic Tier (Bearer Token). (HIGHLY recommend basic tier)
2.  **Google Gemini API:** Free tier key from Google AI Studio.

## Installation

1.  Clone this repository or download the files.
2.  Enter keys in .env file
3.  Install the required dependencies:

```bash
pip install tweepy pandas google-genai python-dotenv
