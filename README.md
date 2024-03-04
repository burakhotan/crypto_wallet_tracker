<h1 align="center">
Crypto Wallet Transactions Tracker Bot for Blast Network
</h1>



This is a Telegram bot that tracks the transactions of added Blast wallets and sends notifications whenever a new transaction occurs. The bot uses the BlastScan APIs to gather information about transactions, and CoinGecko to fetch the current prices of ETH.

## Commands

- `/start` shows a welcome message and instructions on how to use the bot.
- `/add` adds a new wallet to track transactions for. The wallet address must be provided in the correct format (starting with '0x' for Blast(ETH) wallets), otherwise the bot will prompt the user to correct it. The added wallets are saved in a JSON file for persistence.
- `/remove` removes a wallet from the list of tracked wallets. The user must provide the wallet address in the correct format.
- `/list` shows the list of currently tracked wallets.

## Features

- Logging: the bot prompts every transaction and errors.
- Format check: the bot checks that the wallet address provided by the user is in the correct format before adding it to the list of tracked wallets.

## Requirements

To run the bot, you'll need to have Python 3.6 or later installed on your system, along with the following Python libraries:

- `requests` (for making HTTP requests to the APIs)
- `web3` (for interacting with the Ethereum blockchain)

You'll also need to obtain API keys for Blastscan, as well as a Telegram bot token. These can be obtained by following the instructions on the respective websites.

## Installation

1. Clone this repository: `git clone https://github.com/burakhotan/blast_wallet_tracker.git`
2. Install the required packages: `pip install -r requirements.txt`
3. Replace the following placeholders in the `.env.example` file with your API keys and bot token:
4. Rename `.env.example` as `.env` and save it

    ```python
    BLASTSCAN_API_KEY = '<your_blastscan_api_key>'
    TELEGRAM_BOT_TOKEN = '<your_telegram_bot_token>'
    TELEGRAM_CHAT_ID = '<your_telegram_chat_id>'
    ```
4. Start the bot: `python main.py`

## Authors
- www.github.com/burakhotan
- www.github.com/sarp-u
- www.github.com/umutyesildal

## Disclaimer

This bot is provided for educational purposes only and should not be used as financial advice. The bot does not have access to your wallet.
