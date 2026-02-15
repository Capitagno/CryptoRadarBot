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

def clean_float(val):
    """Estrae un valore numerico pulito per evitare errori di formato"""
    if isinstance(val, pd.Series):
        return float(val.iloc[0])
    return float(val)

def get_market_radar():
    radar_msg = "\n\n📊 *ANALISI POTENZIALE (RSI / EMA)*"
    tickers = {
        'BTC': 'BTC-USD', 'ETH': 'ETH-USD', 'SOL': 'SOL-USD', 
        'BNB': 'BNB-USD', 'OP': 'OP-USD', 'STRK': 'STRK22691-USD'
    }
    
    radar_results = []
    
    for name, symbol in tickers.items():
        try:
            df = yf.download(symbol, period="1y", interval="1d", progress=False)
            if df.empty: continue
            
            # Prezzo attuale e EMA 200
            last_price = clean_float(df['Close'].iloc[-1])
            ema200 = clean_float(df['Close'].ewm(span=200, adjust=False).mean().iloc[-1])
            
            # RSI per l'ordinamento
            rsi_series = calcola_rsi(df['Close'])
            current_rsi = clean_float(rsi_series.iloc[-1])
            
            # Distanza dalla EMA 200 (Potenziale di crescita)
            distanza_ema = ((ema200 / last_price) - 1) * 100
            
            radar_results.append({
                'name': name, 
                'rsi': current_rsi, 
                'distanza': distanza_ema
            })
        except: continue
    
    # Ordina per RSI crescente
    radar_results.sort(key=lambda x: x['rsi'])
    
    for i, res in enumerate(radar_results):
        emoji = "🟢" if i < 3 else "🔹"
        # Ora i numeri sono puliti e non manderanno in crash il bot
        radar_msg += f"\n{emoji} *{res['name']}* | RSI: {res['rsi']:.1f} | Crescita EMA: {res['distanza']:+.2f}%"
        
    return radar_msg

def get_bilancio_euro():
    report = "\n\n💰 *BILANCIO INVESTIMENTI*"
    totale_pnl_eur = 0.0
    valore_totale_eur = 0.0

    try:
        usd_eur_data = yf.download("EURUSD=X", period="1d", progress=False)
        eur_usd_rate = clean_float(usd_eur_data['Close'].iloc[-1])
    except:
        eur_usd_rate = 1.08

    for coin, dati in PORTAFOGLIO.items():
        try:
            symbol = f"{coin}-USD"
            if coin == "STRK": symbol = "STRK22691-USD"
            
            data = yf.download(symbol, period="1d", interval="1m", progress=False)
            prezzo_attuale_usdc = clean_float(data['Close'].iloc[-1])
            
            pnl_usdc_per_coin = prezzo_attuale_usdc - dati['pmc_usdc']
            pnl_perc = (pnl_usdc_per_coin / dati['pmc_usdc']) * 100
            
            valore_attuale_eur = (prezzo_attuale_usdc * dati['qty']) / eur_usd_rate
            pnl_totale_eur = (pnl_usdc_per_coin * dati['qty']) / eur_usd_rate
            
            totale_pnl_eur += pnl_totale_eur
            valore_totale_eur += valore_attuale_eur
            report += f"\n*{coin}*: {pnl_totale_eur:+.2f}€ ({pnl_perc:+.2f}%)"
        except: continue
    
    report += f"\n\n📊 *PNL TOTALE*: {totale_pnl_eur:+.2f}€"
    report += f"\n🏦 *VALORE PORT*: {valore_totale_eur:.2f}€"
    return report

def run_radar_v46():
    try:
        fng_data = requests.get('https://api.alternative.me/fng/').json()
        fng = fng_data['data'][0]['value']
    except: fng = "N/A"
    
    intestazione = f"🚀 *REPORT RADAR v46*\n*Sentiment*: {fng}/100"
    invia_telegram(intestazione + get_market_radar() + get_bilancio_euro())

if __name__ == "__main__":
    run_radar_v46()
