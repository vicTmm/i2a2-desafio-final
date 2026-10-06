# Entrega InsurMinds / I2A2 2026

Pacote final revisado em 05/10/2026. Equipe: Victor Hugo Araujo, João Carlos Mendonça, Adriéli Zacharias e Bruno Veiga.

- `InsurMinds_Relatorio_Tecnico.pdf`: arquitetura, decisões, limites e validação.
- `InsurMinds_System_Design.docx`: desenho técnico editável.
- `InsurMinds_Projeto_Final.pptx`: pitch com oito slides editáveis.
- `InsurMinds_Projeto_Final.mp4`: navegação real na aplicação, usando os resultados da IA sobre os PDFs fictícios; narração sintética identificada.
- `Validacao_IA_Exemplos.json`: registro da execução real com Gemini 3.8 Flash. Dois documentos, 16 critérios com evidências verificadas por documento, 10 diferenças e exportações PDF/JSON aprovadas.
- `Validacao_Apolices_Reais.json`: métricas públicas do teste de mercado; renovação Tecnogeo concluída, demais com indisponibilidade/cota. Não contém trechos contratuais.
- `InsurMinds_Codigo_Fonte.zip`: código, documentação e entregáveis, sem chave, dados locais ou apólices privadas.
- `exemplos/`: PDFs e imagem sintéticos autorais, sem validade contratual.

Carregar exemplos pela interface usa dados pré-preenchidos. O vídeo usa os resultados dos documentos enviados ao Gemini, sem esse atalho. A presença textual das citações não comprova precisão contratual, que ainda requer revisão especializada. Os testes de mercado estão documentados em `docs/REVISAO_APOLICES_REAIS.md`.

Validação: 32 testes Python, um teste Node de upload, build e QA da interface desktop/móvel. Repositório: https://github.com/vicTmm/i2a2-desafio-final.

Regeneração na raiz: `python scripts/build_delivery.py`, `node scripts/build_pitch.mjs`, `python scripts/update_system_design.py`. Para gravar: `node scripts/record_demo.mjs` requer Chrome, Playwright Core e a aplicação local em `DEMO_URL` (padrão http://127.0.0.1:8002), com a biblioteca dos dois PDFs fictícios já analisados pela IA. O cache FFmpeg de gravação é preparado pelo roteiro. A narração usa a voz Luciana do macOS. `python scripts/render_office.py` exporta cópias de QA e imagens de todas as páginas com o LibreOffice instalado. Depois de gerar os artefatos, execute `python scripts/build_delivery.py --zip-only` e `python scripts/check_artifacts.py`.
