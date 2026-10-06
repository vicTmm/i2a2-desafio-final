# Revisão e teste das apólices reais

Teste realizado em 05/10/2026 com os quatro arquivos originais informados pelo usuário, usando Python 3.14.8 e as dependências fixadas em `requirements.txt`.

## Diagnóstico da versão original, antes das correções

**Nenhuma das quatro apólices concluiu a análise na versão original.** Três documentos não passavam pelos limites de entrada. Cortel passou pela leitura, mas duas tentativas reais com acesso à rede terminaram com falha de comunicação com Gemini. As referências de código nesta seção correspondem à versão anterior às mudanças.

| Arquivo | Páginas | Caracteres extraídos¹ | Resultado local |
| --- | ---: | ---: | --- |
| Apólice - Sandech Consultoria Em Engenharia E Gestão Ltda - D&O.pdf | 59 | 254.132 | Upload HTTP 202; processamento termina em `error`: excede 220 mil caracteres. |
| (Apolice) Tecnogeo Fundações - Renovação 2026- D&O.pdf | 110 | 303.871 | Upload HTTP 400: excede 60 páginas. |
| Apólice - Tecnogeo -D&O - Chubb.pdf | 114 | 318.786 | Upload HTTP 400: excede 60 páginas. |
| Apólice - Cortel Holding S.A - 22.07.2024.pdf | 39 | 162.716 | Upload HTTP 202; leitura e limites passam; duas tentativas reais com rede terminam em `error`: falha de comunicação com a IA. |

¹ Texto extraído por `page.get_text(sort=True).strip()`, somado por página. Nos documentos acima de 60 páginas, a medição foi feita diretamente com PyMuPDF para diagnóstico; o leitor da ferramenta rejeita esses documentos antes de extrair o texto.

Todos os arquivos têm menos de 1 MB e não exigem senha. Sandech e Cortel têm uma página rasterizada cada, dentro do limite de 20 páginas visuais.

## Verificação executada

- A suíte existente passou: **18 testes**, incluindo leitura, evidências, integração da API, comparação, persistência e exportação. Os testes do provedor dessa suíte são simulados.
- O frontend compilou com sucesso usando `npm run build` (TypeScript e Vite).
- Os PDFs reais foram lidos com PyMuPDF e submetidos a `backend.documents.read_document`.
- Cada original foi enviado separadamente ao endpoint `/api/upload` via `TestClient`, com armazenamento temporário isolado e espera pela conclusão das tarefas.
- Sem chave, a API devolveu HTTP 503 para todos os arquivos, conforme previsto no código.
- Para verificar os limites independentemente da chave, somente a indicação de configuração foi simulada. A função de comunicação com Gemini foi substituída por uma interrupção explícita, sem gerar fatos ou resultados de IA. As duas Tecnogeo e Sandech falharam antes dessa função; Cortel chegou a ela. O estado `error` de Cortel nesse ensaio corresponde à interrupção do teste, e não a uma falha do documento.
- Após o usuário fornecer uma chave, foi executado o fluxo real dos quatro arquivos, sem simular o provedor. Os três documentos bloqueados falharam antes da chamada ao Gemini. Cortel foi enviada ao Gemini e terminou com erro de comunicação. A tentativa no sandbox e duas tentativas com acesso à rede não produziram extração.
- Uma chamada mínima de diagnóstico, sem o documento, retornou `503 UNAVAILABLE` do Gemini: o modelo estava com alta demanda e pediu nova tentativa. Isso identifica indisponibilidade do provedor na chamada de diagnóstico; o erro original de Cortel foi mascarado pela mensagem genérica do backend.
- A chave foi armazenada somente no `.env` local, ignorado pelo Git. Nenhum original foi alterado ou incluído no repositório.

As medições e os resultados locais estão em `tmp/real-policies/preflight.json` e `tmp/real-policies/api-results.json`, ignorados pelo Git. `tmp/real-policies/live-results.json` registra o teste real; `provider-diagnostic.json` registra o diagnóstico com a chave ocultada. O roteiro local está em `tmp/real-policies/run_live.py`.

## Achados da revisão

