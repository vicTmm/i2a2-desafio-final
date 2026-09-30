---
name: "InsurMinds"
description: "Interface compacta para conferir e comparar apólices D&O."
colors:
  background: "#ffffff"
  foreground: "#242426"
  card: "#ffffff"
  card-foreground: "#242426"
  popover: "#ffffff"
  popover-foreground: "#242426"
  primary: "#27272a"
  primary-foreground: "#ffffff"
  secondary: "#f4f4f5"
  secondary-foreground: "#3f3f46"
  muted: "#fafafa"
  muted-foreground: "#636369"
  accent: "#ededee"
  accent-foreground: "#242426"
  destructive: "#a12d2d"
  border: "#e4e4e7"
  input: "#d4d4d8"
  ring: "#71717a"
  overlay: "rgb(24 24 27 / 32%)"
typography:
  headline:
    fontFamily: "DM Sans, sans-serif"
    fontSize: "28px"
    fontWeight: 600
    lineHeight: 1.25
    letterSpacing: "-0.03em"
  headline-mobile:
    fontFamily: "DM Sans, sans-serif"
    fontSize: "24px"
    fontWeight: 600
    lineHeight: 1.25
    letterSpacing: "-0.03em"
  title:
    fontFamily: "DM Sans, sans-serif"
    fontSize: "18px"
    fontWeight: 600
    letterSpacing: "-0.02em"
  section:
    fontFamily: "DM Sans, sans-serif"
    fontSize: "16px"
    fontWeight: 600
    letterSpacing: "-0.02em"
  body:
    fontFamily: "DM Sans, sans-serif"
    fontSize: "14px"
    fontWeight: 400
    lineHeight: 1.65
  label:
    fontFamily: "DM Sans, sans-serif"
    fontSize: "12px"
    fontWeight: 400
  metric:
    fontFamily: "DM Sans, sans-serif"
    fontSize: "24px"
    fontWeight: 500
    lineHeight: 1
    letterSpacing: "-0.03em"
rounded:
  field: "6px"
  lg: "8px"
  panel: "10px"
  xl: "11.2px"
  4xl: "20.8px"
spacing:
  "4": "4px"
  "8": "8px"
  "10": "10px"
  "12": "12px"
  "16": "16px"
  "20": "20px"
  "24": "24px"
  "32": "32px"
components:
  button-primary:
    backgroundColor: "{colors.primary}"
    textColor: "{colors.primary-foreground}"
    rounded: "{rounded.lg}"
    padding: "0 10px"
    height: "32px"
  button-outline:
    backgroundColor: "{colors.background}"
    textColor: "{colors.foreground}"
    rounded: "{rounded.lg}"
    padding: "0 10px"
    height: "32px"
  button-ghost:
    backgroundColor: "transparent"
    textColor: "{colors.foreground}"
    rounded: "{rounded.lg}"
    padding: "0 10px"
    height: "32px"
  button-link:
    backgroundColor: "transparent"
    textColor: "{colors.primary}"
    rounded: "{rounded.lg}"
    padding: "0 10px"
    height: "32px"
  search:
    backgroundColor: "{colors.background}"
    textColor: "{colors.foreground}"
    rounded: "{rounded.field}"
    padding: "0 12px"
    width: "340px"
  nav-item:
    backgroundColor: "transparent"
    textColor: "{colors.muted-foreground}"
    rounded: "{rounded.field}"
    padding: "10px 12px"
  badge-secondary:
    backgroundColor: "{colors.secondary}"
    textColor: "{colors.secondary-foreground}"
    rounded: "{rounded.4xl}"
    padding: "2px 8px"
    height: "20px"
  policy-card:
    backgroundColor: "{colors.background}"
    textColor: "{colors.foreground}"
    rounded: "{rounded.panel}"
    padding: "20px"
  upload-zone:
    backgroundColor: "{colors.muted}"
    textColor: "{colors.foreground}"
    rounded: "{rounded.lg}"
    padding: "24px 15px"
  alert:
    backgroundColor: "{colors.card}"
    textColor: "{colors.destructive}"
    rounded: "{rounded.lg}"
    padding: "8px 10px"
---

# Design System: InsurMinds

## Overview

**Creative North Star: "Mesa de conferência"**

Uma mesa de conferência documental: superfícies claras, contraste neutro e controles compactos. A hierarquia distingue ação, conteúdo e apoio sem depender de ilustração ou cor decorativa.

DM Sans reúne títulos, valores e textos de interface. Bordas leves organizam tabelas e painéis; diferenças de tom indicam seleção e disponibilidade.

**Key Characteristics:**
- Tons neutros e vermelho reservado a erros.
- Uma família tipográfica, com pesos 400, 500 e 600.
- Densidade compacta, foco visível e adaptação ao toque.

## Colors

Cinzas próximos do branco sustentam a leitura; o grafite concentra as ações.

### Primary
- **Grafite:** `primary` nas ações principais; `primary-foreground` no texto sobre elas.

### Neutral
- **Papel:** `background`, `card` e `popover` nas superfícies; seus pares `foreground` no conteúdo.
- **Cinza de apoio:** `secondary` e `muted` em estados, cabeçalhos e áreas auxiliares; seus pares de texto preservam hierarquia.
- **Cinza de seleção:** `accent` e `accent-foreground` na navegação ativa e seleção de texto.
- **Contornos:** `border` separa áreas, `input` marca campos e `ring` indica foco. `overlay` é o véu disponível para sobreposições.
- **Vermelho de erro:** `destructive` acompanha mensagem ou ícone de erro; não é uma cor de marca.

