import os
import yfinance as yf
import requests

# === CONFIGURAZIONE ===
TOKEN = os.environ.get('TELEGRAM_TOKEN')
CHAT_ID = os.environ.get('TELEGRAM_CHAT_ID')

# === 📝 PORTAFOGLIO REALE (Dati aggiornati al momento dell'acquisto) ===
PORTAFOGLIO = {
    'BNB':  {'qty': 0.555,   'pmc': 629.99},
    'OP':   {'qty': 1783.77, 'pmc': 0.1962},
    'STRK': {'qty': 6782.94, 'pmc': 0.0516},
}

def invia_telegram(messaggio):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    payload = {"chat_id": CHAT_ID, "text": messaggio, "parse_mode": "Markdown"}
    requests.post(url, json=payload, timeout=15)

def get_bilancio_euro():
    report = "\n\n💰 *BILANCIO INVESTIMENTI*"
    totale_pnl_eur = 0.0
    valore_totale_asset = 0.0

    try:
        # Recuperiamo il tasso di cambio EUR/USD per la conversione in Euro
        usd_eur_data = yf.download("EURUSD=X", period="1d", progress=False)
        # Il ticker restituisce quanti USD vale 1 EUR (es. 1.08)
        eur_usd_rate = float(usd_eur_data['Close'].iloc[-1])
    except:
        eur_usd_rate = 1.08 # Valore di emergenza se Yahoo non risponde

    for coin, dati in PORTAFOGLIO.items():
        try:
            # Usiamo i ticker USD che sono i più affidabili
            symbol = f"{coin}-USD"
            data = yf.download(symbol, period="1d", interval="1m", progress=False)
            if data.empty: continue
            
            # Convertiamo il prezzo attuale da USD a EUR
            prezzo_usd = float(data['Close'].iloc[-1])
            prezzo_eur = prezzo_usd / eur_usd_rate
            
            valore_attuale_eur = prezzo_eur * dati['qty']
            costo_iniziale_eur = dati['pmc'] * dati['qty']
            
            pnl_eur = valore_attuale_eur - costo_iniziale_eur
            pnl_perc = ((prezzo_eur / dati['pmc']) - 1) * 100
            
            totale_pnl_eur += float(pnl_eur)
            valore_totale_asset += float(valore_attuale_eur)
            
            report += f"\n*{coin}*: {pnl_eur:+.2f}€ ({pnl_perc:+.2f}%)"
        except: continue
    
    report += f"\n\n📊 *PNL TOTALE*: {totale_pnl_eur:+.2f}€"
    report += f"\n🏦 *CAPITALE ATTUALE*: {valore_totale_asset:.2f}€"
    return report

def run_radar_v36():
    try:
        fng = requests.get('https://api.alternative.me/fng/').json()['data'][0]['value']
    except: fng = "N/A"
    
    titolo = f"🚀 *REPORT RADAR v36*\n*Sentiment*: {fng}/100"
    
    # Prezzi di mercato rapidi
    analisi = "\n\n📊 *MERCATO (USD)*"
    for t in ['BTC-USD', 'ETH-USD', 'SOL-USD']:
        try:
            df = yf.download(t, period="1d", progress=False)
            p = float(df['Close'].iloc[-1])
            analisi += f"\n*{t.replace('-USD', '')}
