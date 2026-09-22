"""Grava navegação real com legendas. Os exemplos não representam execução de IA."""
import json
import os
from html import escape
from pathlib import Path
import subprocess
from playwright.sync_api import sync_playwright, expect

ROOT = Path(__file__).resolve().parents[1]
TMP = ROOT / "tmp" / "video"
OUT = ROOT / "Projeto_Final_Artefatos"
TMP.mkdir(parents=True, exist_ok=True)
OUT.mkdir(exist_ok=True)

def slide(page, label, title, body, seconds=10):
    page.set_content(f'''<!doctype html><html lang="pt-BR"><meta charset="utf-8"><style>
    body{{margin:0;background:#f8f9f4;color:#244b3b;font-family:Arial,sans-serif;height:100vh;display:flex;align-items:center;}}
    main{{padding:64px 75px;max-width:1200px;box-sizing:border-box;}}small{{font-size:15px;color:#66755d;letter-spacing:2px;}}h1{{font-size:48px;line-height:1.2;margin:30px 0;letter-spacing:-1px;}}p{{font-size:24px;line-height:1.55;color:#607157;white-space:pre-line;margin:0;}}footer{{position:fixed;bottom:28px;left:75px;font-size:13px;color:#66755d;}}
    </style><main><small>{escape(label)}</small><h1>{escape(title)}</h1><p>{escape(body)}</p></main><footer>InsurMinds / Projeto Final I2A2 2026</footer></html>''')
    page.wait_for_timeout(seconds * 1000)

