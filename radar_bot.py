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
    radar_msg = "\n\n📊 *ANALISI MERCATO (RSI)*"
    # Usiamo il ticker corretto per Starknet su Yahoo
    tickers = {
        'BTC': 'BTC-USD', 'ETH': 'ETH-USD', 'SOL': 'SOL-USD', 
        'OP': 'OP-USD', 'STRK': 'STRK22691-USD'
    }
    
    for name, symbol in tickers.items():
        try:
            df = yf.download(symbol, period="1y", interval="1d", progress=False)
            if df.empty: continue
            
            # Prezzo e EMA 200
            last_price = float(df['Close'].iloc[-1])
            ema200 = df['Close'].ewm(span=200, adjust=False).mean().iloc[-1]
            
            # RSI
            rsi_series = calcola_rsi(df['Close'])
            current_rsi = float(rsi_series.iloc[-1])
            
            # Logica Segnale (Potenziale)
            status = ""
            if current_rsi < 45:
                # Se RSI molto basso e sopra la media 200, è un BUY forte
                if current_rsi < 32 and last_price > ema200:
                    status = "🟢 *BUY*"
                else:
                    status = "🟠 *EVAL*"
            
            if status:
                radar_msg += f"\n{status} {name} | RSI: {current_rsi:.1f}"
        except: continue
    return radar_msg

def get_bilancio_euro():
    report = "\n\n💰 *BILANCIO INVESTIMENTI*"
    totale_pnl_eur = 0.0
    valore_totale_eur = 0.0

    try:
        usd_eur_data = yf.download("EURUSD=X", period="1d", progress=False)
        eur_usd_rate = float(usd_eur_data['Close'].iloc[-1])
    except:
        eur_usd_rate = 1.08

    for coin, dati in PORTAFOGLIO.items():
        try:
            symbol = f"{coin}-USD"
            if coin == "STRK": symbol = "STRK22691-USD"
            
            data = yf.download(symbol, period="1d", interval="1m", progress=False)
            prezzo_attuale_usdc = float(data['Close'].iloc[-1])
            
            # Calcolo PnL (Base USDC)
            pnl_usdc_per_coin = prezzo_attuale_usdc - dati['pmc_usdc']
            pnl_perc = (pnl_usdc_per_coin / dati['pmc_usdc']) * 100
            
            # Conversione in Euro
            valore_attuale_eur = (prezzo_attuale_usdc * dati['qty']) / eur_usd_rate
            pnl_totale_eur = (pnl_usdc_per_coin * dati['qty']) / eur_usd_rate
            
            totale_pnl_eur += pnl_totale_eur
            valore_totale_eur += valore_attuale_eur
            
            report += f"\n*{coin}*: {pnl_totale_eur:+.2f}€ ({pnl_perc:+.2f}%)"
        except: continue
    
    report += f"\n\n📊 *PNL TOTALE*: {totale_pnl_eur:+.2f}€"
    report += f"\n🏦 *VALORE PORT*: {valore_totale_eur:.2f}€"
    return report

def run_radar_v40():
    try:
        fng = requests.get('https://api.alternative.me/fng/').json()['data'][0]['value']
    except: fng = "N/A"
    
    intestazione = f"🚀 *REPORT RADAR v40*\n*Sentiment*: {fng}/100"
    
    # Combina le due parti del messaggio
    messaggio_finale = intestazione + get_market_radar() + get_bilancio_euro()
    invia_telegram(messaggio_finale)

if __name__ == "__main__":
    run_radar_v40()
