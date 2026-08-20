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
        page.wait_for_timeout(8000)  # Más tiempo para asegurar carga
        
        # Extraer todo el texto visible de la página
        full_text = page.inner_text("body")
        
        browser.close()
    
    # === MODO DEPURACIÓN: Mostrar texto completo ===
    print("\n" + "="*80)
    print("TEXTO CRUDO EXTRAÍDO DE LA WEB:")
    print("="*80)
    print(full_text[:3000])  # Primeros 3000 caracteres
    print("\n" + "="*80)
    print("FIN DEL TEXTO")
    print("="*80 + "\n")
    
    # Parsear los datos con expresiones regulares más flexibles
    stats = {}
    
    # Total Picks - buscar patrones más flexibles
    picks_match = re.search(r"Total\s*Picks\s*[:\s]*(\d+)", full_text, re.IGNORECASE)
    stats["total_picks"] = int(picks_match.group(1)) if picks_match else None
    
    # Liquidados
    liquidados_match = re.search(r"Liquidados\s*[:\s]*(\d+)", full_text, re.IGNORECASE)
    stats["liquidados"] = int(liquidados_match.group(1)) if liquidados_match else None
    
    # Aciertos (con o sin emoji)
    aciertos_match = re.search(r"(?:✅\s*)?Aciertos\s*[:\s]*(\d+)", full_text, re.IGNORECASE)
    stats["aciertos"] = int(aciertos_match.group(1)) if aciertos_match else None
    
    # Errores (con o sin emoji)
    errores_match = re.search(r"(?:\s*)?Errores?\s*[:\s]*(\d+)", full_text, re.IGNORECASE)
    stats["errores"] = int(errores_match.group(1)) if errores_match else None
    
    # Hit Rate
    hitrate_match = re.search(r"Hit\s*Rate\s*[:\s]*([\d.]+)\s*%", full_text, re.IGNORECASE)
    stats["hit_rate"] = float(hitrate_match.group(1)) if hitrate_match else None
    
    # PnL (puede ser negativo o positivo)
    pnl_match = re.search(r"PnL\s*[:\s]*([-+]?\d+\.?\d*)\s*u", full_text, re.IGNORECASE)
    stats["pnl"] = float(pnl_match.group(1)) if pnl_match else None
    
    # Yield
    yield_match = re.search(r"Yield\s*[:\s]*([-+]?\d+\.?\d*)\s*%", full_text, re.IGNORECASE)
    stats["yield"] = float(yield_match.group(1)) if yield_match else None
    
    # EV medio declarado
    ev_match = re.search(r"EV\s*medio.*?([-+]?\d+\.?\d*)\s*%", full_text, re.IGNORECASE | re.DOTALL)
    stats["ev_medio"] = float(ev_match.group(1)) if ev_match else None
    
    # Sobreestimación
    sobreest_match = re.search(r"sobreestima.*?([-+]?\d+\.?\d*)\s*pp", full_text, re.IGNORECASE)
    stats["sobreestimacion"] = float(sobreest_match.group(1)) if sobreest_match else None
    
    # CLV medio
    clv_match = re.search(r"CLV\s*medio\s*[:\s]*([-+]?\d+\.?\d*)\s*%", full_text, re.IGNORECASE)
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
