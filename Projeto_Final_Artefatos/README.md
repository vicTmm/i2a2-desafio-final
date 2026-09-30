# Artefatos da entrega

Esta pasta reúne o relatório técnico, o pitch editável, os documentos fictícios de demonstração e o ZIP do código-fonte. O vídeo anterior foi removido; a equipe fará uma nova gravação após revisar e testar o sistema.

Os artefatos descrevem o que está implementado. Os exemplos carregados pela interface usam dados pré-preenchidos e não chamam a IA. A equipe testou a integração com Gemini enviando os PDFs fictícios pela análise. A precisão em apólices reais de mercado ainda não foi avaliada por especialistas. O repositório já é público.

Equipe InsurMinds: Victor Hugo Araujo, João Carlos Mendonça, Adriéli Zacharias e Bruno Veiga.

Os PDFs e a imagem em `exemplos/` são materiais sintéticos autorais, sem validade contratual. Não foram obtidos de seguradoras, SUSEP ou outras bases reais. A imagem mostra apenas a primeira página da apólice Aurora; por isso, vários critérios não aparecem nela.

Para recriar os PDFs e o relatório técnico e atualizar o ZIP a partir da raiz do projeto:

```powershell
py -3.14 scripts/build_delivery.py
```

Para atualizar somente o ZIP:

```powershell
py -3.14 scripts/build_delivery.py --zip-only
```

O pitch pode ser regenerado com `node scripts/build_pitch.mjs`. A equipe fará a gravação do vídeo após concluir os testes. O PowerPoint é opcional para renderizar os slides com `scripts/render_pitch.ps1`. A geração usa PptxGenJS como alternativa local ao runtime Artifact Tool.