1. **Os limites impedem o uso de três dos quatro contratos completos.** `backend/documents.py:7` limita a leitura a 60 páginas; `backend/agents.py:102` rejeita mais de 220 mil caracteres. Aumentar apenas o limite de páginas não resolve as duas Tecnogeo, pois também ultrapassam o limite de texto. O tratamento de documentos longos precisa preservar páginas e conciliar informações entre partes do mesmo contrato.
2. **O envio em lote para no primeiro upload rejeitado.** Em `src/main.tsx:1324`, todos os envios estão dentro de um único `try`. Uma Tecnogeo rejeitada interrompe os arquivos seguintes. Na ordem fornecida pelo usuário, Sandech entra na fila, a renovação Tecnogeo falha e os dois documentos seguintes ficam sem envio naquela tentativa. Essa consequência foi identificada por revisão do código; não foi executado um teste de navegador.
3. **Sandech só revela o excesso de texto depois de entrar na biblioteca.** O upload valida páginas e tamanho, mas o limite de caracteres é verificado na tarefa de extração. O resultado é HTTP 202 seguido de `error`, em vez de rejeição imediata com explicação do limite.
4. **`verified` confirma a presença da citação, não a interpretação do valor.** `backend/agents.py:86` procura o trecho na página; não comprova que o valor resumido decorre desse trecho. O schema oferece apenas uma citação e uma página por critério, limitando o suporte de resumos de exclusões distribuídas por várias páginas. A interface já informa que a interpretação precisa de revisão. Os testes existentes não medem a precisão dos 16 critérios nessas apólices reais.
5. **Indisponibilidade do modelo aparece como erro genérico de conexão.** `backend/agents.py:61` não distingue HTTP 503 do provedor; uma resposta de alta demanda recebe a orientação de verificar a conexão. Diferenciar indisponibilidade temporária ajudaria o usuário a decidir quando reprocessar.

## Pendências para um teste completo

A chave já está configurada. Cortel depende de uma resposta utilizável do provedor; as outras três exigem primeiro suporte a documentos maiores. Depois da extração, conferir os 16 critérios com as páginas originais, principalmente coberturas contratadas versus condições gerais, franquias, exclusões, retroatividade e prazos; só então verificar comparação e exportação com resultados reais.

O diagnóstico acima foi registrado antes das mudanças de produção.

## Correções implementadas

- Limite ampliado para 300 páginas e 2 milhões de caracteres, mantendo 20 MB por arquivo.
- Divisão sem descarte de texto em blocos de até 60 mil caracteres, 20 páginas e 4 imagens. A numeração original é preservada, inclusive quando uma página muito longa precisa de mais de um bloco.
- Checkpoints locais gravados atomicamente por conteúdo, prompt, schema e modelos. Uma nova tentativa reutiliza blocos concluídos, inclusive após reiniciar o servidor.
- Timeout de 90 segundos por chamada, três tentativas com espera progressiva para erros transitórios e alternativa configurável de modelo após indisponibilidade. Erros de chave e cotas não provocam alternância de modelo. Intervalo mínimo padrão de 15 segundos entre chamadas.
- Valores distintos preservados com suas evidências e sinalização de revisão. Várias citações/páginas aparecem nos detalhes, JSON e PDF; documentos antigos permanecem compatíveis. Páginas diferentes não criam diferenças artificiais na comparação dos mesmos valores.
- Upload em lote continua após um arquivo rejeitado, mantendo somente os arquivos que falharam para nova tentativa.
- Progresso por bloco e quantidade de partes salvas aparecem nos detalhes da apólice.

## Validação após as mudanças

Passaram 32 testes Python, o teste Node de envio em lote e o build TypeScript/Vite. O teste de navegador com dados fictícios verificou evidências múltiplas, links para páginas originais, exibição das versões, tela móvel sem overflow, atualização automática do progresso no diálogo aberto e continuação do lote após um upload rejeitado. Capturas ficaram em `tmp/chunks-ui/`.

As quatro apólices reais passaram pela leitura e divisão local:

| Apólice | Páginas | Caracteres | Blocos |
| --- | ---: | ---: | ---: |
| Sandech | 59 | 254.132 | 5 |
| Tecnogeo renovação 2026 | 110 | 303.871 | 6 |
| Tecnogeo Chubb | 114 | 318.786 | 6 |
| Cortel | 39 | 162.716 | 3 |

