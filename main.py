import os
import json
import logging
import requests
from datetime import datetime

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def load_stats():
    try:
        with open("datos.json", "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        logging.error("❌ No se encontró datos.json. ¿Se ha exportado desde Streamlit?")
        return None
    except Exception as e:
        logging.error(f"❌ Error leyendo datos.json: {e}")
        return None

def generate_report(stats):
    sobreest = float(stats.get('sobreestimacion', 0) or 0)
    if sobreest > 30:
        recomendacion = "🚨 **CRÍTICO**: Sobreestimación grave. Reducir stake al 25%."
    elif sobreest > 20:
        recomendacion = "⚠️ **ALERTA**: Sobreestimación alta. Reducir stake al 50%."
    elif sobreest > 10:
        recomendacion = "🟡 **PRECAUCIÓN**: Ligera sobreestimación."
    else:
        recomendacion = "✅ **OK**: Modelo bien calibrado."
    
    clv = float(stats.get('clv_medio', 0) or 0)
    clv_status = "✅ Positivo" if clv > 0 else ("⚠️ Negativo leve" if clv > -5 else "❌ Negativo")
    
    analisis_extra = ""
    if 'mejor_mercado' in stats:
        analisis_extra = f"\n🏆 Mejor mercado: {stats['mejor_mercado']} (Yield: {stats.get('yield_mejor_mercado', 'N/A')}%)"

    return f"""📊 *INFORME SEMANAL - {datetime.now().strftime('%d/%m/%Y')}*

📈 *RENDIMIENTO GLOBAL*
• Total Picks: {stats.get('total_picks', 'N/A')}
• Liquidados: {stats.get('liquidados', 'N/A')}
• Hit Rate: {stats.get('hit_rate', 'N/A')}%
• PnL: {stats.get('pnl', 'N/A')} u
• Yield: {stats.get('yield', 'N/A')}%

🎯 *CALIDAD DEL MODELO*
• EV Declarado: {stats.get('ev_medio', 'N/A')}%
• Sobreestimación: +{stats.get('sobreestimacion', 'N/A')} pp
• CLV Medio: {stats.get('clv_medio', 'N/A')}% ({clv_status})
• Bate al cierre: {stats.get('bate_cierre_pct', 'N/A')}%

💡 *RECOMENDACIÓN*
{recomendacion}{analisis_extra}

🕒 Actualizado: {stats.get('ultima_actualizacion', 'Desconocida')}
"""

def send_telegram(message):
    bot_token = os.getenv("TELEGRAM_BOT_TOKEN")
    chat_id = os.getenv("TELEGRAM_CHAT_ID")
    
    if not bot_token or not chat_id:
        logging.error("❌ Faltan credenciales de Telegram")
        return False
    
    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    try:
        response = requests.post(url, json={
            "chat_id": chat_id,
            "text": message,
            "parse_mode": "Markdown"
        }, timeout=10)
        
        if response.status_code == 200:
            logging.info("✅ Informe enviado a Telegram")
            return True
        else:
            logging.error(f"❌ Error Telegram: {response.text}")
            return False
    except Exception as e:
        logging.error(f"❌ Excepción: {e}")
        return False

def main():
    logging.info("🚀 Iniciando bot de informes...")
    stats = load_stats()
    
    if not stats:
        send_telegram("❌ Error: No se encontraron datos. Verifica que la app de Streamlit haya exportado `datos.json`")
        return
    
    report = generate_report(stats)
    send_telegram(report)
    logging.info("✅ Proceso completado")

if __name__ == '__main__':
    main()
