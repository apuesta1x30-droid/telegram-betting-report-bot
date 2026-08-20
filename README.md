# 🤖 Telegram Betting Report Bot

Bot automatizado que extrae estadísticas de rendimiento de apuestas deportivas y envía un informe ejecutivo semanal por Telegram.

## Características
- Extracción de datos reales (Web Scraping).
- Cálculo de KPIs críticos: Yield, PnL, CLV y Brecha de Sobreestimación.
- Generación de gráficos de rendimiento.
- Ejecución automática semanal vía GitHub Actions (Domingos 05:00 AM CET).

## Configuración de Secretos
Debes añadir en GitHub (Settings > Secrets and variables > Actions):
- `TELEGRAM_BOT_TOKEN`: Tu token de @BotFather
- `TELEGRAM_CHAT_ID`: Tu ID de chat de Telegram
