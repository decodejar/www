import os
import requests
import json

def fetch_and_save_data():
    """
    Fetches historical price data from the Taostats API and saves it to a JSON file.
    """
    # It is critical to store the API key as a secret in your GitHub repository settings.
    # Do not hardcode the key directly in this file.
    api_key = os.getenv('TAOSTATS_API_KEY')
    if not api_key:
        print("Error: TAOSTATS_API_KEY secret is not set in the GitHub repository.")
        return

    api_url = "https://taostats.com/api/price/history"
    output_filename = "price_data.json"

    print("Fetching data from Taostats API...")
    
    try:
        # The API key must be sent in the body of a POST request.
        response = requests.post(api_url, json={'api_key': api_key}, timeout=30)
        
        # This will raise an exception for HTTP error codes (4xx or 5xx).
        response.raise_for_status()
        
        # The response is expected to be a JSON array.
        data = response.json()

        if not isinstance(data, list):
            print(f"Error: API returned an unexpected data format.")
            return

        # Sort data by timestamp just in case it's not ordered.
        data.sort(key=lambda x: x[0])

        print(f"Successfully fetched {len(data)} data points.")

        # Save the data to the output file.
        with open(output_filename, 'w') as f:
            json.dump(data, f)
            
        print(f"Data successfully saved to {output_filename}")

    except requests.exceptions.RequestException as e:
        print(f"An error occurred while fetching data: {e}")
    except json.JSONDecodeError:
        print("Error: Failed to decode JSON from the API response.")

if __name__ == "__main__":
    fetch_and_save_data()
