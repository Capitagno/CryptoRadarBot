import os
import yfinance as yf
import requests

# === CONFIGURAZIONE ===
TOKEN = os.environ.get('TELEGRAM_TOKEN')
CHAT_ID = os.environ.get('TELEGRAM_CHAT_ID')

# === 📝 PORTAFOGLIO REALE (Dati Scaricati da Binance all'acquisto) ===
PORTAFOGLIO = {
    'BNB':  {'qty': 0.555,  'pmc': 629.99},
    'OP':   {'qty': 1783.77,    'pmc': 0.1962},
    'STRK': {'qty': 6782.94,  'pmc': 0.0516},
}

def invia_telegram(messaggio):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    payload = {"chat_id": CHAT_ID, "text": messaggio, "parse_mode": "Markdown"}
    requests.post(url, json=payload, timeout=15)

def get_bilancio_euro():
    report = "\n\n💰 *BILANCIO INVESTIMENTI*"
    totale_pnl_eur = 0
    valore_totale_asset = 0

    for coin, dati in PORTAFOGLIO.items():
        try:
            # Usiamo il ticker -EUR per precisione assoluta
            symbol = f"{coin}-EUR"
            data = yf.download(symbol, period="1d", interval="1m", progress=False)
            if data.empty: continue
            
            prezzo_attuale = data['Close'].iloc[-1]
            valore_attuale = prezzo_attuale * dati['qty']
            costo_iniziale = dati['pmc'] * dati['qty']
            
            pnl_eur = valore_attuale - costo_iniziale
            pnl_perc = ((prezzo_attuale / dati['pmc']) - 1) * 100
            
            totale_pnl_eur += pnl_eur
            valore_totale_asset += valore_attuale
            
            report += f"\n*{coin}*: {pnl_eur:+.2f}€ ({pnl_perc:+.2f}%)"
        except: continue
    
    report += f"\n\n📊 *PNL TOTALE*: {totale_pnl_eur:+.2f}€"
    report += f"\n🏦 *CAPITALE ATTUALE*: {valore_totale_asset:.2f}€"
    return report

def run_radar_v34():
    try: fng = requests.get('https://api.alternative.me/fng/').json()['data'][0]['value']
    except: fng = "N/A"
    
    titolo = f"🚀 *REPORT RADAR v34 - ATTIVO*\n*Sentiment*: {fng}/100"
    
    # Prezzi di mercato rapidi
    analisi = "\n\n📊 *MERCATO (EUR)*"
    for t in ['BTC-EUR', 'ETH-EUR', 'SOL-EUR']:
        try:
            df = yf.download(t, period="1d", progress=False)
            p = df['Close'].iloc[-1]
            analisi += f"\n*{t.replace('-EUR', '')}*: {p:.2f}€"
        except: continue

    invia_telegram(titolo + analisi + get_bilancio_euro())

if __name__ == "__main__":
    run_radar_v34()
