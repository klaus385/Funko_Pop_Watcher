#!/bin/bash

# This is to know if testing or not
# Helps Not having to comment out the final
# Step of checking out.
POPENV="$1"
export POPENV

source Funko_Pop_Watcher/bin/activate

# Start Bot with Production ENV Variables
if [[ "$1" == "prd" ]];
then
    export TELEGRAM_TOKEN="653625270:AAE3SY6TQp7eV_XdwjT1eeLqCRGWMX9HR0s"
    export TELEGRAM_CHATID="482379749"
# Start Bot with Development ENV Variables
elif [[ "$1" == "dev" ]];
then
    export TELEGRAM_TOKEN="889567177:AAEfsXXFU2p2hIGNn0JwMYTO4zUf7tEMxRo"
    export TELEGRAM_CHATID="482379749"
# Start Bot with Production ENV Variables when no matches occur
else
    export TELEGRAM_TOKEN="653625270:AAE3SY6TQp7eV_XdwjT1eeLqCRGWMX9HR0s"
    export TELEGRAM_CHATID="482379749"
fi

# Start Bot
python ./pop_bot.py
