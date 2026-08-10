import requests
import json
import os

def get_ethereum_price():
    try:
        response = requests.get('https://min-api.cryptocompare.com/data/price?fsym=ETH&tsyms=USD')
        data = response.json()
        return data.get('USD')  # Use get() to avoid KeyError
    except requests.exceptions.RequestException as e:
        print(f"Error: {e}")
        return None

def save_price_to_file(price):
    desktop = os.path.join(os.path.join(os.path.expanduser('~')), 'Desktop')
    filename = 'ethereum_price.txt'
    filepath = os.path.join(desktop, filename)
    with open(filepath, 'w') as f:
        f.write(str(price))
    print(f"Price saved to {filepath}")

def main():
    price = get_ethereum_price()
    if price is not None:
        save_price_to_file(price)
    else:
        print("Failed to retrieve Ethereum price")

if __name__ == "__main__":
    main()