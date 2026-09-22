# InsurMinds

Plataforma de análise e comparação de apólices D&O com IA generativa, desenvolvida para o Projeto Final do Instituto de Inteligência Artificial Aplicada (I2A2), turma 2026.

O MVP recebe PDFs ou imagens, extrai 16 critérios com referências à origem, armazena os resultados e compara de duas a quatro apólices. A interface oferece busca, consulta contextual com IA, histórico e exportação de relatório PDF e dados JSON.

## Execução rápida

Requisitos: Node.js 24 e Python 3.14, versões usadas na validação. A extração real requer chave e cota na API do Google Gemini. O modo de exemplos funciona sem chave e utiliza documentos fictícios com resultados pré-preenchidos; ele não cumpre, sozinho, o requisito de processamento por IA generativa.

```powershell
npm install
py -3.14 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
Copy-Item .env.example .env
```

Preencha `GEMINI_API_KEY` em `.env`. Nunca coloque a chave no frontend ou no Git. O modelo padrão é `gemini-3.6-flash`, alterável por `GEMINI_MODEL`. Reinicie a API após editar o ambiente.

No primeiro terminal:

```powershell
.\.venv\Scripts\python.exe -m uvicorn backend.app:app --host 127.0.0.1 --port 8001
```

No segundo terminal:

```powershell
npm run dev
```

Acesse http://127.0.0.1:5173. Em Linux/macOS, substitua `py -3.14` por `python3`, use `.venv/bin/python` e `cp .env.example .env`.

Para executar apenas um servidor após compilar:

```powershell
npm run build
.\.venv\Scripts\python.exe -m uvicorn backend.app:app --host 127.0.0.1 --port 8001
```

Nesse modo, acesse http://127.0.0.1:8001. O backend serve o conteúdo de `dist/` quando essa pasta existe no início do processo. Use um único worker neste MVP.

## Demonstração

1. Clique em **Carregar exemplos** na visão geral. Os documentos Aurora e Vértice são fictícios, claramente identificados e não representam ofertas de seguro.
2. Selecione ambas as apólices e clique em **Comparar apólices**.
3. Ative o filtro de diferenças, abra o limite de responsabilidade e confira o trecho e a página.
4. Exporte o PDF e retome o resultado pelo histórico.
5. Para demonstrar IA real, configure a chave, use **Nova análise** e envie os PDFs de `Projeto_Final_Artefatos/exemplos/`. O upload cria novas análises com chamada ao modelo; carregar exemplos apenas insere fixtures.

Os arquivos ficam em `data/`, junto ao SQLite. Eles persistem ao reiniciar. O conteúdo enviado para extração e consulta é processado pelo Google Gemini. O MVP é local, sem login e sem isolamento entre usuários; não o exponha publicamente sem adaptar a arquitetura.

## Tecnologias e organização

```text
backend/                  API, documentos, IA, comparação, banco e relatórios
src/                      Interface React, TypeScript e CSS responsivo
tests/                    Testes de leitura, evidências e integração da API
scripts/                  Geração de artefatos e verificação no navegador
docs/                     Arquitetura e roteiro da apresentação
Projeto_Final_Artefatos/  Relatório técnico, pitch, vídeo e exemplos fictícios
.github/workflows/        Verificação automatizada do código
```

Frontend: React 19, TypeScript, Vite, Lucide, DM Sans e Manrope. Backend: Python, Starlette, uvicorn, Pydantic, Google GenAI SDK, PyMuPDF, Pillow e SQLite. IA: Google Gemini GenerateContent com saída JSON estruturada e leitura multimodal. PDFs: ReportLab. Artefatos: PptxGenJS e FFmpeg. As fontes são locais e não dependem de CDN.

Consulte [a arquitetura, decisões e limitações](docs/ARQUITETURA.md). O sistema usa componentes especializados de pipeline, com IA na extração e consulta. A comparação é textual e determinística; igualdade de texto não comprova equivalência jurídica.

## Testes

```powershell
npm run build
.\.venv\Scripts\python.exe -m unittest discover -s tests -v
```

O teste de navegador é opcional e requer os dois servidores em execução:

```powershell
.\.venv\Scripts\python.exe -m pip install playwright
.\.venv\Scripts\python.exe scripts/check_ui.py
```

No Windows, usa Edge em modo sem janela. Em Linux, instale o Chromium com `python -m playwright install chromium`. Capturas e resultados temporários ficam em `tmp/ui/`. Os testes do provedor usam respostas simuladas e não consomem API. A precisão de extração em contratos reais ainda precisa de avaliação por especialistas.

## Entregáveis e situação da entrega

- [Relatório técnico](Projeto_Final_Artefatos/InsurMinds_Relatorio_Tecnico.pdf).
- [Pitch Deck](Projeto_Final_Artefatos/InsurMinds_Projeto_Final.pptx).
- [Vídeo de demonstração](Projeto_Final_Artefatos/InsurMinds_Projeto_Final.mp4).
- [Roteiro e instruções de gravação](docs/ROTEIRO.md).
- Código-fonte e artefatos em `Projeto_Final_Artefatos/InsurMinds_Codigo_Fonte.zip`, gerado por `python scripts/build_delivery.py`.
- Repositório público: https://github.com/vicTmm/i2a2-desafio-final.

A demonstração gravada utiliza exemplos fictícios e identifica essa condição na própria interface. Para apresentar uma execução real de IA, configure `GEMINI_API_KEY`, processe documentos próprios e grave uma nova demonstração. Nenhum resultado simulado deve ser apresentado como execução real de IA.

Prazo informado no enunciado: **06/10/2026 às 23h59**.

## Integrantes

Equipe: **InsurMinds**. Nomes completos dos integrantes: **pendentes de informação da equipe**. Atualizar esta seção antes de entregar.

## Licença

Código-fonte sob [licença MIT](LICENSE). Os exemplos são sintéticos e autorais. Dependências e fontes preservam suas próprias licenças. Não há apólices reais de terceiros incluídas no repositório.
