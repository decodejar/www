import os
import requests
import json

def fetch_and_save_data():
    """
    Fetches historical price data from the CoinGecko API using an API key
    and saves it to a JSON file.
    """
    # --- ENHANCED DEBUGGING ---
    # Check for the secret and print status.
    api_key = os.getenv('COINGECKO_API_KEY')
    if not api_key:
        print("--- DIAGNOSTIC FAILURE ---")
        print("Error: The COINGECKO_API_KEY secret was NOT found in the environment.")
        print("Please verify the secret exists under your repository's Settings > Secrets and variables > Actions page.")
        print("Ensure it is a 'Repository secret' and not an 'Environment secret'.")
        return
    else:
        print("--- DIAGNOSTIC SUCCESS ---")
        print("Successfully loaded the COINGECKO_API_KEY secret.")
        print(f"The key starts with: '{api_key[:5]}...' to confirm it is not empty.")


    # CoinGecko API endpoint for historical market data.
    api_url = f"https://api.coingecko.com/api/v3/coins/bittensor/market_chart?vs_currency=usd&days=max&interval=daily&x_cg_demo_api_key={api_key}"
    
    script_dir = os.path.dirname(os.path.abspath(__file__))
    output_filename = os.path.join(script_dir, "price_data.json")

    print(f"Attempting GET request to CoinGecko: {api_url.split('?')[0]}")
    
    try:
        response = requests.get(api_url, timeout=30)
        response.raise_for_status()
        
        data = response.json().get('prices')

        if not isinstance(data, list):
            print(f"Error: API returned an unexpected data format: {data}")
            return
        
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

