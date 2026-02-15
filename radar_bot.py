import os
import yfinance as yf
import requests

# === CONFIGURAZIONE ===
TOKEN = os.environ.get('TELEGRAM_TOKEN')
CHAT_ID = os.environ.get('TELEGRAM_CHAT_ID')

# === 📝 PMC REALI (Dalle tue foto) ===
MIEI_ACQUISTI = {
    'STRK': 0.0516,
    'OP': 0.19621341, # Prezzo reale esatto (Prezzo.jpg)
    'BNB': 629.99
}

def invia_telegram(messaggio):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    payload = {"chat_id": CHAT_ID, "text": messaggio, "parse_mode": "Markdown"}
    requests.post(url, json=payload, timeout=15)

def get_portfolio_report():
    report = "\n\n💰 *PROFITI REALI v28*"
    for coin, buy_p in MIEI_ACQUISTI.items():
        try:
            ticker = yf.Ticker(f"{coin}-USD")
            curr_p = ticker.history(period="1d")['Close'].iloc[-1]
            pnl = ((curr_p / buy_p) - 1) * 100
            report += f"\n*{coin}*: {pnl:+.2f}% (Prezzo: {curr_p:.4f})"
        except: continue
    return report

def run_radar_v28():
    try: fng = requests.get('https://api.alternative.me/fng/').json()['data'][0]['value']
    except: fng = "N/A"
    
    titolo = f"🚀 *RADAR DEFINITIVO v28*\n*Sentiment*: {fng}/100\n"
    tickers = ['BTC-USD', 'ETH-USD', 'SOL-USD', 'OP-USD', 'STRK-USD']
    radar_body = ""
    for t in tickers:
        try:
            df = yf.download(t, period="1y", interval="1d", progress=False)
            lp = df['Close'].iloc[-1].item()
            ema = df['Close'].ewm(span=200, adjust=False).mean().iloc[-1].item()
            delta = df['Close'].diff()
            rsi = (100 - (100 / (1 + (delta.where(delta > 0, 0).rolling(14).mean() / -delta.where(delta < 0, 0).rolling(14).mean())))).iloc[-1].item()
            if rsi < 45:
                st = "🟢 BUY" if (rsi < 32 and lp > ema) else "🟠 EVAL"
                radar_body += f"\n{st} *{t.split('-')[0]}* | RSI: {rsi:.1f}"
        except: continue

    invia_telegram(titolo + radar_body + get_portfolio_report())

if __name__ == "__main__":
    run_radar_v28()
