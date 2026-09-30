"""Verifica estados, foco e telas responsivas. Requer a API e o Vite locais."""
import json
import os
from pathlib import Path
from playwright.sync_api import sync_playwright, expect

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "tmp" / "design-review"
OUT.mkdir(parents=True, exist_ok=True)

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True, channel=os.getenv("BROWSER_CHANNEL", "msedge" if os.name == "nt" else "chromium"))
    page = browser.new_page(viewport={"width": 1440, "height": 1000})
    errors = []
    page.on("pageerror", lambda error: errors.append(str(error)))
    url = os.getenv("APP_URL", "http://127.0.0.1:5173")
    checks = {}

    def capture(name, full=False):
        page.evaluate("document.fonts.ready")
        page.wait_for_timeout(250)
        assert page.evaluate("document.documentElement.scrollWidth <= innerWidth"), name
        page.screenshot(path=str(OUT / f"{name}.png"), full_page=full)
        page.add_script_tag(path=str(ROOT / "node_modules/axe-core/axe.min.js"))
        violations = page.evaluate("async () => (await axe.run(document, {runOnly:{type:'tag',values:['wcag2a','wcag2aa','wcag21aa']}})).violations")
        checks[name] = violations

    page.goto(url, wait_until="networkidle")
    page.get_by_role("button", name="Carregar exemplos", exact=True).click()
    expect(page.get_by_role("button", name="D&O Essencial").first).to_be_visible()
    page.get_by_role("button", name="Fechar notificação").click()
    capture("desktop")

    trigger = page.get_by_role("button", name="Nova análise", exact=True)
    trigger.click()
    dialog = page.get_by_role("dialog", name="Nova análise")
    expect(dialog).to_be_visible()
    capture("upload-desktop")
    page.locator('input[type="file"]').set_input_files({"name":"invalido.txt","mimeType":"text/plain","buffer":b"invalid"})
    expect(dialog.get_by_role("alert")).to_contain_text("Use arquivos PDF")
    capture("upload-error")
    page.keyboard.press("Escape")
    expect(trigger).to_be_focused()

    page.get_by_role("checkbox", name="Selecionar D&O Essencial").check()
    page.get_by_role("checkbox", name="Selecionar D&O Ampliada").check()
    page.locator(".selection-bar").get_by_role("button", name="Comparar apólices").click()
    expect(page.locator(".comparison-table")).to_be_visible()
    capture("comparison-desktop")
    evidence = page.locator(".evidence-cell").filter(has_text="15.000.000")
    evidence.click()
    expect(page.get_by_role("dialog")).to_be_visible()
    capture("evidence-desktop")
    page.keyboard.press("Escape")
    expect(evidence).to_be_focused()

    page.set_viewport_size({"width": 390, "height": 844})
    page.evaluate("window.scrollTo(0,0)")
    capture("comparison-mobile")
    page.get_by_role("button", name="Abrir navegação").click()
    nav = page.get_by_role("dialog", name="Navegação")
    expect(nav).to_be_visible()
    capture("navigation-mobile")
    for _ in range(12):
        page.keyboard.press("Tab")
        assert nav.evaluate("node => node.contains(document.activeElement)")
    page.keyboard.press("Escape")
    expect(page.get_by_role("button", name="Abrir navegação")).to_be_focused()
    page.get_by_role("button", name="Abrir navegação").click()
    page.get_by_role("dialog").get_by_role("button", name="Visão geral", exact=True).click()
    expect(nav).to_have_count(0)
    page.get_by_role("button", name="Limpar", exact=True).click()
    capture("mobile", full=True)
    page.get_by_role("button", name="Nova análise", exact=True).click()
    capture("upload-mobile")
    page.keyboard.press("Escape")

    for width in (320, 768, 1024):
        page.set_viewport_size({"width": width, "height": 900})
        capture(f"overview-{width}")

    # Empty and failure states are simulated only for UI validation.
    page.set_viewport_size({"width": 1440, "height": 1000})
    page.route("**/api/policies", lambda route: route.fulfill(json=[]))
    page.reload(wait_until="networkidle")
    capture("desktop-empty")
    page.unroute("**/api/policies")
    page.route("**/api/policies", lambda route: route.fulfill(status=503, json={"error":"Não foi possível carregar os documentos. Tente novamente."}))
    page.reload(wait_until="networkidle")
    capture("connection-error")
    (OUT / "accessibility.json").write_text(json.dumps(checks, ensure_ascii=False, indent=2), encoding="utf-8")
    failures = {name: [v["id"] for v in found] for name, found in checks.items() if found}
    assert not failures, failures
    assert not errors, errors
    browser.close()
    print(f"Design: {len(checks)} estados/tamanhos, acessibilidade, Escape e foco aprovados.")
