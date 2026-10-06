# InsurMinds

Plataforma de análise e comparação de apólices D&O com IA generativa, desenvolvida para o Projeto Final do Instituto de Inteligência Artificial Aplicada (I2A2), turma 2026.

O MVP recebe PDFs ou imagens, extrai 16 critérios com referências às páginas de origem, armazena os resultados e compara de duas a quatro apólices. Também oferece busca, consulta contextual com IA, histórico e exportação para PDF e JSON.

## Execução rápida

Requisitos: Node.js 24 e Python 3.14, versões usadas na validação. O modo de exemplos funciona sem chave e carrega documentos fictícios com resultados pré-preenchidos. Para analisar um arquivo com Gemini, configure uma chave de API.

```powershell
npm install
py -3.14 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
Copy-Item .env.example .env
```

### Como obter e configurar a chave Gemini

Abra o [Google AI Studio](https://aistudio.google.com/api-keys) e consulte a área de chaves de API. Se a chave anterior não estiver disponível para cópia, crie uma nova. Nesta cópia do projeto não há arquivo `.env` configurado; depois de copiá-lo do exemplo, preencha `GEMINI_API_KEY` no `.env` local. Mantenha a chave no servidor: não a inclua no frontend, no Git ou em mensagens. O `.env` é ignorado pelo Git.

O modelo padrão é `gemini-3.8-flash` e pode ser alterado com `GEMINI_MODEL`. Em indisponibilidade temporária, o pipeline tenta `gemini-3.7-flash`, configurável por `GEMINI_FALLBACK_MODELS` (lista separada por vírgulas; vazio desativa). Use modelos disponíveis na faixa gratuita da sua conta. As cotas continuam valendo; a aplicação não ativa faturamento nem garante disponibilidade. Reinicie a API após mudar o ambiente.

PDFs de até 300 páginas e 20 MB são analisados em blocos de até 60 mil caracteres, 20 páginas e 4 páginas visuais por chamada, mantendo os números originais. O limite total é de 2 milhões de caracteres. Os blocos concluídos ficam salvos em `data/checkpoints/`; **Tentar novamente** reaproveita esses resultados após uma falha ou reinício. Alterações no conteúdo, prompt, schema ou modelos invalidam o cache correspondente. Há três tentativas por modelo para erros transitórios, timeout de 90 segundos por chamada e intervalo mínimo padrão de 15 segundos entre chamadas (`GEMINI_REQUEST_INTERVAL`). Ajuste o intervalo conforme as cotas da conta.

Os critérios podem reunir várias evidências. Formulações distintas entre blocos são preservadas e sinalizadas para revisão; a ferramenta não escolhe automaticamente qual condição prevalece. O envio de vários arquivos continua mesmo quando um deles é rejeitado.

No primeiro terminal:

```powershell
.\.venv\Scripts\python.exe -m uvicorn backend.app:app --host 127.0.0.1 --port 8001
```

No segundo terminal:

```powershell
npm run dev
```

Acesse http://127.0.0.1:5173. Em Linux/macOS, substitua `py -3.14` por `python3`, use `.venv/bin/python` e `cp .env.example .env`.

Para executar com um único servidor após compilar:

```powershell
npm run build
npm run test:upload
.\.venv\Scripts\python.exe -m uvicorn backend.app:app --host 127.0.0.1 --port 8001
```

Nesse modo, acesse http://127.0.0.1:8001. O backend serve o conteúdo de `dist/` quando essa pasta existe no início do processo. Use um único worker neste MVP.

## Demonstração

1. Clique em **Carregar exemplos** na visão geral. Aurora e Vértice são apólices fictícias, identificadas na interface; não representam ofertas de seguro.
2. Selecione as duas apólices e clique em **Comparar apólices**.
3. Ative o filtro de diferenças, abra o limite de responsabilidade e confira o trecho e a página de origem.
4. Exporte o PDF e recupere o resultado pelo histórico.
5. Para demonstrar uma chamada real ao Gemini, configure a chave, abra **Nova análise** e envie um PDF ou imagem. Os arquivos em `Projeto_Final_Artefatos/exemplos/` são materiais fictícios; carregar os exemplos na interface apenas insere dados de demonstração e não chama o modelo.

Os arquivos enviados ficam em `data/`, junto ao SQLite, e permanecem após reiniciar o serviço. O conteúdo usado na extração e na consulta é enviado ao Google Gemini. O MVP é local, não tem autenticação nem separação entre usuários; não o exponha publicamente sem adaptar a arquitetura.

## Tecnologias e organização

```text
backend/                  API, documentos, IA, comparação, banco e relatórios
src/                      Interface React, TypeScript e CSS responsivo
tests/                    Testes de leitura, evidências e integração da API
scripts/                  Geração de artefatos e verificação no navegador
docs/                     Arquitetura, revisão e roteiro do vídeo final
Projeto_Final_Artefatos/  Relatório técnico, pitch, exemplos fictícios e ZIP
.github/workflows/        Verificação automatizada do código
```

Frontend: React 19, TypeScript, Vite, Tailwind CSS 4, shadcn/ui (Radix), Lucide e DM Sans. Backend: Python, Starlette, uvicorn, Pydantic, Google GenAI SDK, PyMuPDF, Pillow e SQLite. A integração usa Gemini GenerateContent com resposta JSON estruturada e leitura multimodal. Os relatórios usam ReportLab; os slides, PptxGenJS. As fontes são locais e não dependem de CDN.

A interface usa tons neutros, navegação compacta e componentes reutilizáveis em `src/components/ui/`. O [sistema visual](DESIGN.md) registra cores, tipografia e padrões de interação. A revisão visual usou [Impeccable](https://github.com/pbakaus/impeccable), a [skill shadcn](https://github.com/shadcn-ui/ui/tree/main/skills/shadcn) e Humanizer para revisar os textos em português.

Consulte [a arquitetura, as decisões e as limitações](docs/ARQUITETURA.md). A comparação é textual e determinística: textos iguais não comprovam equivalência jurídica.

## Testes

```powershell
npm run build
.\.venv\Scripts\python.exe -m unittest discover -s tests -v
```

O teste no navegador é opcional e requer os dois servidores em execução:

```powershell
.\.venv\Scripts\python.exe -m pip install playwright
.\.venv\Scripts\python.exe scripts/check_ui.py
.\.venv\Scripts\python.exe scripts/check_design.py
```

No Windows, o navegador usa Edge em modo sem janela. Em Linux, instale Chromium com `python -m playwright install chromium`. Capturas e resultados temporários ficam em `tmp/ui/`. Os testes do provedor usam respostas simuladas e não consomem a API. A precisão da extração em contratos reais ainda precisa ser avaliada por especialistas.

`check_design.py` percorre estados de upload e erro, navegação por teclado, retorno de foco, contraste e telas de 320 a 1440 pixels. Capturas e resultados de acessibilidade ficam em `tmp/design-review/`. Os testes de navegador carregam exemplos e salvam comparações; para executá-los sem alterar sua biblioteca, inicie a API com `DATA_DIR` apontando para uma pasta temporária.

## Entregáveis e situação

- [Relatório técnico](Projeto_Final_Artefatos/InsurMinds_Relatorio_Tecnico.pdf).
- [Pitch Deck](Projeto_Final_Artefatos/InsurMinds_Projeto_Final.pptx).
- [Roteiro do vídeo final](docs/ROTEIRO.md) e [vídeo narrado](Projeto_Final_Artefatos/InsurMinds_Projeto_Final.mp4), com navegação real e PDFs fictícios analisados pelo Gemini 3.8.
- Código-fonte e materiais em `Projeto_Final_Artefatos/InsurMinds_Codigo_Fonte.zip`. Para atualizar o ZIP: `py -3.14 scripts/build_delivery.py --zip-only`.
- Repositório público: https://github.com/vicTmm/i2a2-desafio-final. A equipe concluiu os testes funcionais desta versão; a precisão em apólices reais ainda requer avaliação especializada.

O fluxo de extração foi testado com o Gemini usando os documentos fictícios do projeto. Isso confirma o funcionamento da integração, mas não mede a precisão em apólices reais de mercado; essa avaliação ainda requer revisão especializada.

Para testar PDFs reais pela API com armazenamento isolado e retomada entre execuções:

```bash
.venv/bin/python scripts/check_real_policies.py /caminho/apolice1.pdf /caminho/apolice2.pdf
```

Use `--preflight-only` para testar leitura e divisão sem chamar a IA. Os documentos, checkpoints e resultados privados ficam em `tmp/real-policies/processed/`, ignorados pelo Git. Quando duas ou mais análises concluem, o roteiro verifica também comparação e exportações. O teste real consome a cota da conta configurada. A [revisão das quatro apólices reais](docs/REVISAO_APOLICES_REAIS.md) registra o diagnóstico e a validação das mudanças.

Prazo informado no enunciado: **06/10/2026 às 23h59**.

## Integrantes

Equipe InsurMinds: Victor Hugo Araujo, João Carlos Mendonça, Adriéli Zacharias e Bruno Veiga.

## Licença

O código-fonte está sob [licença MIT](LICENSE). Os exemplos são sintéticos e autorais. Dependências e fontes mantêm suas próprias licenças. O repositório não inclui apólices reais de terceiros.
