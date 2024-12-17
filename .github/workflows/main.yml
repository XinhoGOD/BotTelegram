name: Run Telegram Bot

on: 
  schedule_
    -cron:'0 21 * * *'
  workflow_dispatch:
jobs:
  run-bot
    runs-bot: ubuntu-lasted

    steps:
      - name: Checkout code
       uses: actions/checkout@v2

      - name: Set up Python
       uses: actions/setup-python@v2
       with:
          python-version: '3.9'

      - name: Install dependencies
       run: |
         python -m pip install --upgrade pip
         pip install -r requierements.txt 

      - name: Run the bot
        run: |
          python bot.py
        env:
          TELEGRAM_TOKEN:"7448542578:AAFTd9VT-CuMme0SAa1xhX4D08cr8pepywQ"
          CHAT_ID: "-1002232864049"
