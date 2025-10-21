import os
import requests
import json
from datetime import datetime

def fetch_and_save_data():
    """
    Fetches the entire historical OHLCV data for Bittensor (TAO) from the
    CoinMarketCap API and saves it to a JSON file.
    """
    # The new secret name for the CoinMarketCap key will be COINMARKETCAP_API_KEY.
    api_key = os.getenv('COINMARKETCAP_API_KEY')
    if not api_key:
        print("Error: COINMARKETCAP_API_KEY secret is not set in the GitHub repository.")
        print("Please create this secret under Settings > Secrets and variables > Actions.")
        return

    # CoinMarketCap API endpoint for historical OHLCV data.
    api_url = "https://pro-api.coinmarketcap.com/v2/cryptocurrency/ohlcv/historical"
    
    script_dir = os.path.dirname(os.path.abspath(__file__))
    output_filename = os.path.join(script_dir, "price_data.json")

    print(f"Attempting GET request to CoinMarketCap for Bittensor (TAO)...")
    
    try:
        # --- AUTHENTICATION PER COINMARKETCAP DOCUMENTATION ---
        headers = {
            'Accepts': 'application/json',
            'X-CMC_PRO_API_KEY': api_key,
        }
        
        # Parameters to get all daily data for TAO in USD.
        params = {
            'slug': 'bittensor',
            'convert': 'USD',
            'interval': 'daily'
        }
        
        response = requests.get(api_url, headers=headers, params=params, timeout=30)
        response.raise_for_status()
        
        # The data is nested under data -> <id> -> quotes
        response_data = response.json()
        quotes = response_data.get('data', {}).get('quotes', [])

        if not quotes:
            print(f"Error: API returned no price data or in an unexpected format.")
            return

        # Process the data into [timestamp_in_seconds, close_price] format.
        # The timestamp is at 'time_close', and the price is in 'quote' -> 'USD' -> 'close'.
        processed_data = []
        for q in quotes:
            timestamp_str = q['time_close']
            # Convert ISO 8601 timestamp string to Unix timestamp in seconds.
            timestamp_dt = datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))
            timestamp_sec = int(timestamp_dt.timestamp())
            
            close_price = q['quote']['USD']['close']
            processed_data.append([timestamp_sec, close_price])

        # Sort data by timestamp just in case it's not ordered.
        processed_data.sort(key=lambda x: x[0])
        
        print(f"Successfully fetched {len(processed_data)} data points.")

        with open(output_filename, 'w') as f:
            json.dump(processed_data, f)
            
        print(f"Data successfully saved to {output_filename}")

    except requests.exceptions.HTTPError as e:
        print(f"HTTP Error occurred: {e}")
        print(f"Response body: {e.response.text}")
    except requests.exceptions.RequestException as e:
        print(f"An error occurred while fetching data: {e}")
    except (json.JSONDecodeError, KeyError) as e:
        print(f"Error processing data from the API response. Error: {e}")
        print(f"Response was: {response.text}")

if __name__ == "__main__":
    fetch_and_save_data()

