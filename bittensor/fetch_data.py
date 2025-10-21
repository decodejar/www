import os
import requests
import json

def fetch_and_save_data():
    """
    Fetches historical price data from the CoinGecko API using an API key
    and saves it to a JSON file.
    """
    api_key = os.getenv('COINGECKO_API_KEY')
    if not api_key:
        print("--- DIAGNOSTIC FAILURE ---")
        print("Error: The COINGECKO_API_KEY secret was NOT found in the environment.")
        return
    else:
        print("--- DIAGNOSTIC SUCCESS ---")
        print("Successfully loaded the COINGECKO_API_KEY secret.")

    # --- FINAL CORRECTION ---
    # The free CoinGecko API key limits historical data to the last 365 days.
    # We are changing 'days=max' to 'days=365' to comply with this limitation.
    api_url = f"https://api.coingecko.com/api/v3/coins/bittensor/market_chart?vs_currency=usd&days=365&interval=daily&x_cg_demo_api_key={api_key}"
    
    script_dir = os.path.dirname(os.path.abspath(__file__))
    output_filename = os.path.join(script_dir, "price_data.json")

    print(f"Attempting GET request to CoinGecko for the last 365 days...")
    
    try:
        response = requests.get(api_url, timeout=30)
        response.raise_for_status()
        
        data = response.json().get('prices')

        if not isinstance(data, list):
            print(f"Error: API returned an unexpected data format: {data}")
            return
        
        # Convert timestamps from milliseconds (CoinGecko) to seconds.
        processed_data = [[p[0] // 1000, p[1]] for p in data]

        print(f"Successfully fetched {len(processed_data)} data points.")

        with open(output_filename, 'w') as f:
            json.dump(processed_data, f)
            
        print(f"Data successfully saved to {output_filename}")

    except requests.exceptions.HTTPError as e:
        print(f"HTTP Error occurred: {e}")
        print(f"Response body: {e.response.text}")
    except requests.exceptions.RequestException as e:
        print(f"An error occurred while fetching data: {e}")
    except json.JSONDecodeError:
        print(f"Error: Failed to decode JSON from the API response. Response was: {response.text}")

if __name__ == "__main__":
    fetch_and_save_data()

