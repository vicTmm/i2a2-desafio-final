# Artefatos da entrega

Esta pasta contém o relatório técnico, o pitch editável, o vídeo com legendas, documentos fictícios de demonstração e um ZIP do código.

Os artefatos descrevem o estado efetivamente implementado. A demonstração usa exemplos com dados pré-preenchidos. Para fechar a entrega acadêmica, a equipe precisa validar e gravar uma extração real com IA, identificar os integrantes e publicar o repositório com acesso público.

Os PDFs e a imagem em `exemplos/` são materiais sintéticos autorais, sem validade contratual. Não foram obtidos de seguradoras, SUSEP ou outras bases reais. A imagem contém apenas a primeira página da apólice Aurora, de modo que vários critérios não aparecem nela.

Regeneração a partir da raiz do projeto:

```powershell
py -3.14 scripts/build_delivery.py
node scripts/build_pitch.mjs
py -3.14 scripts/record_demo.py
py -3.14 scripts/build_delivery.py --zip-only
```

O vídeo requer os servidores locais em execução, Playwright e FFmpeg instalado pelo npm. No Windows utiliza Edge em modo sem janela. O PowerPoint é opcional para renderizar os slides com `scripts/render_pitch.ps1`. A geração usa PptxGenJS como alternativa local à indisponibilidade do runtime Artifact Tool.