O roteiro reproduzível é `scripts/check_real_policies.py`. O teste real usa armazenamento isolado em `tmp/real-policies/processed/`, com os documentos, checkpoints, SQLite e `results.json`. Nenhum conteúdo de contrato foi incluído nos arquivos versionáveis.

### Resultado das chamadas reais após as correções

Todos os uploads retornaram HTTP 202. O Gemini permaneceu intermitentemente indisponível, mesmo com repetições e alternativa de modelo; nenhuma análise completa chegou a `ready` nesta execução.

| Apólice | Blocos concluídos/salvos | Estado final |
| --- | ---: | --- |
| Sandech | 0/5 | `error`: Gemini temporariamente indisponível |
| Tecnogeo renovação 2026 | 2/6 | `error`: Gemini temporariamente indisponível |
| Tecnogeo Chubb | 0/6 | `error`: Gemini temporariamente indisponível |
| Cortel | 0/3 | `error`: Gemini temporariamente indisponível |

Os dois blocos da renovação foram produzidos por `gemini-3.6-flash`. A revalidação local encontrou 14 ocorrências de critérios com evidência textual em cada bloco (28 ao todo, antes da consolidação), sem descarte por citação inválida e sem evidências que exigissem revisão visual. Isso confirma a localização dos trechos citados; não confirma a interpretação dos valores nem a completude do contrato.

Como nenhuma análise completa ficou pronta, não foi possível testar comparação e exportação com esses resultados reais. Esses fluxos passaram nos testes automatizados com dados simulados, incluindo versões com evidências em páginas distintas.

Para retomar os mesmos arquivos, execute novamente o roteiro com os caminhos originais. Ele reutiliza as apólices no armazenamento isolado e os dois checkpoints já salvos. Exemplo para retomar a renovação:

```bash
.venv/bin/python scripts/check_real_policies.py '/Users/victorhugo/Downloads/(Apolice) Tecnogeo Fundações - Renovação 2026- D&O.pdf'
```

As cópias armazenadas dos quatro PDFs foram conferidas byte a byte com os originais e são idênticas. Os testes reais mantêm a biblioteca principal em `data/` separada do armazenamento de teste.

### Execução final com Gemini 3.8 Flash — 05/10/2026

O modelo padrão foi atualizado para `gemini-3.8-flash`, mantendo a alternativa 3.7. As quatro entradas passaram pelo preflight e upload HTTP 202.

| Apólice | Blocos concluídos | Resultado final |
| --- | ---: | --- |
| Sandech | 0/5 | `error`: indisponibilidade temporária do Gemini |
| Tecnogeo renovação 2026 | 6/6 | `ready`: processamento completo com Gemini 3.8 |
| Tecnogeo Chubb | 0/6 | `error`: indisponibilidade temporária do Gemini |
| Cortel | 0/3 | `error`: cota do Gemini atingida |

Na renovação, 15 dos 16 critérios mantiveram valores com evidências textuais verificadas; o segurado ficou ausente após validação. Quatorze critérios preservaram versões distintas e receberam sinalização de revisão. A consolidação conserva a origem de cada versão, mas não decide a prevalência de condições gerais sobre coberturas contratadas. Portanto, `ready` confirma conclusão técnica, não aprovação contratual. As cópias armazenadas permaneceram idênticas aos originais.

Somente uma apólice real ficou pronta; a comparação requer pelo menos duas e não foi executada com contratos reais. O registro público `Projeto_Final_Artefatos/Validacao_Apolices_Reais.json` contém apenas métricas, progresso e erros, sem fatos, trechos ou arquivos dos contratos. O registro completo permanece no diretório privado ignorado pelo Git.

Não se repetiu a chamada após o erro de cota. A retomada requer disponibilidade/cota liberada e reutiliza checkpoints compatíveis. Em paralelo, os dois PDFs fictícios concluíram a extração real com Gemini 3.8: 16 critérios verificados por documento; comparação com 10 diferenças e zero ausências; exportações PDF e JSON aprovadas. A evidência pública dessa execução está em `Validacao_IA_Exemplos.json`.
