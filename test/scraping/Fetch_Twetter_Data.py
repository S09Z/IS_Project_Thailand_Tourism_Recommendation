import tweepy
import json
import os

# Step 1: Set up Twitter API credentials
API_KEY = os.getenv('GOOGLE_API_KEY')
API_SECRET_KEY = os.getenv('GOOGLE_API_SECRET_KEY')
ACCESS_TOKEN = os.getenv('GOOGLE_ACCESS_TOKEN')
ACCESS_TOKEN_SECRET = os.getenv('GOOGLE_ACCESS_TOKEN_SECRET')
BEARER_TOKEN = os.getenv('GOOGLE_BEARER_TOKEN')

# Step 2: Authenticate to Twitter using v2 API
client = tweepy.Client(bearer_token=BEARER_TOKEN)

# Step 3: Define a function to gather tweets using v2 API
def gather_tweets_v2(query, max_tweets=100):
    tweets_data = []
    for tweet in tweepy.Paginator(client.search_recent_tweets, query=query, tweet_fields=['created_at', 'text', 'author_id', 'geo'], max_results=100).flatten(limit=max_tweets):
        tweets_data.append({
            'created_at': tweet.created_at,
            'username': tweet.author_id,  # V2 API returns user ID instead of screen_name
            'text': tweet.text,
            'location': tweet.geo  # Note: V2 API requires additional permissions for detailed location info
        })
    return tweets_data

# Step 4: Use the function to gather tweets related to Thailand tourism attractions
query = "Thailand tourism OR Thailand attraction OR Thailand travel OR Thailand vacation"
tweets = gather_tweets_v2(query=query, max_tweets=200)  # Gather 200 tweets

# Optional: Save tweets to a JSON file
with open('thailand_tourism_reviews_2024.json', 'w') as outfile:
    json.dump(tweets, outfile, indent=4)

# Print a sample tweet
print(tweets[0])