def caption(page, title, body, seconds=9):
    page.evaluate('''([title,body])=>{document.getElementById('video-caption')?.remove();const n=document.createElement('aside');n.id='video-caption';n.setAttribute('popover','manual');n.style.cssText='position:fixed;inset:auto 20px 15px 260px;margin:0;border:0;width:auto;max-width:none;background:#183d32;color:white;padding:18px 22px;border-radius:9px;box-shadow:0 8px 30px #0002;font-family:Arial,sans-serif;pointer-events:none';const a=document.createElement('strong');a.textContent=title;a.style.cssText='font-size:18px;display:block;margin-bottom:8px';const b=document.createElement('div');b.textContent=body;b.style.cssText='font-size:15px;line-height:1.5;color:#e5efd9';n.append(a,b);document.body.append(n);n.showPopover()}''', [title,body])
    page.wait_for_timeout(seconds * 1000)

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True, channel=os.getenv("BROWSER_CHANNEL", "msedge" if os.name == "nt" else "chromium"))
    context = browser.new_context(viewport={"width":1280,"height":800}, record_video_dir=str(TMP), record_video_size={"width":1280,"height":800})
    page = context.new_page()
    video = page.video
    slide(page,"INSURMINDS / D&O","Clareza na comparação de apólices","Uma plataforma para organizar informações, identificar diferenças e conferir a origem de cada dado.",9)
    slide(page,"O PROBLEMA","Os detalhes mudam a análise","Limites, franquias, coberturas e exclusões precisam ser lidos em conjunto. Localizar cada condição é parte essencial da comparação.",11)
    slide(page,"ARQUITETURA","Interface simples. Processamento especializado.","React → API Python → leitura de PDF ou imagem\nOpenAI + validação → SQLite → comparação e PDF\n\nIA na extração e consulta. Comparação textual reproduzível.",13)
    page.goto('http://127.0.0.1:5173',wait_until='networkidle')
    expect(page.get_by_role('heading',name='Visão geral.')).to_be_visible()
    caption(page,'A plataforma em funcionamento','A biblioteca organiza documentos, acompanha análises e mantém as comparações no histórico.',8)
    page.get_by_role('button',name='Carregar exemplos',exact=True).click()
    expect(page.get_by_role('button',name='D&O Essencial').first).to_be_visible()
    if page.get_by_role('button',name='Fechar notificação').count():
        page.get_by_role('button',name='Fechar notificação').click()
    page.locator('nav').get_by_role('button',name='Apólices',exact=False).first.click()
    caption(page,'Exemplos fictícios identificados','Aurora e Vértice são documentos autorais. Os dados estão pré-preenchidos e não representam uma chamada real de IA.',11)
    page.get_by_role('checkbox',name='Selecionar D&O Essencial').check()
    page.get_by_role('checkbox',name='Selecionar D&O Ampliada').check()
    page.evaluate("document.getElementById('video-caption')?.remove()")
    page.wait_for_timeout(2000)
    page.locator('.selection-bar').get_by_role('button',name='Comparar apólices').click()
    expect(page.locator('.comparison-table')).to_be_visible()
    caption(page,'16 critérios, lado a lado','A tabela apresenta identificação, condições, coberturas e exclusões. Cada informação mantém sua referência de origem.',10)
    page.get_by_label('Só diferenças e ausências').check()
    page.locator('.evidence-cell').filter(has_text='15.000.000').scroll_into_view_if_needed()
    caption(page,'10 diferenças textuais nos exemplos','Os limites são R$ 10 milhões e R$ 15 milhões. Os valores precisam ser interpretados com as franquias e demais condições.',11)
    page.locator('.evidence-cell').filter(has_text='15.000.000').click()
    expect(page.locator('.quote-card')).to_be_visible()
    caption(page,'Evidência na página do documento','O trecho confirma a origem do valor. Presença textual não comprova interpretação jurídica correta.',10)
    page.wait_for_timeout(1000)
    page.keyboard.press('Escape')
    page.evaluate("document.getElementById('video-caption')?.remove()")
    page.get_by_role('link',name='Exportar PDF').scroll_into_view_if_needed()
    with page.expect_download() as download:
        page.get_by_role('link',name='Exportar PDF').click()
    download.value.save_as(str(TMP/'comparacao-demo.pdf'))
    caption(page,'Relatório comparativo em PDF','O arquivo reúne os valores, os trechos citados e as limitações. A mesma comparação também pode ser exportada em JSON.',10)
    page.get_by_role('button',name='Histórico',exact=True).click()
    caption(page,'Histórico persistente','As comparações ficam no SQLite e podem ser retomadas depois de reiniciar o aplicativo.',8)
    page.get_by_role('button',name='Visão geral',exact=True).click()
    page.get_by_role('button',name='Nova análise',exact=True).click()
    caption(page,'Recebimento de novos documentos','O upload aceita PDF, PNG, JPG e WebP. A extração real exige uma chave OpenAI configurada no servidor.',11)
    page.keyboard.press('Escape')
    page.get_by_role('button',name='Configurações',exact=True).click()
    caption(page,'Validação com IA ainda pendente','Esta gravação demonstra a interface com exemplos. A chamada real ao modelo depende da credencial da equipe.',10)
    slide(page,'RESULTADOS E EVOLUÇÃO','Um MVP verificável','18 testes automatizados aprovados. Fluxo de interface validado em desktop e celular.\n\nPróximos passos: testar a IA com documentos reais, revisar com especialistas e concluir a publicação do repositório.',13)
    awaitable_path = video.path()
    context.close()
    browser.close()
    source=Path(awaitable_path)

ffmpeg=ROOT/'node_modules'/'ffmpeg-static'/('ffmpeg.exe' if os.name=='nt' else 'ffmpeg')
target=OUT/'InsurMinds_Projeto_Final.mp4'
subprocess.run([str(ffmpeg),'-y','-i',str(source),'-c:v','libx264','-preset','fast','-crf','21','-pix_fmt','yuv420p','-movflags','+faststart','-an',str(target)],check=True,stdout=subprocess.DEVNULL,stderr=subprocess.PIPE)
print(f'Vídeo gerado: {target.name} ({target.stat().st_size/1024/1024:.1f} MB)',flush=True)
