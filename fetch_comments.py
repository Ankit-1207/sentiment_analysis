from apify_client import ApifyClient

def extract_shortcode(url):
    try:
        url = url.split("?")[0]
        if "/p/" in url:
            return url.split("/p/")[1].split("/")[0]
        elif "/reel/" in url:
            return url.split("/reel/")[1].split("/")[0]
        elif "/tv/" in url:
            return url.split("/tv/")[1].split("/")[0]
        
        # Fallback
        parts = [p for p in url.split("/") if p]
        return parts[-1]
    except:
        return None

def fetch_comments(url, apify_token=None):
    if not apify_token:
        return ["Error: Apify API token is required. Please sign up at apify.com, go to Settings -> Integrations, and copy your Personal API token."]
        
    try:
        client = ApifyClient(apify_token)

        # Prepare actor input (using the official free apify instagram comment scraper)
        run_input = {
            "directUrls": [url],
            "resultsLimit": 50,
        }

        # Run the Actor and wait for it to finish
        run = client.actor("apify/instagram-comment-scraper").call(run_input=run_input)
        
        comments = []
        raw_items = list(client.dataset(run["defaultDatasetId"]).iterate_items())
        
        if not raw_items:
            # Apify successfully executed but generated 0 output items
            return [f"Error: Apify scraper completed but found 0 results. Check the Instagram URL or Apify run status. Status: {run.get('status')}"]
            
        for item in raw_items:
            # Apify data structure for different actors can vary a bit. Often it's 'text', sometimes 'message', etc.
            text = item.get("text") or item.get("message")
            if text:
                comments.append({
                    "text": text,
                    "username": item.get("ownerUsername", "UnknownUser"),
                    "timestamp": item.get("timestamp", "")
                })
                
        if not comments:
            return ["No comments found by parser."]
            
        return comments
        
    except Exception as e:
        print(f"Apify General error: {e}")
        return [f"Error fetching comments via Apify: {str(e)}"]