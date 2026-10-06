# InsurMinds

Ferramenta local para ler e comparar apólices D&O em PDF ou imagem, desenvolvida para o Projeto Final I2A2 2026. O Gemini extrai 16 critérios com trechos e páginas de origem. A interface permite conferir as evidências, comparar de duas a quatro apólices, consultar os dados e exportar PDF ou JSON.

A leitura usa o conteúdo do documento, sem exigir um formulário fixo. Os PDFs fictícios Aurora e Vértice acompanham o projeto para demonstração e foram processados pela integração real com IA.

## Instalação

Requisitos: Node.js 24 e Python 3.14.

**macOS / Linux**

```bash
npm ci
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
cp .env.example .env
```

**Windows / PowerShell**

```powershell
npm ci
py -3.14 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
Copy-Item .env.example .env
```

Copie `.env.example` apenas na primeira configuração. Se `.env` já existe, preserve suas configurações. Para analisar novos documentos, preencha `GEMINI_API_KEY` com uma chave do [Google AI Studio](https://aistudio.google.com/api-keys). A chave permanece no servidor e o `.env` é ignorado pelo Git.

O modelo padrão é `gemini-3.8-flash`; `GEMINI_MODEL` permite alterá-lo. `GEMINI_FALLBACK_MODELS` define a alternativa em caso de indisponibilidade, e `GEMINI_REQUEST_INTERVAL` controla o intervalo entre chamadas. Reinicie o servidor após mudar essas variáveis. A extração depende da disponibilidade e da cota da conta Gemini.

## Executar

Compile a interface e inicie o servidor na raiz do projeto:

```bash
npm run build
.venv/bin/python -m uvicorn backend.app:app --host 127.0.0.1 --port 8001
```

No Windows, use `.\.venv\Scripts\python.exe` no lugar de `.venv/bin/python`.

Abra **http://127.0.0.1:8001**. O servidor entrega a interface compilada e a API. Use um único processo de servidor.

Para desenvolver a interface com atualização automática, mantenha a API em execução e rode `npm run dev` em outro terminal. Nesse modo, abra http://127.0.0.1:5173.

## Testar a leitura dos PDFs

1. Abra **Nova análise** e envie os dois PDFs de [exemplos](Projeto_Final_Artefatos/exemplos).
2. Aguarde o estado **Analisado** e confira os critérios e suas evidências.
3. Selecione os dois documentos e clique em **Comparar apólices**.
4. Use o filtro de diferenças, abra um trecho de origem e exporte o PDF.
5. Consulte a comparação novamente em **Histórico**.

**Carregar exemplos** oferece uma demonstração imediata com dados pré-preenchidos e funciona sem chave. Essa ação não chama a IA; para testar a leitura, use o upload descrito acima.

A execução registrada com Gemini 3.8 concluiu ambos os PDFs fictícios: 16 critérios com citações verificadas por documento, 10 diferenças textuais na comparação e exportações PDF/JSON aprovadas. O [registro de validação](Projeto_Final_Artefatos/Validacao_IA_Exemplos.json) acompanha a entrega.

## Verificação

```bash
.venv/bin/python -m unittest discover -s tests -v
npm run test:upload
npm run build
```

A suíte contém 32 testes Python e um teste Node. Os testes automatizados do provedor usam respostas simuladas e não consomem a API.

Para conferir a leitura dos exemplos sem chamar o Gemini:

```bash
.venv/bin/python scripts/check_documents.py --preflight-only
```

Para executar upload, extração real, comparação e exportações em uma biblioteca de teste isolada:

```bash
.venv/bin/python scripts/check_documents.py
```

Esse comando consome a cota da conta configurada. Os resultados ficam em `tmp/document-checks/`, sem alterar a biblioteca principal. O script também aceita caminhos de outros documentos e `--data-dir` para escolher a biblioteca de teste.

As verificações opcionais de interface e acessibilidade estão descritas em [docs/VALIDACAO.md](docs/VALIDACAO.md).

## Arquitetura e limites

React/TypeScript na interface; Starlette/Python na API; Gemini para extração e consulta; PyMuPDF/Pillow para leitura; SQLite e arquivos locais para persistência; ReportLab para os relatórios. Veja [a arquitetura](docs/ARQUITETURA.md), [o escopo do produto](PRODUCT.md) e [os padrões visuais](DESIGN.md).

A entrada aceita até 20 MB, 300 páginas PDF e 2 milhões de caracteres. O processamento divide documentos em blocos, preserva as páginas e salva checkpoints para retomada após falhas. Informações divergentes mantêm suas evidências e recebem sinalização de revisão.

Arquivos e resultados permanecem em `data/`. O conteúdo usado na extração e na consulta é enviado ao Gemini. A aplicação foi desenvolvida para uso local, sem autenticação ou separação entre usuários. A verificação de uma citação comprova sua presença textual; a interpretação deve ser conferida pelo usuário. A comparação identifica diferenças textuais e não recomenda contratação.

## Entregáveis

- [Relatório técnico](Projeto_Final_Artefatos/InsurMinds_Relatorio_Tecnico.pdf).
- [System Design editável](Projeto_Final_Artefatos/InsurMinds_System_Design.docx).
- [Apresentação com oito slides](Projeto_Final_Artefatos/InsurMinds_Projeto_Final.pptx).
- [Vídeo narrado da aplicação](Projeto_Final_Artefatos/InsurMinds_Projeto_Final.mp4).
- [Código-fonte e materiais da entrega](Projeto_Final_Artefatos/InsurMinds_Codigo_Fonte.zip).

Todos os entregáveis estão disponíveis. As instruções para regenerá-los estão em [Projeto_Final_Artefatos/README.md](Projeto_Final_Artefatos/README.md).

Repositório: https://github.com/vicTmm/i2a2-desafio-final.

## Equipe e licença

Equipe InsurMinds: Victor Hugo Araujo, João Carlos Mendonça, Adriéli Zacharias e Bruno Veiga.

Código sob [licença MIT](LICENSE). Os exemplos são sintéticos e autorais. Dependências e fontes mantêm suas próprias licenças.
