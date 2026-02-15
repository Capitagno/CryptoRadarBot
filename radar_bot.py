import os
import yfinance as yf
import requests

# === CONFIGURAZIONE ===
TOKEN = os.environ.get('TELEGRAM_TOKEN')
CHAT_ID = os.environ.get('TELEGRAM_CHAT_ID')

# === 📝 PORTAFOGLIO REALE (Prezzi in USDC/USD) ===
PORTAFOGLIO = {
    'BNB':  {'qty': 0.555,   'pmc_usdc': 629.99},
    'OP':   {'qty': 1783.77, 'pmc_usdc': 0.1962},
    'STRK': {'qty': 6782.94, 'pmc_usdc': 0.0516},
}

def invia_telegram(messaggio):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    payload = {"chat_id": CHAT_ID, "text": messaggio, "parse_mode": "Markdown"}
    requests.post(url, json=payload, timeout=15)

def get_bilancio_euro():
    report = "\n\n💰 *BILANCIO (BASE USDC)*"
    totale_pnl_eur = 0.0
    valore_totale_eur = 0.0

    try:
        # Recuperiamo il cambio EUR/USD per la conversione finale
        usd_eur_data = yf.download("EURUSD=X", period="1d", progress=False)
        eur_usd_rate = float(usd_eur_data['Close'].iloc[-1]) # 1 EUR = X USD
    except:
        eur_usd_rate = 1.08

    for coin, dati in PORTAFOGLIO.items():
        try:
            # Ticker specifici per Yahoo Finance
            symbol = f"{coin}-USD"
            if coin == "STRK": symbol = "STRK22691-USD" # Starknet reale
            
            data = yf.download(symbol, period="1d", interval="1m", progress=False)
            if data.empty: continue
            
            # Prezzo attuale in USD/USDC
            prezzo_attuale_usdc = float(data['Close'].iloc[-1])
            
            # Calcolo PnL in Dollari/USDC
            pnl_usdc_per_coin = prezzo_attuale_usdc - dati['pmc_usdc']
            pnl_perc = (pnl_usdc_per_coin / dati['pmc_usdc']) * 100
            
            # Conversione Valori in Euro per il report
            valore_attuale_eur = (prezzo_attuale_usdc * dati['qty']) / eur_usd_rate
            pnl_totale_eur = (pnl_usdc_per_coin * dati['qty']) / eur_usd_rate
            
            totale_pnl_eur += pnl_totale_eur
            valore_totale_eur += valore_attuale_eur
            
            report += f"\n*{coin}*: {pnl_totale_eur:+.2f}€ ({pnl_perc:+.2f}%)\n   _Price: {prezzo_attuale_usdc:.4f} USDC_"
        except: continue
    
    report += f"\n\n📊 *PNL TOTALE*: {totale_pnl_eur:+.2f}€"
    report += f"\n🏦 *VALORE PORT*: {valore_totale_eur:.2f}€"
    return report

def run_radar_v39():
    try:
        fng = requests.get('https://api.alternative.me/fng/').json()['data'][0]['value']
    except: fng = "N/A"
    
    titolo = f"🚀 *REPORT RADAR v39*\n*Sentiment*: {fng}/100"
    invia_telegram(titolo + get_bilancio_euro())

if __name__ == "__main__":
    run_radar_v39()
