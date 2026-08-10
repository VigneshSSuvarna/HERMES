import requests
import json
import os

def get_ethereum_price():
    url = 'https://min-api.cryptocompare.com/data/price?fsym=ETH&tsyms=USD'
    response = requests.get(url)
    data = response.json()
    price = data['USD']
    return price

def save_price_to_file(price):
    desktop = os.path.join(os.path.join(os.environ['USERPROFILE']), 'Desktop')
    filename = 'ethereum_price.txt'
    filepath = os.path.join(desktop, filename)
    with open(filepath, 'w') as file:
        file.write(f'Current Ethereum price: {price} USD')
    print('Ethereum price saved to file.')

def main():
    price = get_ethereum_price()
    save_price_to_file(price)
    print('Current Ethereum price fetched and saved to file on desktop.')

if __name__ == '__main__':
    main()