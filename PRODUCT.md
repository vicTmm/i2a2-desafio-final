# InsurMinds

<!-- impeccable:product-schema 1 -->

## Platform

web

## Product Purpose

MVP acadêmico I2A2 para ler e comparar apólices D&O. O fluxo existente recebe PDF ou imagem, extrai 16 critérios com referências à origem, compara de duas a quatro apólices e exporta PDF ou JSON.

## Operating Context

Aplicação local em React/TypeScript e Python/Starlette. Documentos e comparações persistem em SQLite e arquivos locais. A extração e a consulta usam Gemini; a comparação é textual. Não há autenticação nem isolamento por usuário.

## Users

A interface atende à leitura e conferência documental. Perfil profissional específico e frequência de uso ainda não foram definidos pela equipe.

## Capabilities and Constraints

Preservar biblioteca, busca, filtros, seleção, comparação, evidências, histórico, upload e exportação. Exemplos são fictícios e devem continuar identificados. Evidência textual localizada não comprova interpretação correta. A validação real da IA ainda consta como pendente na documentação.

## Brand Commitments

Nome InsurMinds. Direção escolhida pelo usuário: minimalista, tons neutros e interface mais compacta. Textos em português, diretos e sem promessas de precisão não comprovadas. Aplicar Impeccable, shadcn e Humanizer.

## Evidence on Hand

README.md, docs/ARQUITETURA.md, backend/models.py, backend/demo.py e tests/test_pipeline.py descrevem as funcionalidades e os exemplos existentes. Não há métricas de precisão em contratos reais.
