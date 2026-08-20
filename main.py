"""
Bot de informes semanales para Telegram.
Extrae estadísticas de la web de Streamlit y envía un informe ejecutivo.
Se ejecuta semanalmente vía cron job en Render.
"""

from playwright.sync_api import sync_playwright
import requests
import os
from datetime import datetime
import re


def extract_stats():
    """Extrae las estadísticas de la web de Streamlit"""
    url = "https://football-betting-ai2-xay2ankt3xzaecxpbu6nwf.streamlit.app/"
    
    print(f"🔍 Conectando a {url}...")
    
    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=True,
            args=['--no-sandbox', '--disable-setuid-sandbox']
        )
        context = browser.new_context(
            viewport={"width": 1280, "height": 900},
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        )
        page = context.new_page()
        
        try:
            page.goto(url, wait_until="domcontentloaded", timeout=60000)
            print("⏳ Esperando renderizado completo...")
            page.wait_for_timeout(30000)
            
            all_text = page.inner_text("body")
            browser.close()
            return all_text
            
        except Exception as e:
            print(f"❌ Error: {e}")
            browser.close()
            return None


def parse_stats(text):
    """Parsea el texto extraído y devuelve un diccionario de estadísticas"""
    if not text:
        return None
    
    stats = {}
    
    # Total Picks
    match = re.search(r"Total\s*Picks\s*[:\s]*(\d+)", text, re.IGNORECASE)
    stats["total_picks"] = int(match.group(1)) if match else None
    
    # Liquidados
    match = re.search(r"Liquidados\s*[:\s]*(\d+)", text, re.IGNORECASE)
    stats["liquidados"] = int(match.group(1)) if match else None
    
    # Pendientes
    match = re.search(r"Pendientes\s*[:\s]*(\d+)", text, re.IGNORECASE)
    stats["pendientes"] = int(match.group(1)) if match else None
    
    # Aciertos
    match = re.search(r"(?:✅\s*)?Aciertos\s*[:\s]*(\d+)", text, re.IGNORECASE)
    stats["aciertos"] = int(match.group(1)) if match else None
    
    # Errores
    match = re.search(r"(?:\s*)?Errores?\s*[:\s]*(\d+)", text, re.IGNORECASE)
    stats["errores"] = int(match.group(1)) if match else None
    
    # Hit Rate
    match = re.search(r"Hit\s*Rate\s*[:\s]*([\d.]+)\s*%", text, re.IGNORECASE)
    stats["hit_rate"] = float(match.group(1)) if match else None
    
    # PnL
    match = re.search(r"PnL\s*[:\s]*([-+]?\d+\.?\d*)\s*u", text, re.IGNORECASE)
    stats["pnl"] = float(match.group(1)) if match else None
    
    # Yield
    match = re.search(r"Yield\s*[:\s]*([-+]?\d+\.?\d*)\s*%", text, re.IGNORECASE)
    stats["yield"] = float(match.group(1)) if match else None
    
    # EV medio
    match = re.search(r"EV\s*medio.*?([-+]?\d+\.?\d*)\s*%", text, re.IGNORECASE | re.DOTALL)
    stats["ev_medio"] = float(match.group(1)) if match else None
    
    # Sobreestimación
    match = re.search(r"SOBREESTIMA.*?([-+]?\d+\.?\d*)\s*pp", text, re.IGNORECASE)
    stats["sobreestimacion"] = float(match.group(1)) if match else None
    
    # CLV medio
    match = re.search(r"CLV\s*medio\s*[:\s]*([-+]?\d+\.?\d*)\s*%", text, re.IGNORECASE)
    stats["clv_medio"] = float(match.group(1)) if match else None
    
    return stats


def generate_report(stats):
    """Genera el mensaje de informe ejecutivo"""
    if not stats:
        return "❌ Error: No se pudieron extraer los datos."
    
    # Calcular recomendación basada en sobreestimación
    sobreest = stats.get('sobreestimacion', 0)
    if sobreest > 30:
        recomendacion = " **CRÍTICO**: El modelo sobreestima gravemente. Suspender apuestas o reducir stake al 25%."
    elif sobreest > 20:
        recomendacion = " **ALERTA**: Sobreestimación alta. Reducir stake al 50% hasta mejorar calibración."
    elif sobreest > 10:
        recomendacion = "🟡 **PRECAUCIÓN**: Ligera sobreestimación. Mantener stakes conservadores."
    else:
        recomendacion = " **OK**: El modelo está razonablemente calibrado."
    
    # Calificar CLV
    clv = stats.get('clv_medio', 0)
    if clv > 0:
        clv_status = "✅ Positivo (batas al mercado)"
    elif clv > -5:
        clv_status = "⚠️ Ligeramente negativo"
    else:
        clv_status = "❌ Negativo (no bates al mercado)"
    
    # Formatear mensaje
    report = f""" *INFORME SEMANAL - {datetime.now().strftime('%d/%m/%Y')}*

📈 *RENDIMIENTO ACUMULADO*
• Total Picks: {stats.get('total_picks', 'N/A')}
• Liquidados: {stats.get('liquidados', 'N/A')}
• Pendientes: {stats.get('pendientes', 'N/A')}
• ✅ Aciertos: {stats.get('aciertos', 'N/A')}
• ❌ Errores: {stats.get('errores', 'N/A')}

 *MÉTRICAS CLAVE*
• Hit Rate: {stats.get('hit_rate', 'N/A')}%
• PnL: {stats.get('pnl', 'N/A')} u
• Yield: {stats.get('yield', 'N/A')}%

🎯 *ANÁLISIS DEL MODELO*
• EV Declarado: {stats.get('ev_medio', 'N/A')}%
• Sobreestimación: +{stats.get('sobreestimacion', 'N/A')} pp
• CLV Medio: {stats.get('clv_medio', 'N/A')}% ({clv_status})

💡 *RECOMENDACIÓN*
{recomendacion}

 *PRÓXIMOS PASOS*
1. Revisar calibración del modelo
2. Ajustar stakes según recomendación
3. Monitorear CLV semanalmente
"""
    return report


def send_telegram_report(message):
    """Envía el informe a Telegram"""
    bot_token = os.getenv("TELEGRAM_BOT_TOKEN")
    chat_id = os.getenv("TELEGRAM_CHAT_ID")
    
    if not bot_token or not chat_id:
        print("❌ Error: TELEGRAM_BOT_TOKEN o TELEGRAM_CHAT_ID no configurados")
        return False
    
    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    
    try:
        response = requests.post(url, json={
            "chat_id": chat_id,
            "text": message,
            "parse_mode": "Markdown"
        }, timeout=10)
        
        if response.status_code == 200:
            print("✅ Informe enviado correctamente a Telegram")
            return True
        else:
            print(f"❌ Error en Telegram API: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error enviando a Telegram: {e}")
        return False


def main():
    """Función principal"""
    print("🚀 Iniciando bot de informes semanales...")
    
    # 1. Extraer datos
    text = extract_stats()
    if not text:
        send_telegram_report("❌ Error: No se pudo conectar con la web de estadísticas.")
        return
    
    # 2. Parsear estadísticas
    stats = parse_stats(text)
    
    # 3. Generar informe
    report = generate_report(stats)
    
    # 4. Enviar a Telegram
    send_telegram_report(report)
    
    print("✅ Proceso completado")


if __name__ == "__main__":
    main()
