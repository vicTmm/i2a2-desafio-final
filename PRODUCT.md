# InsurMinds

<!-- impeccable:product-schema 1 -->

## Platform

web

## Product Purpose

MVP acadêmico I2A2 para ler e comparar apólices D&O. O fluxo existente recebe PDF ou imagem, extrai 16 critérios com referências à origem, compara de duas a quatro apólices e exporta PDF ou JSON.

## Operating Context

Aplicação local em React/TypeScript e Python/Starlette. Documentos e comparações persistem em SQLite e arquivos locais. A extração e a consulta usam Gemini; a comparação é textual. Não há autenticação nem isolamento por usuário.

## Users

A interface atende pessoas que precisam localizar informações, conferir evidências e comparar documentos de apólices D&O.

## Capabilities and Constraints

Biblioteca, busca, filtros, seleção, comparação, evidências, histórico, upload e exportação estão implementados. Os exemplos fictícios são identificados na interface. Os dois PDFs de demonstração foram processados pelo Gemini 3.8 Flash, com 16 critérios e evidências verificadas por documento. A correspondência textual da citação não substitui a conferência da interpretação.

## Brand Commitments

Nome InsurMinds. Interface minimalista, tons neutros e controles compactos. Textos diretos em português. Os padrões visuais estão em DESIGN.md e os componentes em src/components/ui/.

## Evidence on Hand

README.md, docs/ARQUITETURA.md, backend/models.py, backend/demo.py e tests/ descrevem as funcionalidades e os exemplos existentes. Projeto_Final_Artefatos/Validacao_IA_Exemplos.json registra a execução real da IA sobre os PDFs fictícios. A demonstração não é uma avaliação de precisão em contratos de mercado.
