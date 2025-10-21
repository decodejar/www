import os
import requests
import json

def fetch_and_save_data():
    """
    Fetches historical price data from the Taostats API using a header for authentication
    and saves it to a JSON file in the same directory as the script.
    """
    api_key = os.getenv('TAOSTATS_API_KEY')
    if not api_key:
        print("Error: TAOSTATS_API_KEY secret is not set in the GitHub repository.")
        return

    api_url = "https://taostats.com/api/price/history"
    
    script_dir = os.path.dirname(os.path.abspath(__file__))
    output_filename = os.path.join(script_dir, "price_data.json")

    print(f"Fetching data from Taostats API and saving to {output_filename}...")
    
    # --- CORRECTED AUTHENTICATION ---
    # The API key should be sent as a request header, not in the body.
    headers = {
        'Content-Type': 'application/json',
        'X-API-Key': api_key
    }
    
    try:
        # A POST request is still used, but with the key in the headers.
        response = requests.post(api_url, headers=headers, timeout=30)
        
        # This will raise an exception for HTTP error codes (e.g., 401, 403, 500).
        response.raise_for_status()
        
        data = response.json()

        if not isinstance(data, list):
            print(f"Error: API returned an unexpected data format: {data}")
            return

        data.sort(key=lambda x: x[0])

        print(f"Successfully fetched {len(data)} data points.")

        with open(output_filename, 'w') as f:
            json.dump(data, f)
            
        print(f"Data successfully saved.")

    except requests.exceptions.HTTPError as e:
        print(f"HTTP Error occurred: {e}")
        print(f"Response body: {e.response.text}")
    except requests.exceptions.RequestException as e:
        print(f"An error occurred while fetching data: {e}")
    except json.JSONDecodeError:
        print(f"Error: Failed to decode JSON from the API response. Response was: {response.text}")

if __name__ == "__main__":
    fetch_and_save_data()

