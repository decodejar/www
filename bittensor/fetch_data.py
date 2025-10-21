import os
import requests
import json
import time

def fetch_and_save_data():
    """
    Fetches the entire historical price data for TAOUSDT from the Binance API
    by making multiple requests and saves it to a JSON file.
    """
    api_url = "https://api.binance.com/api/v3/klines"
    symbol = "TAOUSDT"
    interval = "1d"
    limit = 1000  # Binance API max limit per request

    script_dir = os.path.dirname(os.path.abspath(__file__))
    output_filename = os.path.join(script_dir, "price_data.json")

    print(f"Fetching full historical data for {symbol} from Binance...")
    
    all_klines = []
    end_time = None

    while True:
        try:
            params = {
                'symbol': symbol,
                'interval': interval,
                'limit': limit
            }
            if end_time:
                params['endTime'] = end_time

            print(f"Fetching chunk ending at {end_time}...")
            
            response = requests.get(api_url, params=params, timeout=30)
            response.raise_for_status()
            
            klines = response.json()

            # If the API returns an empty list, we've reached the beginning of the history
            if not klines:
                print("Reached the beginning of the trading history.")
                break

            all_klines = klines + all_klines
            
            # Set the end_time for the next request to be just before the oldest candle we just received
            end_time = klines[0][0] - 1

            # Be respectful of the API rate limits
            time.sleep(0.5)

        except requests.exceptions.HTTPError as e:
            print(f"HTTP Error occurred: {e}")
            print(f"Response body: {e.response.text}")
            return  # Stop the script on error
        except requests.exceptions.RequestException as e:
            print(f"An error occurred while fetching data: {e}")
            return
        except json.JSONDecodeError:
            print(f"Error: Failed to decode JSON from the API response. Response was: {response.text}")
            return
            
    if not all_klines:
        print("No data was fetched. Aborting.")
        return

    # Sort data by timestamp and remove duplicates
    all_klines = sorted(list({kline[0]: kline for kline in all_klines}.values()))

    # Process the data into the [timestamp_in_seconds, price] format
    # Binance provides [open_time_ms, open, high, low, close_price, ...]
    processed_data = [[kline[0] // 1000, float(kline[4])] for kline in all_klines]

    print(f"Successfully fetched a total of {len(processed_data)} data points.")

    with open(output_filename, 'w') as f:
        json.dump(processed_data, f)
        
    print(f"Data successfully saved to {output_filename}")


if __name__ == "__main__":
    fetch_and_save_data()

