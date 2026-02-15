import os
import requests
from binance.client import Client

# === CONFIGURAZIONE SECRETS ===
TOKEN = os.environ.get('TELEGRAM_TOKEN')
CHAT_ID = os.environ.get('TELEGRAM_CHAT_ID')
BIN_KEY = os.environ.get('BINANCE_API_KEY')
BIN_SEC = os.environ.get('BINANCE_API_SECRET')

# === PMC REALI (Dalla tua foto Prezzo.jpg) ===
MIEI_ACQUISTI = {
    'STRK': 0.0516,
    'OP': 0.19621341,
    'BNB': 629.99
}

def invia_telegram(messaggio):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    payload = {"chat_id": CHAT_ID, "text": messaggio, "parse_mode": "Markdown"}
    requests.post(url, json=payload, timeout=15)

def get_binance_pnl():
    if not BIN_KEY or not BIN_SEC:
        return "\n\n❌ Errore: Le chiavi non sono state passate dal file main.yml."

    try:
        client = Client(BIN_KEY, BIN_SEC)
        report = "\n\n💰 *STATO BINANCE LIVE*"
        
        for coin, buy_p in MIEI_ACQUISTI.items():
            try:
                # Seleziona la coppia corretta
                symbol = f"{coin}USDT"
                if coin in ["OP", "STRK"]: symbol = f"{coin}USDC"
                
                ticker = client.get_symbol_ticker(symbol=symbol)
                curr_p = float(ticker['price'])
                pnl = ((curr_p / buy_p) - 1) * 100
                report += f"\n*{coin}*: {pnl:+.2f}% (Prezzo: {curr_p:.4f})"
            except:
                report += f"\n*{coin}*: Coppia {symbol} non trovata."
        return report
    except Exception as e:
        return f"\n\n❌ Errore API Binance: {str(e)}"

def run_radar_v31():
    try: fng = requests.get('https://api.alternative.me/fng/').json()['data'][0]['value']
    except: fng = "N/A"
    
    titolo = f"🛰️ *RADAR v31 - BINANCE OK*\n*Sentiment*: {fng}/100"
    invia_telegram(titolo + get_binance_pnl())

if __name__ == "__main__":
    run_radar_v31()
