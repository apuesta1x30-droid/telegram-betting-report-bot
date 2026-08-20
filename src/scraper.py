"""
Scraper para extraer estadísticas de la web de Streamlit.
Usa Playwright para renderizar la página y extraer los datos dinámicos.
"""

from playwright.sync_api import sync_playwright
import re


def extract_stats():
    """
    Extrae las estadísticas principales de la web de apuestas.
    
    Returns:
        dict: Diccionario con los KPIs extraídos.
    """
    url = "https://football-betting-ai2-xay2ankt3xzaecxpbu6nwf.streamlit.app/"
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        
        print(f"Navegando a {url}...")
        page.goto(url, wait_until="networkidle")
        
        # Esperar a que Streamlit cargue completamente el contenido
        print("Esperando carga completa de Streamlit...")
        page.wait_for_timeout(5000)
        
        # Extraer todo el texto visible de la página
        full_text = page.inner_text("body")
        
        browser.close()
    
    # Parsear los datos con expresiones regulares
    stats = {}
    
    # Total Picks
    picks_match = re.search(r"Total Picks\s*(\d+)", full_text)
    stats["total_picks"] = int(picks_match.group(1)) if picks_match else None
    
    # Liquidados
    liquidados_match = re.search(r"Liquidados\s*(\d+)", full_text)
    stats["liquidados"] = int(liquidados_match.group(1)) if liquidados_match else None
    
    # Aciertos
    aciertos_match = re.search(r"✅?\s*Aciertos\s*(\d+)", full_text)
    stats["aciertos"] = int(aciertos_match.group(1)) if aciertos_match else None
    
    # Errores
    errores_match = re.search(r"❌?\s*Errores\s*(\d+)", full_text)
    stats["errores"] = int(errores_match.group(1)) if errores_match else None
    
    # Hit Rate
    hitrate_match = re.search(r"Hit Rate\s*([\d.]+)%", full_text)
    stats["hit_rate"] = float(hitrate_match.group(1)) if hitrate_match else None
    
    # PnL
    pnl_match = re.search(r"PnL\s*([-+]?\d+\.?\d*)\s*u", full_text)
    stats["pnl"] = float(pnl_match.group(1)) if pnl_match else None
    
    # Yield
    yield_match = re.search(r"Yield\s*([-+]?\d+\.?\d*)%", full_text)
    stats["yield"] = float(yield_match.group(1)) if yield_match else None
    
    # EV medio declarado
    ev_match = re.search(r"EV medio.*?([-+]?\d+\.?\d*)%", full_text)
    stats["ev_medio"] = float(ev_match.group(1)) if ev_match else None
    
    # Sobreestimación
    sobreest_match = re.search(r"sobreestima.*?([-+]?\d+\.?\d*)\s*pp", full_text, re.IGNORECASE)
    stats["sobreestimacion"] = float(sobreest_match.group(1)) if sobreest_match else None
    
    # CLV medio
    clv_match = re.search(r"CLV medio\s*([-+]?\d+\.?\d*)%", full_text)
    stats["clv_medio"] = float(clv_match.group(1)) if clv_match else None
    
    print("Extracción completada:")
    for key, value in stats.items():
        print(f"  {key}: {value}")
    
    return stats


if __name__ == "__main__":
    # Prueba local del scraper
    stats = extract_stats()
    print("\nResultado final:")
    print(stats)
