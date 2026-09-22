"""Smoke test real da interface. Requer a API e o Vite em execução."""
import json
import os
from pathlib import Path
from playwright.sync_api import sync_playwright, expect

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "tmp" / "ui"
OUT.mkdir(parents=True, exist_ok=True)

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True, channel=os.getenv("BROWSER_CHANNEL", "msedge" if os.name == "nt" else "chromium"))
    page = browser.new_page(viewport={"width": 1440, "height": 1080}, device_scale_factor=1)
    errors = []
    page.on("pageerror", lambda e: errors.append(str(e)))
    page.goto(os.getenv("APP_URL", "http://127.0.0.1:5173"), wait_until="networkidle")
    expect(page.get_by_role("heading", name="Visão geral.")).to_be_visible()
    page.screenshot(path=str(OUT / "overview-empty.png"), full_page=True)
    page.get_by_role("button", name="Carregar exemplos", exact=True).click()
    expect(page.get_by_role("button", name="D&O Essencial").first).to_be_visible()
    page.get_by_role("button", name="Fechar notificação").click()
    page.evaluate("window.scrollTo(0, 0)")
    page.wait_for_timeout(200)
    page.screenshot(path=str(OUT / "overview.png"), full_page=True)
    page.get_by_role("checkbox", name="Selecionar D&O Essencial").check()
    page.get_by_role("checkbox", name="Selecionar D&O Ampliada").check()
    page.locator(".selection-bar").get_by_role("button", name="Comparar apólices").click()
    expect(page.locator(".comparison-table")).to_be_visible()
    expect(page.locator(".comparison-table tbody tr")).to_have_count(16)
    page.screenshot(path=str(OUT / "comparison.png"), full_page=True)
    page.get_by_label("Só diferenças e ausências").check()
    expect(page.locator(".comparison-table tbody tr")).to_have_count(10)
    page.locator(".evidence-cell").filter(has_text="15.000.000").click()
    expect(page.get_by_role("dialog")).to_be_visible()
    expect(page.locator(".quote-card")).to_contain_text("15.000.000")
    page.screenshot(path=str(OUT / "evidence.png"), full_page=True)
    page.keyboard.press("Escape")
    expect(page.get_by_role("dialog")).to_have_count(0)
    with page.expect_download() as download:
        page.get_by_role("link", name="Exportar PDF").click()
    download.value.save_as(str(OUT / "comparison.pdf"))
    assert (OUT / "comparison.pdf").read_bytes().startswith(b"%PDF")
    page.get_by_role("button", name="Histórico", exact=True).click()
    expect(page.locator(".history-item").first).to_be_visible()
    page.get_by_role("button", name="Apólices", exact=False).first.click()
    # Select the navigation item precisely to avoid other comparison buttons.
    page.locator("nav").get_by_role("button", name="Apólices", exact=False).first.click()
    page.get_by_placeholder("Buscar apólice ou seguradora…").fill("Aurora")
    expect(page.locator(".policy-table tbody tr")).to_have_count(1)
    page.get_by_placeholder("Buscar apólice ou seguradora…").fill("nada-encontrado")
    expect(page.get_by_text("Nenhuma apólice encontrada")).to_be_visible()
    page.get_by_role("button", name="Nova análise").click()
    expect(page.get_by_role("button", name="Analisar documentos")).to_be_disabled()
    page.keyboard.press("Escape")
    page.get_by_role("button", name="Visão geral", exact=True).click()
    # Axe catches accessibility regressions in the actual rendered DOM.
    axe_path = ROOT / "node_modules" / "axe-core" / "axe.min.js"
    if axe_path.exists():
        page.add_script_tag(path=str(axe_path))
        result = page.evaluate("async () => await axe.run(document, {runOnly: {type:'tag', values:['wcag2a','wcag2aa','wcag21aa']}})")
        (OUT / "accessibility.json").write_text(json.dumps(result["violations"], ensure_ascii=False, indent=2), encoding="utf-8")
        print("Accessibility:", [(v["id"], len(v["nodes"])) for v in result["violations"]])
        assert not result["violations"], "Há violações de acessibilidade"
    page.get_by_role("button", name="Limpar", exact=True).click()
    page.set_viewport_size({"width": 390, "height": 844})
    page.wait_for_timeout(350)
    page.evaluate("window.scrollTo(0, 0)")
    page.screenshot(path=str(OUT / "mobile.png"), full_page=True)
    assert page.evaluate("document.documentElement.scrollWidth <= window.innerWidth"), "Overflow na página móvel"
    page.get_by_role("button", name="Abrir navegação").click()
    page.get_by_role("button", name="Configurações", exact=True).click()
    expect(page.get_by_role("heading", name="Configurações.")).to_be_visible()
    page.screenshot(path=str(OUT / "settings-mobile.png"), full_page=True)
    assert not errors, errors
    browser.close()
    print("UI smoke: OK. Desktop, mobile, seleção, comparação, evidência, exportação, histórico e busca.")
