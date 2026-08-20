"""
Scraper de diagnóstico para la web de Streamlit.
Toma screenshot, extrae HTML y prueba múltiples estrategias.
"""

from playwright.sync_api import sync_playwright
import re
import os


def extract_stats():
    url = "https://football-betting-ai2-xay2ankt3xzaecxpbu6nwf.streamlit.app/"
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True, args=['--no-sandbox', '--disable-setuid-sandbox'])
        page = browser.new_page(viewport={"width": 1280, "height": 900})
        
        print(f"Navegando a {url}...")
        page.goto(url, wait_until="networkidle", timeout=30000)
        
        print("Esperando carga completa...")
        page.wait_for_timeout(10000)
        
        # === DIAGNÓSTICO 1: Captura de pantalla ===
        screenshot_path = "screenshot.png"
        page.screenshot(path=screenshot_path, full_page=True)
        print(f" Screenshot guardado en: {os.path.abspath(screenshot_path)}")
        
        # === DIAGNÓSTICO 2: HTML completo ===
        html_content = page.content()
        html_path = "page.html"
        with open(html_path, "w", encoding="utf-8") as f:
            f.write(html_content)
        print(f"📄 HTML guardado en: {os.path.abspath(html_path)}")
        print(f"   Tamaño del HTML: {len(html_content)} caracteres")
        
        # === DIAGNÓSTICO 3: Texto con diferentes selectores ===
        print("\n--- Prueba de selectores ---")
        
        # Selector 1: body
        text_body = page.inner_text("body")
        print(f"inner_text('body'): {len(text_body)} chars")
        
        # Selector 2: Streamlit container
        try:
            text_st = page.inner_text("[data-testid='stVerticalBlock']")
            print(f"inner_text('stVerticalBlock'): {len(text_st)} chars")
        except Exception as e:
            print(f"stVerticalBlock: {e}")
        
        # Selector 3: Todos los divs
        try:
            text_divs = page.inner_text("div")
            print(f"inner_text('div'): {len(text_divs)} chars")
        except Exception as e:
            print(f"div: {e}")
        
        # Selector 4: Streamlit text elements
        try:
            elements = page.query_selector_all(".stText, .stMarkdown, p, h1, h2, h3, span")
            print(f"Elementos de texto encontrados: {len(elements)}")
            for i, el in enumerate(elements[:10]):
                txt = el.inner_text()
                if txt.strip():
                    print(f"  [{i}] {txt[:100]}")
        except Exception as e:
            print(f"query_selector_all: {e}")
        
        # === DIAGNÓSTICO 4: Título de la página ===
        title = page.title()
        print(f"\n📌 Título de la página: '{title}'")
        
        # === DIAGNÓSTICO 5: URL actual ===
        print(f"📌 URL actual: {page.url}")
        
        browser.close()
    
    return {"screenshot": screenshot_path, "html": html_path}


if __name__ == "__main__":
    print("🔍 Iniciando scraper de diagnóstico...\n")
    result = extract_stats()
    print("\n✅ Diagnóstico completado")
