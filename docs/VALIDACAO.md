# Validação do projeto

A suíte automatizada verifica leitura de PDF e imagem, limites de entrada, citações, persistência, retomada por checkpoints, upload em lote, comparação e exportações. Os testes do provedor usam respostas simuladas. Execute os comandos da seção Verificação do README.

## Execução real com IA

Os dois PDFs fictícios de demonstração foram enviados ao Gemini 3.8 Flash em 05/10/2026. Ambos concluíram a extração, com 16 critérios e citações verificadas por documento. A comparação apresentou 10 diferenças entre 16 campos, sem ausências; as exportações PDF e JSON passaram. O registro está em `Projeto_Final_Artefatos/Validacao_IA_Exemplos.json`.

Para repetir o fluxo, execute `python scripts/check_documents.py` com o ambiente virtual ativo e a chave configurada. A execução usa `tmp/document-checks/` e consome a cota da conta. `--preflight-only` verifica apenas leitura e divisão, sem chamada à IA.

## Interface e acessibilidade

Os roteiros opcionais requerem Python Playwright. Instale-o no ambiente virtual:

```bash
python -m pip install playwright
python -m playwright install chromium
```

Inicie uma API separada para que os testes não alterem sua biblioteca. Com o ambiente virtual ativo, em macOS/Linux:

```bash
DATA_DIR=tmp/ui-checks python -m uvicorn backend.app:app --host 127.0.0.1 --port 8003
```

No PowerShell:

```powershell
$env:DATA_DIR = 'tmp/ui-checks'
python -m uvicorn backend.app:app --host 127.0.0.1 --port 8003
```

Em outro terminal, execute ambos os roteiros contra essa API, com a interface compilada por `npm run build`. Em macOS/Linux:

```bash
APP_URL=http://127.0.0.1:8003 python scripts/check_ui.py
APP_URL=http://127.0.0.1:8003 python scripts/check_design.py
```

No PowerShell, defina `$env:APP_URL = 'http://127.0.0.1:8003'` e execute os mesmos comandos `python`. No Windows, os roteiros usam Edge por padrão; defina `BROWSER_CHANNEL=chromium` para usar o navegador instalado pelo Playwright.

`check_ui.py` verifica biblioteca, busca, seleção, comparação, evidências, exportação e histórico. `check_design.py` verifica foco, erros, acessibilidade e telas de 320 a 1440 pixels. Os arquivos de QA ficam em `tmp/`, ignorados pelo Git.

## Entregáveis

`python scripts/check_artifacts.py` verifica DOCX, PPTX, PDF, vídeo e o conteúdo atualizado do ZIP. Requer as dependências do projeto e FFmpeg, instalado por `npm ci`. `python scripts/render_office.py` renderiza todas as páginas do DOCX e os slides com LibreOffice para conferência visual.

A validação funcional demonstra o processamento dos arquivos de exemplo. A presença textual das citações não comprova interpretação contratual correta.