**The Cor funcional Rule.** Use vermelho para erro; seleção e navegação usam tons neutros.

## Typography

**Display Font / Body Font:** DM Sans, com fallback sans-serif. A aplicação carrega os pesos regular, médio e seminegrito; não há família de destaque separada.

### Hierarchy
- **Headline:** título da página; `headline-mobile` substitui sua dimensão no celular.
- **Title / Section:** títulos de painéis e seções; subtítulos menores usam corpo seminegrito.
- **Body:** texto geral. Biblioteca e descrições também usam tamanho compacto (13px); parágrafos explicativos têm largura de leitura até (65 a 70ch).
- **Label:** rótulos e metadados; a tabela também usa texto auxiliar (11px).
- **Metric:** resumo numérico, com algarismos tabulares. Valores monetários também usam algarismos tabulares.

**The Peso disponível Rule.** Use os pesos carregados de DM Sans: 400, 500 e 600.

## Layout

Barra lateral fixa (216px), cabeçalho (57px) e conteúdo central com largura máxima (1360px) e margens internas (32px). Entre (701 a 1050px), a lateral passa a (200px) e as margens a (24px).

Até (700px), a navegação abre em diálogo Radix, o cabeçalho mede (56px) e o conteúdo usa margens laterais (16px). Resumos passam de quatro para duas colunas; cartões de seleção passam a uma coluna. Botões recebem altura mínima (40px). A barra de seleção quebra linhas e sua ação principal ocupa a largura disponível.

Biblioteca e comparação preservam rolagem horizontal em seus próprios contêineres. No resumo da comparação, ícone e conteúdo formam duas colunas; a ação fica alinhada ao conteúdo no celular. O ritmo reutiliza principalmente os passos de espaçamento do frontmatter.

## Elevation & Depth

O conteúdo permanece plano, separado por bordas finas e fundos neutros. A barra de seleção e as notificações usam sombras suaves; a comparação conserva uma sombra curta na coluna fixa. Diálogos usam contorno translúcido e véu leve, com desfoque quando suportado.

### Shadow Vocabulary
- **Seleção flutuante:** `0 8px 32px rgb(24 24 27 / 14%)`.
- **Notificação:** `0 6px 24px rgb(24 24 27 / 10%)`.
- **Coluna fixa:** `0 1px 2px var(--border)`.

**The Superfície plana Rule.** Organize o conteúdo com bordas e tons; reserve sombras suaves para elementos flutuantes.

## Shapes

Cantos discretamente arredondados distinguem campos e navegação, tabelas, painéis e diálogos. O frontmatter registra as medidas finais; os raios derivados do tema partem de `--radius`. Badges usam o raio mais amplo. Bordas de conteúdo têm espessura (1px); a área de upload usa linha tracejada. ícones são SVG Lucide.

## Components

### Buttons

Botões shadcn/Radix Nova, com texto médio (14px), altura padrão compacta e ícone (16px). Primário em grafite; outline com borda; ghost para ações discretas; link para ações textuais. Hover altera o fundo ou sublinha o link. Foco usa anel de (3px) em `ring` com metade da opacidade; pressionar desloca (1px) quando não há popup. Desabilitados perdem opacidade e interação. A biblioteca também oferece secondary e destructive.

### Chips

Badge secundário para estado e contagem; outline para exemplo fictício; destructive para erro. Texto (12px), ícone (12px) e contorno fino. Estado sempre acompanha texto ou ícone.

### Cards / Containers

Cartão de seleção branco, com borda, espaçamento interno compacto e título seminegrito. Selecionado, recebe fundo `muted` e borda `primary`, sem sombra. Tabelas e painéis usam borda uniforme; citações usam fundo discreto e o mesmo contorno.

### Inputs / Fields

Busca nativa em contêiner com ícone, borda fina, texto (13px) e largura limitada pelo espaço disponível. Foco global usa contorno (2px) e afastamento (3px). Erros incluem mensagem; controles desabilitados mantém estado explícito.

### Navigation

Itens laterais com ícone (17px), texto (13px), altura mínima (40px) e fundo transparente. Ativo usa `accent`, texto principal e peso 600. Hover clareia o fundo. No celular, o diálogo gerencia foco e fechamento.

### Upload e alertas

área de upload tracejada, centralizada e compacta, com instrução, formatos e limite de arquivo. Hover e arrastar usam fundo `secondary` e borda `primary`; o diálogo mantém espaçamento pelo grid, sem margens acumuladas. Alertas agrupam mensagem e tentativa de recuperação, com dispensa separada. No celular, ações quebram linha junto ao conteúdo.

Transições de controles usam (160ms); diálogos usam (100ms). A preferência por movimento reduzido remove transições e reduz animações.

## Do's and Don'ts

### Do:
- Do preservar foco visível, rótulos e estados desabilitados.
- Do identificar exemplos fictícios e usar textos curtos em português.
- Do manter a rolagem horizontal dentro das tabelas e permitir quebra de texto nos controles.

### Don't:
- Don't adicionar cores decorativas à paleta neutra confirmada.
- Don't usar banners promocionais ou ilustrações decorativas.
- Don't remover estados de erro ou usar cor como único indicador de estado.
