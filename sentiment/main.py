import os
import sys
import subprocess
from dotenv import load_dotenv

def main():
    # 1. Load environment variables from .env file
    # This reads the file and injects variables into os.environ
    loaded = load_dotenv()
    
    print("="*60)
    print("   MARKET SENTIMENT PIPELINE (ENV MODE)")
    print("="*60)

    if not loaded:
        print("[!] Warning: .env file not found.")
    
    # 2. Verify Keys exist
    twitter_token = os.getenv("TWITTER_BEARER_TOKEN")
    gemini_key = os.getenv("GEMINI_API_KEY")

    if not twitter_token or not gemini_key:
        print("\n[!] Error: Keys are missing.")
        print("    Please ensure you have a .env file with:")
        print("    TWITTER_BEARER_TOKEN=...")
        print("    GEMINI_API_KEY=...")
        return

    print("[+] Keys loaded successfully.")

    # 3. Step 1: Run the Fetcher
    print("\n" + "-"*30)
    print(">>> STEP 1: Fetching Tweets...")
    print("-"*30)
    
    try:
        # We pass os.environ (which now contains our loaded keys) to the child process
        subprocess.run(
            [sys.executable, "fetch_tweets.py"], 
            env=os.environ, 
            check=True
        )
    except subprocess.CalledProcessError:
        print("\n[!] Fetch script failed. Stopping pipeline.")
        return

    # 4. Step 2: Run the Analyzer
    print("\n" + "-"*30)
    print(">>> STEP 2: Analyzing with Gemini...")
    print("-"*30)

    try:
        subprocess.run(
            [sys.executable, "analyze_tweets.py"], 
            env=os.environ, 
            check=True
        )
    except subprocess.CalledProcessError:
        print("\n[!] Analysis script failed.")
        return

    print("\n" + "="*60)
    print("   PIPELINE COMPLETE")
    print("="*60)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n[!] Operation cancelled by user.")
