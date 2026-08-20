import os
import re
import logging
from datetime import datetime
from flask import Flask, jsonify
from playwright.sync_api import sync_playwright

# Configurar logs para ver TODO en Render
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

app = Flask(__name__)

def extract_stats():
    url = "https://football-betting-ai2-xay2ankt3xzaecxpbu6nwf.streamlit.app/"
    logging.info(f"🔍 Conectando a {url}...")
    
    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=True,
            args=['--no-sandbox', '--disable-setuid-sandbox', '--disable-gpu']
        )
        context = browser.new_context(
            viewport={"width": 1280, "height": 900},
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )
        page = context.new_page()
        
        try:
            page.goto(url, wait_until="domcontentloaded", timeout=60000)
            logging.info("⏳ Esperando 30 segundos para renderizado de Streamlit...")
            page.wait_for_timeout(30000)
            
            all_text = page.inner_text("body")
            logging.info(f"📝 Longitud del texto extraído: {len(all_text)} caracteres")
            
            # Mostrar un fragmento en los logs para depuración
            if len(all_text) > 500:
                logging.info(f"👀 Muestra del texto: {all_text[200:700]}")
            else:
                logging.warning("⚠️ El texto extraído es muy corto. Posible bloqueo de JS.")
                
            browser.close()
            return all_text
        except Exception as e:
            logging.error(f"❌ Error en Playwright: {e}")
            browser.close()
            return None

def parse_stats(text):
    if not text:
        return None
    
    stats = {}
    patterns = {
        "total_picks": r"Total\s*Picks\s*[:\s]*(\d+)",
        "liquidados": r"Liquidados\s*[:\s]*(\d+)",
        "pendientes": r"Pendientes\s*[:\s]*(\d+)",
        "aciertos": r"(?:✅\s*)?Aciertos\s*[:\s]*(\d+)",
        "errores": r"(?:\s*)?Errores?\s*[:\s]*(\d+)",
        "hit_rate": r"Hit\s*Rate\s*[:\s]*([\d.]+)\s*%",
        "pnl": r"PnL\s*[:\s]*([-+]?\d+\.?\d*)\s*u",
        "yield": r"Yield\s*[:\s]*([-+]?\d+\.?\d*)\s*%",
        "ev_medio": r"EV\s*medio.*?([-+]?\d+\.?\d*)\s*%",
        "sobreestimacion": r"SOBREESTIMA.*?([-+]?\d+\.?\d*)\s*pp",
        "clv_medio": r"CLV\s*medio\s*[:\s]*([-+]?\d+\.?\d*)\s*%"
    }
    
    for key, pattern in patterns.items():
        match = re.search(pattern, text, re.IGNORECASE | (re.DOTALL if key == "ev_medio" else 0))
        if match:
            val = match.group(1)
            stats[key] = float(val) if '.' in val else int(val)
        else:
            stats[key] = None
    return stats

def generate_report(stats):
    if not stats or stats.get('total_picks') is None:
        return "❌ Error: No se pudieron extraer los datos. Revisa los logs de Render."
    
    sobreest = stats.get('sobreestimacion', 0) or 0
    if sobreest > 30:
        recomendacion = "🚨 **CRÍTICO**: Sobreestimación grave. Reducir stake al 25% o pausar."
    elif sobreest > 20:
        recomendacion = "⚠️ **ALERTA**: Sobreestimación alta. Reducir stake al 50%."
    else:
        recomendacion = "✅ **OK**: Modelo razonablemente calibrado."
    
    clv = stats.get('clv_medio', 0) or 0
    clv_status = "✅ Positivo" if clv > 0 else ("⚠️ Negativo leve" if clv > -5 else "❌ Negativo")
    
    return f"""📊 *INFORME SEMANAL - {datetime.now().strftime('%d/%m/%Y')}*

📈 *RENDIMIENTO*
• Picks: {stats.get('total_picks', 'N/A')} (Liquidados: {stats.get('liquidados', 'N/A')})
• Hit Rate: {stats.get('hit_rate', 'N/A')}%
• PnL: {stats.get('pnl', 'N/A')} u | Yield: {stats.get('yield', 'N/A')}%

🎯 *MODELO*
• EV Declarado: {stats.get('ev_medio', 'N/A')}%
• Sobreestimación: +{stats.get('sobreestimacion', 'N/A')} pp
• CLV Medio: {stats.get('clv_medio', 'N/A')}% ({clv_status})

💡 *RECOMENDACIÓN*
{recomendacion}
"""

def send_telegram_report(message):
    bot_token = os.getenv("TELEGRAM_BOT_TOKEN")
    chat_id = os.getenv("TELEGRAM_CHAT_ID")
    
    if not bot_token or not chat_id:
        logging.error("❌ Faltan TELEGRAM_BOT_TOKEN o TELEGRAM_CHAT_ID en Render")
        return False
    
    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    try:
        import requests
        response = requests.post(url, json={
            "chat_id": chat_id,
            "text": message,
            "parse_mode": "Markdown"
        }, timeout=15)
        
        if response.status_code == 200:
            logging.info("✅ Informe enviado a Telegram con éxito")
            return True
        else:
            logging.error(f"❌ Error Telegram API: {response.text}")
            return False
    except Exception as e:
        logging.error(f"❌ Excepción enviando a Telegram: {e}")
        return False

@app.route('/')
def health():
    return jsonify({"status": "ok", "message": "Bot activo"}), 200

@app.route('/trigger', methods=['GET', 'POST'])
def trigger_report():
    logging.info("🚀 Iniciando proceso de informe...")
    text = extract_stats()
    
    if not text or len(text) < 500:
        logging.error("❌ No se extrajo texto válido de la web.")
        send_telegram_report("❌ Error: La web no devolvió datos. Posible bloqueo anti-bot.")
        return jsonify({"status": "error", "message": "Fallo en extracción"}), 500
    
    stats = parse_stats(text)
    logging.info(f"📊 Datos parseados: {stats}")
    
    report = generate_report(stats)
    success = send_telegram_report(report)
    
    if success:
        return jsonify({"status": "success", "message": "Informe enviado"}), 200
    else:
        return jsonify({"status": "error", "message": "Fallo al enviar a Telegram"}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 10000))
    logging.info(f"🚀 Iniciando servidor Flask en el puerto {port}...")
    app.run(host='0.0.0.0', port=port)
