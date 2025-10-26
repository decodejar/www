import os
import requests
import json
from datetime import datetime, timezone

def fetch_and_save_data():
    """
    Loads existing historical data, then fetches any new data from CoinGecko
    since the last entry and appends it, or fetches all history if no file exists.
    """
    # The CoinGecko Pro API key is typically passed via environment variable
    api_key = os.getenv('COINGECKO_PRO_API_KEY')
    if not api_key:
        print("Error: COINGECKO_PRO_API_KEY secret is not set.")
        return
    else:
        print("Successfully loaded COINGECKO_PRO_API_KEY secret.")

    script_dir = os.path.dirname(os.path.abspath(__file__))
    data_filename = os.path.join(script_dir, "price_data.json")

    existing_data = []
    last_timestamp_sec = 0

    # Step 1: Load the existing pre-filled data and find the last timestamp.
    try:
        with open(data_filename, 'r') as f:
            existing_data = json.load(f)
            if existing_data:
                # Get the timestamp from the very last entry in the file.
                last_timestamp_sec = existing_data[-1][0]
                print(f"Last entry in local data is from: {datetime.fromtimestamp(last_timestamp_sec, tz=timezone.utc).strftime('%Y-%m-%d')}")
            else:
                print("Local data file is empty.")
    except (FileNotFoundError, json.JSONDecodeError):
        print("Warning: 'price_data.json' not found or is invalid.")
        last_timestamp_sec = 0


    # Step 2: Determine the start and end timestamps for the API call.
    current_timestamp = int(datetime.now(timezone.utc).timestamp())

    if last_timestamp_sec > 0:
        # File exists: Fetch data starting from the second after the last recorded entry
        # to get only new data and avoid duplicates.
        start_timestamp = last_timestamp_sec + 1
        print(f"Fetching new data since: {datetime.fromtimestamp(start_timestamp, tz=timezone.utc).strftime('%Y-%m-%d %H:%M:%S')}")
    else:
        # File not found/empty: Fetch all history since a safe early date (Jan 1, 2021)
        # to ensure we capture the full history of Bittensor.
        start_date = datetime(2021, 1, 1, tzinfo=timezone.utc)
        start_timestamp = int(start_date.timestamp())
        print(f"Fetching all historical data since: {start_date.strftime('%Y-%m-%d')}")
    
    
    # Step 3: Construct the API URL using the Market Chart Range endpoint.
    # We use the pro-api domain and the 'x_cg_pro_api_key' parameter.
    api_url = (
        f"https://pro-api.coingecko.com/api/v3/coins/bittensor/market_chart/range"
        f"?vs_currency=usd&from={start_timestamp}&to={current_timestamp}"
        f"&x_cg_pro_api_key={api_key}"
    )

    try:
        response = requests.get(api_url, timeout=60)
        response.raise_for_status()
        
        # The 'market_chart/range' endpoint returns data with very high resolution if the range is small.
        # It's better to fetch it all and filter/aggregate later if needed, but for daily prices, 
        # the structure will be consistent.
        new_data_raw = response.json().get('prices')

        if not isinstance(new_data_raw, list):
            print(f"Error: API returned an unexpected data format: {response.json()}")
            return
        
        # Step 4: Filter out duplicates and append only the new entries.
        new_entries_count = 0
        
        # Create a set of existing timestamps (in seconds) for fast lookups.
        existing_timestamps_sec = {entry[0] for entry in existing_data}

        for entry in new_data_raw:
            timestamp_ms = entry[0]
            timestamp_sec = timestamp_ms // 1000 # CoinGecko typically uses milliseconds
            price = entry[1]
            
            # Only add data that is truly new and not already in the existing set.
            # We use `existing_timestamps_sec` to handle potential duplicates returned by the API range.
            if timestamp_sec not in existing_timestamps_sec:
                existing_data.append([timestamp_sec, price])
                existing_timestamps_sec.add(timestamp_sec) # Add to the set to prevent duplicates from the same API call
                new_entries_count += 1
        
        if new_entries_count > 0:
            # Sort the combined data by timestamp to ensure it's always in chronological order.
            existing_data.sort(key=lambda x: x[0])
            
            with open(data_filename, 'w') as f:
                # Use ensure_ascii=False for better readability in case of non-ASCII characters (though unlikely for prices)
                json.dump(existing_data, f, indent=2)
            print(f"Successfully added {new_entries_count} new data point(s). Total entries: {len(existing_data)}")
        else:
            print("No new data to add. The file is already up-to-date.")

    except requests.exceptions.HTTPError as e:
        print(f"HTTP Error occurred while fetching from CoinGecko: {e}")
        print(f"Response body: {e.response.text}")
    except requests.exceptions.RequestException as e:
        print(f"An error occurred while fetching data: {e}")
    except (json.JSONDecodeError, KeyError) as e:
        print(f"Error processing data from the API response. Error: {e}")

if __name__ == "__main__":
    fetch_and_save_data()
