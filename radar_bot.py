import os
import requests
import pandas as pd
from binance.client import Client

# === CONFIGURAZIONE SECRETS (Nomi dalla tua foto secrets.jpg) ===
TOKEN = os.environ.get('TELEGRAM_TOKEN')
CHAT_ID = os.environ.get('TELEGRAM_CHAT_ID')
BIN_KEY = os.environ.get('BINANCE_API_KEY')
BIN_SEC = os.environ.get('BINANCE_API_SECRET') # Uso il nome esatto della tua foto

# === 📝 PMC REALI (Necessari per il calcolo PnL) ===
MIEI_ACQUISTI = {
    'STRK': 0.0516,
    'OP': 0.1962,
    'BNB': 629.99
}

def invia_telegram(messaggio):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    payload = {"chat_id": CHAT_ID, "text": messaggio, "parse_mode": "Markdown"}
    requests.post(url, json=payload, timeout=15)

def get_binance_data():
    try:
        # Inizializza il client Binance
        client = Client(BIN_KEY, BIN_SEC)
        report = "\n\n💰 *PORTAFOGLIO BINANCE*"
        
        for coin, buy_p in MIEI_ACQUISTI.items():
            try:
                # Prende il prezzo attuale direttamente da Binance
                symbol = f"{coin}USDT"
                if coin == "STRK": symbol = "STRKUSDC" # Adeguamento per le tue coppie
                if coin == "OP": symbol = "OPUSDC"     # Adeguamento dalla tua foto
                
                ticker = client.get_symbol_ticker(symbol=symbol)
                curr_p = float(ticker['price'])
                
                # Calcolo PnL
                pnl = ((curr_p / buy_p) - 1) * 100
                report += f"\n*{coin}*: {pnl:+.2f}% (Prezzo: {curr_p:.4f})"
            except Exception as e:
                report += f"\n*{coin}*: Errore dati ({str(e)})"
        return report
    except:
        return "\n\n❌ Errore connessione API Binance (Controlla le chiavi)."

def run_radar_v29():
    # 1. Sentiment
    try: fng = requests.get('https://api.alternative.me/fng/').json()['data'][0]['value']
    except: fng = "N/A"
    
    # 2. Intestazione
    titolo = f"🛰️ *RADAR v29 - BINANCE LIVE*\n*Sentiment*: {fng}/100"
    
    # 3. Messaggio finale
    # Nota: Ho rimosso l'analisi tecnica yfinance per concentrarci sul test Binance
    invia_telegram(titolo + get_binance_data())

if __name__ == "__main__":
    run_radar_v29()
