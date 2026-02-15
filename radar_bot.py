import os
import yfinance as yf
import requests
import pandas as pd

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

def calcola_rsi(data, window=14):
    delta = data.diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=window).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=window).mean()
    rs = gain / loss
    return 100 - (100 / (1 + rs))

def get_market_radar():
    radar_msg = "\n\n📊 *ANALISI POTENZIALE*"
    tickers = {
        'BTC': 'BTC-USD', 'ETH': 'ETH-USD', 'SOL': 'SOL-USD', 
        'BNB': 'BNB-USD', 'OP': 'OP-USD', 'STRK': 'STRK22691-USD'
    }
    
    radar_results = []
    
    for name, symbol in tickers.items():
        try:
            df = yf.download(symbol, period="1y", interval="1d", progress=False)
            if df.empty: continue
            
            rsi_series = calcola_rsi(df['Close'])
            current_rsi = float(rsi_series.iloc[-1])
            
            # Calcolo Potenziale: più l'RSI è basso, più il potenziale è alto
            potenziale = 100 - current_rsi
            
            radar_results.append({
                'name': name, 
                'rsi': current_rsi, 
                'potenziale': potenziale
            })
        except: continue
    
    # Ordina per Potenziale Decrescente (il più alto in cima)
    radar_results.sort(key=lambda x: x['potenziale'], reverse=True)
    
    for i, res in enumerate(radar_results):
        # Mettiamo in grassetto i primi tre (i migliori)
        prefix = "🔥 " if i < 3 else "🔹 "
        radar_msg += f"\n{prefix}*{res['name']}* | Potenziale: {res['potenziale']:.1f}%"
        
    return radar_msg

def get_bilancio_euro():
    report = "\n\n💰 *BILANCIO INVESTIMENTI*"
    totale_pnl_eur = 0.0
    valore_totale_eur = 0.0

    try:
        usd_eur_data = yf.download("EURUSD=X", period="1d", progress=False)
