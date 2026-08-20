"""
Scraper optimizado para Streamlit.
Extrae datos usando selectores específicos y wait_for.
"""

from playwright.sync_api import sync_playwright
import re


def extract_stats():
    url = "https://football-betting-ai2-xay2ankt3xzaecxpbu6nwf.streamlit.app/"
    
    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=True, 
            args=['--no-sandbox', '--disable-setuid-sandbox']
        )
        page = browser.new_page(viewport={"width": 1280, "height": 900})
        
        print(f"Navegando a {url}...")
        page.goto(url, wait_until="networkidle", timeout=30000)
        
        print("Esperando a que carguen las estadísticas...")
        # Esperar a que aparezca el título de Estadísticas Históricas
        try:
            page.wait_for_selector("text=Estadísticas Históricas", timeout=15000)
            print("✅ Sección de estadísticas encontrada")
        except Exception as e:
            print(f"️ Timeout esperando estadísticas: {e}")
        
        # Pequeña pausa para asegurar renderizado completo
        page.wait_for_timeout(3000)
        
        # === EXTRACCIÓN DE DATOS ===
        stats = {}
        
        # Extraer todo el texto de la página para búsqueda flexible
        try:
            # Usar stMarkdown o stText (selectores de Streamlit)
            all_text = ""
            for selector in ["[data-testid='stMarkdownContainer']", "div.stMarkdown", "div.stText", "body"]:
                try:
                    elements = page.query_selector_all(selector)
                    for el in elements:
                        text = el.inner_text()
                        if text:
                            all_text += text + "\n"
                except:
                    continue
            
            print(f"\n📄 Texto extraído: {len(all_text)} caracteres")
            print("="*60)
            # Mostrar solo las primeras líneas relevantes
            lines = all_text.split('\n')
            for line in lines[:30]:  # Primeras 30 líneas
                if any(keyword in line.lower() for keyword in ['total', 'liquidados', 'acierto', 'error', 'hit', 'pnl', 'yield', 'ev']):
                    print(f"  {line.strip()}")
            print("="*60 + "\n")
            
        except Exception as e:
            print(f"Error extrayendo texto: {e}")
            all_text = ""
        
        # === PARSEO DE DATOS ===
        
        # Total Picks
        match = re.search(r"Total\s*Picks\s*[:\s]*(\d+)", all_text, re.IGNORECASE)
        stats["total_picks"] = int(match.group(1)) if match else None
        
        # Liquidados
        match = re.search(r"Liquidados\s*[:\s]*(\d+)", all_text, re.IGNORECASE)
        stats["liquidados"] = int(match.group(1)) if match else None
        
        # Aciertos
        match = re.search(r"(?:✅\s*)?Aciertos\s*[:\s]*(\d+)", all_text, re.IGNORECASE)
        stats["aciertos"] = int(match.group(1)) if match else None
        
        # Errores  
        match = re.search(r"(?:\s*)?Errores?\s*[:\s]*(\d+)", all_text, re.IGNORECASE)
        stats["errores"] = int(match.group(1)) if match else None
        
        # Hit Rate
        match = re.search(r"Hit\s*Rate\s*[:\s]*([\d.]+)\s*%", all_text, re.IGNORECASE)
        stats["hit_rate"] = float(match.group(1)) if match else None
        
        # PnL (puede tener formato: -16.52 u o -16.52u)
        match = re.search(r"PnL\s*[:\s]*([-+]?\d+\.?\d*)\s*u", all_text, re.IGNORECASE)
        stats["pnl"] = float(match.group(1)) if match else None
        
        # Yield
        match = re.search(r"Yield\s*[:\s]*([-+]?\d+\.?\d*)\s*%", all_text, re.IGNORECASE)
        stats["yield"] = float(match.group(1)) if match else None
        
        # EV medio
        match = re.search(r"EV\s*medio.*?([-+]?\d+\.?\d*)\s*%", all_text, re.IGNORECASE | re.DOTALL)
        stats["ev_medio"] = float(match.group(1)) if match else None
        
        # Sobreestimación (buscar "SOBREESTIMA" o "sobreestima")
        match = re.search(r"SOBREESTIMA.*?([-+]?\d+\.?\d*)\s*pp", all_text, re.IGNORECASE)
        stats["sobreestimacion"] = float(match.group(1)) if match else None
        
        # CLV medio
        match = re.search(r"CLV\s*medio\s*[:\s]*([-+]?\d+\.?\d*)\s*%", all_text, re.IGNORECASE)
        stats["clv_medio"] = float(match.group(1)) if match else None
        
        browser.close()
    
    print("\n📊 RESULTADOS DE EXTRACCIÓN:")
    print("="*60)
    for key, value in stats.items():
        status = "✅" if value is not None else "❌"
        print(f"  {status} {key}: {value}")
    print("="*60)
    
    # Verificar cuántos datos se extrajeron
    extracted_count = sum(1 for v in stats.values() if v is not None)
    print(f"\n Éxito: {extracted_count}/{len(stats)} datos extraídos")
    
    return stats


if __name__ == "__main__":
    stats = extract_stats()
    print("\nDiccionario final:")
    print(stats)
