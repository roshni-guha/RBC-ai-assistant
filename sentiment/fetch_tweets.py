import tweepy
import csv
import datetime
import os

def fetch_optimized():
    # 1. Setup
    bearer_token = os.getenv("TWITTER_BEARER_TOKEN")
    if not bearer_token:
        print("[!] Error: No Bearer Token found in environment.")
        return

    client = tweepy.Client(bearer_token=bearer_token, wait_on_rate_limit=True)

    # 2. Configuration
    ACCOUNTS = [
        "tony_mansour", "jam_croissant", "vixologist", "_justinjc_",
        "NoelConvex", "vighnaraj2022", "jaredhstocks", "spotgamma",
        "lord_fed", "FedGuy12", "Ksidiii", "BergMilton",
        "KrisAbdelmessih", "wabuffo", "wesbury", "RyanDetrick", 
        "zerohedge"
    ]
    
    TARGET_PER_USER = 3  # Max 3 posts per user
    MAX_PAGES = 10       # We can search deeper now since we have a time-stop
    HOURS_BACK = 24      # TIME FILTER: Only look at the last 24 hours

    # Calculate the cutoff time (UTC to match Twitter)
    cutoff_time = datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(hours=HOURS_BACK)

    # 3. State Tracking
    collected_data = {user: [] for user in ACCOUNTS}
    finished_users = set() # Users who have hit their max count OR ran out of time
    
    # Build Query
    query = " OR ".join([f"from:{user}" for user in ACCOUNTS])
    query += " -is:retweet -is:reply"

    print(f"Fetching tweets from the last {HOURS_BACK} hours...")
    
    next_token = None
    page_count = 0
    stop_searching = False

    # --- THE PAGINATION LOOP ---
    while not stop_searching and page_count < MAX_PAGES:
        page_count += 1
        print(f"  > Requesting Page {page_count}...")

        try:
            response = client.search_recent_tweets(
                query=query,
                max_results=100,
                tweet_fields=['created_at', 'public_metrics', 'author_id'],
                expansions=['author_id'],
                user_fields=['username', 'name'],
                next_token=next_token
            )
        except Exception as e:
            print(f"    [!] API Error: {e}")
            break

        if not response.data:
            print("    [!] No more data available.")
            break

        # Map ID -> Username
        users_map = {u['id']: u for u in response.includes['users']}

        # Check if the whole batch is too old (Optimization)
        # If the NEWEST tweet in this batch is already older than 24h, stop everything.
        if response.data[0].created_at < cutoff_time:
            print("    [!] Batch is entirely older than 24h. Stopping.")
            break

        for tweet in response.data:
            # 1. TIME CHECK: Is this specific tweet too old?
            if tweet.created_at < cutoff_time:
                # We found a tweet older than 24h. 
                # Note: We don't break immediately because tweets aren't perfectly sorted by user,
                # but usually we are near the end of useful data.
                continue

            user_info = users_map.get(tweet.author_id)
            if not user_info: continue
            
            username = user_info.username

            # 2. COUNT CHECK: Do we already have 3 for this user?
            if len(collected_data.get(username, [])) < TARGET_PER_USER:
                collected_data[username].append({
                    "created_at": tweet.created_at,
                    "handle": username,
                    "name": user_info.name,
                    "text": tweet.text,
                    "likes": tweet.public_metrics.get('like_count', 0),
                    "retweets": tweet.public_metrics.get('retweet_count', 0),
                    "url": f"https://twitter.com/{username}/status/{tweet.id}"
                })

        # Check if we should stop pagination
        # If the OLDEST tweet in this batch is older than our cutoff, 
        # the next page will definitely be too old. Stop saving tokens.
        if response.data[-1].created_at < cutoff_time:
            print("    [!] Reached 24h time limit. Stopping pagination.")
            stop_searching = True
        
        # Continue to next page if needed
        next_token = response.meta.get('next_token')
        if not next_token:
            break

    # 4. Save to CSV
    filename = "market_tweets.csv"
    total_tweets = sum(len(tweets) for tweets in collected_data.values())
    
    with open(filename, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow(["Time (UTC)", "Handle", "Name", "Text", "Likes", "Retweets", "URL"])
        
        for user in ACCOUNTS:
            for tweet in collected_data[user]:
                writer.writerow([
                    tweet["created_at"],
                    tweet["handle"],
                    tweet["name"],
                    tweet["text"],
                    tweet["likes"],
                    tweet["retweets"],
                    tweet["url"]
                ])

    print(f"\nSuccess! Saved {total_tweets} tweets from the last 24h to {filename}")

if __name__ == "__main__":
    fetch_optimized()
