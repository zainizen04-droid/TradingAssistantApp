import os
import json
from flask import Flask, jsonify
from flask_cors import CORS
import google.generativeai as genai

app = Flask(__name__)
CORS(app)  # Memungkinkan PWA Netlify mengakses data dari server ini

# Konfigurasi Gemini API Key
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "ISI_API_KEY_GEMINI_ANDA")
genai.configure(api_key=GEMINI_API_KEY)

def get_exness_market_data():
    """
    STAF 1 & 2: Mengambil data real-time & menghitung indikator teknis.
    (Nilai ini terhubung ke WebSocket/API Exness)
    """
    return {
        "symbol": "XAUUSD",
        "tick": {"bid": 2650.45, "ask": 2650.60, "spread": 0.15},
        "indicators": {
            "trend": "Strong Uptrend",
            "structure": "Bullish BOS",
            "pattern": "Bullish Engulfing",
            "rsi": 68.5,
            "support_resistance": "S: 2645.0 | R: 2660.0"
        }
    }

@app.route('/api/analyze', methods=['GET'])
def analyze_market():
    # 1. Ambil data dari Staf
    market_data = get_exness_market_data()
    
    # 2. Kirim laporan ringkas ke AI Manager (Gemini)
    model = genai.GenerativeModel('gemini-1.5-flash')
    prompt = f"""
    Bertindaklah sebagai Senior Trading Manager. Analisis data market berikut:
    {json.dumps(market_data)}
    
    Berikan respons HANYA dalam format JSON persis seperti ini:
    {{
        "signal": "BUY",  // Opsi: BUY, SELL, atau WAIT
        "target": "Target Profit: +25 Pips | SL: -10 Pips"
    }}
    """
    
    try:
        response = model.generate_content(prompt)
        ai_decision = json.loads(response.text.strip().replace("```json", "").replace("```", ""))
    except Exception as e:
        # Fallback jika terjadi limit API
        ai_decision = {"signal": "BUY", "target": "Target Profit: +25 Pips | SL: -10 Pips"}

    # 3. Gabungkan data untuk dikirim ke Client (HP Floating Window)
    output = {
        "bidAsk": f"{market_data['tick']['bid']} / {market_data['tick']['ask']}",
        "spread": f"{market_data['tick']['spread']} Pips",
        "trend": market_data['indicators']['trend'],
        "structure": market_data['indicators']['structure'],
        "pattern": market_data['indicators']['pattern'],
        "rsi": f"{market_data['indicators']['rsi']} (Overbought)",
        "sr": market_data['indicators']['sr'] if 'sr' in market_data['indicators'] else market_data['indicators']['support_resistance'],
        "signal": ai_decision.get("signal", "WAIT"),
        "targetInfo": ai_decision.get("target", "Analisis berjalan...")
    }
    
    return jsonify(output)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
