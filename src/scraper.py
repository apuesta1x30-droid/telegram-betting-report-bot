"""
Scraper robusto para Streamlit con evasión de detección y tiempos de espera extendidos.
"""

from playwright.sync_api import sync_playwright
import re
import os


def extract_stats():
    url = "https://football-betting-ai2-xay2ankt3xzaecxpbu6nwf.streamlit.app/"
    
    with sync_playwright() as p:
        # 1. Lanzar con argumentos anti-detección
        browser = p.chromium.launch(
            headless=True, 
            args=[
                '--no-sandbox', 
                '--disable-setuid-sandbox',
                '--disable-blink-features=AutomationControlled'
            ]
        )
        
        # 2. Contexto con User-Agent realista de escritorio
        context = browser.new_context(
            viewport={"width": 1280, "height": 900},
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )
        page = context.new_page()
        
        print(f"Navegando a {url}...")
        try:
            # 3. Usar domcontentloaded en lugar de networkidle (Streamlit mantiene websockets abiertos)
            page.goto(url, wait_until="domcontentloaded", timeout=60000)
        except Exception as e:
            print(f"⚠️ Error en la navegación: {e}")
            
        print("⏳ Esperando 30 segundos para que Streamlit renderice el contenido...")
        page.wait_for_timeout(30000)
        
        # === DIAGNÓSTICO VISUAL ===
        screenshot_path = "screenshot.png"
        page.screenshot(path=screenshot_path, full_page=True)
        print(f"📸 Screenshot guardado en: {screenshot_path}")
        
        html_content = page.content()
        print(f"📄 Longitud del HTML: {len(html_content)} caracteres")
        
        if len(html_content) < 3000:
            print("⚠️ ADVERTENCIA CRÍTICA: El HTML es muy corto. JavaScript NO se ejecutó.")
            print("Contenido HTML:")
            print(html_content)
        
        all_text = page.inner_text("body")
        print(f"📝 Longitud del texto extraído: {len(all_text)} caracteres")
        
        print("\n--- Muestra del texto extraído (primeras 30 líneas no vacías) ---")
        lines = [line.strip() for line in all_text.split('\n') if line.strip()]
        for i, line in enumerate(lines[:30]):
            print(f"  {i+1}. {line}")
        print("------------------------------------------------------------------\n")
        
        browser.close()
        
    return all_text


if __name__ == "__main__":
    print("🔍 Iniciando scraper robusto...\n")
    text = extract_stats()
    print("✅ Proceso finalizado. Revisa los artifacts en GitHub Actions.")
