import requests
import json
import time
import os.path
from dotenv import load_dotenv

"""
Operations for all wallets are here.
Add
Remove
List
Monitor Transactions
"""

load_dotenv()

BLASTSCAN_API_KEY = os.getenv('BLASTSCAN_API_KEY')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')
TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')

# Get wallet transactions
def get_wallet_transactions(wallet_address):
    
    # Getting transactions
    all_transactions = f'https://api.blastscan.io/api?module=account&action=txlist&address={wallet_address}&sort=desc&apikey={BLASTSCAN_API_KEY}'
    response = requests.get(all_transactions)
    data = json.loads(response.text)
    result = data.get('result', [])
    
    # Checking if response is okay
    if not isinstance(result, list):
        print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] Error fetching transactions for {wallet_address}: {data}")
        return []

    return result

# Sending Telegram bot notification for new transactions
def send_telegram_notification(message, value, usd_value, tx_hash):
    
    # Creating telegram notification message payload
    blastscan_link = f'<a href="https://blastscan.io/tx/{tx_hash}">Blastscan</a>'
    url = f'https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage'
    payload = {'chat_id': f'{TELEGRAM_CHAT_ID}', 'text': f'{message}: {blastscan_link}\nValue: {value:.6f} (${usd_value:.2f})',
               'parse_mode': 'HTML'}
    
    # Sending telegram notification message
    response = requests.post(url, data=payload)
    
    print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] Telegram notification sent with message: {message}, value: {value}(${usd_value:.2f})")
    return response

# Monitoring wallets to check for new transactions
def monitor_wallets():
    
    # Setting wallets
    watched_wallets = set()
    file_path = "watched_wallets.txt"
    if not os.path.exists(file_path):
        open(file_path, 'w').close()

    # Getting transaction hashes and comparing
    latest_tx_hashes = {}
    latest_tx_hashes_path = "latest_tx_hashes.json"
    if os.path.exists(latest_tx_hashes_path):
        with open(latest_tx_hashes_path, "r") as f:
            latest_tx_hashes = json.load(f)

    # Getting last run time and comparing
    last_run_time = 0
    last_run_time_path = "last_run_time.txt"
    if os.path.exists(last_run_time_path):
        with open(last_run_time_path, "r") as f:
            last_run_time = int(f.read())

    # If everything is okay loop starts to check for new transactions.
    while True:
        try:
            
            # Fetch current ETH prices in USD from CoinGecko API
            eth_usd_price_url = 'https://api.coingecko.com/api/v3/simple/price?ids=ethereum&vs_currencies=usd'
            response = requests.get(eth_usd_price_url)
            data = json.loads(response.text)
            eth_usd_price = data['ethereum']['usd']
            
            # Read from file for wallets
            with open(file_path, 'r') as f:
                watched_wallets = set(f.read().splitlines())

            # For every wallet first transactions are pulled from api.
            for wallet in watched_wallets:
                wallet_address = wallet
                transactions = get_wallet_transactions(wallet_address)
                
                # Latest transaction hashes are compared.
                for tx in transactions:
                    tx_hash = tx['hash']
                    tx_time = int(tx['timeStamp'])
                    
                    if tx_hash not in latest_tx_hashes and tx_time > last_run_time:
                        if tx['to'].lower() == wallet_address.lower():
                            value = float(tx['value']) / 10**18 # Convert from wei to ETH
                            usd_value = value * (eth_usd_price) # Calculate value in USD
                            message = f'🚨 Incoming transaction detected on {wallet_address}'
                            send_telegram_notification(message, value, usd_value, tx['hash'])

                        elif tx['from'].lower() == wallet_address.lower():
                            value = float(tx['value']) / 10**18 # Convert from wei to ETH or BNB
                            usd_value = value * (eth_usd_price) # Calculate value in USD
                            message = f'🚨 Outgoing transaction detected on {wallet_address}'
                            send_telegram_notification(message, value, usd_value, tx['hash'])

                        latest_tx_hashes[tx_hash] = int(tx['blockNumber'])

            # Save latest_tx_hashes to file
            with open(latest_tx_hashes_path, "w") as f:
                json.dump(latest_tx_hashes, f)

            # Update last_run_time
            last_run_time = int(time.time())
            with open(last_run_time_path, "w") as f:
                f.write(str(last_run_time))

            # Sleep for 1 minute
            time.sleep(60)
        except Exception as e:
            print(f'An error occurred: {e}')
            # Sleep for 10 seconds before trying again
            time.sleep(10)

# Adding wallet to database.
def add_wallet(wallet_address):
    file_path = "watched_wallets.txt"
    with open(file_path, 'a') as f:
        f.write(f'{wallet_address}\n')

# Remove wallet from database.
def remove_wallet(wallet_address):
    file_path = "watched_wallets.txt"
    temp_file_path = "temp.txt"
    with open(file_path, 'r') as f, open(temp_file_path, 'w') as temp_f:
        for line in f:
            if line.strip() != f'{wallet_address}':
                temp_f.write(line)
    os.replace(temp_file_path, file_path)
    
# List wallets.
def list_wallets():

    # Open wallet database
    with open("watched_wallets.txt", "r") as f:
        wallets = [line.strip() for line in f.readlines()]
    
    if wallets:
        blast_wallets = []
        for wallet in wallets:
            blast_wallets.append(wallet)

        message = "The following wallets are currently being monitored\n"
        message += "\n"
        if blast_wallets:
            message += "Blast Wallets:\n"
            for i, wallet in enumerate(blast_wallets):
                message += f"{i+1}. {wallet}\n"
            message += "\n"
        
        print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] Telegram notification sent with message: {message}")
        return message
    else:
        message = "There are no wallets currently being monitored."
        print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] Telegram notification sent with message: {message}")
        return message