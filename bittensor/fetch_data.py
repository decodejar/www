import os
import requests
import json

def fetch_and_save_data():
    """
    Fetches historical price data from the Taostats API and saves it to a JSON file
    in the same directory as the script.
    """
    api_key = os.getenv('TAOSTATS_API_KEY')
    if not api_key:
        print("Error: TAOSTATS_API_KEY secret is not set in the GitHub repository.")
        return

    api_url = "https://taostats.com/api/price/history"
    
    # Get the absolute path of the directory where the script is located.
    script_dir = os.path.dirname(os.path.abspath(__file__))
    output_filename = os.path.join(script_dir, "price_data.json")

    print(f"Fetching data from Taostats API and saving to {output_filename}...")
    
    try:
        response = requests.post(api_url, json={'api_key': api_key}, timeout=30)
        response.raise_for_status()
        data = response.json()

        if not isinstance(data, list):
            print("Error: API returned an unexpected data format.")
            return

        data.sort(key=lambda x: x[0])

        print(f"Successfully fetched {len(data)} data points.")

        with open(output_filename, 'w') as f:
            json.dump(data, f)
            
        print(f"Data successfully saved.")

    except requests.exceptions.RequestException as e:
        print(f"An error occurred while fetching data: {e}")
    except json.JSONDecodeError:
        print("Error: Failed to decode JSON from the API response.")

if __name__ == "__main__":
    fetch_and_save_data()
