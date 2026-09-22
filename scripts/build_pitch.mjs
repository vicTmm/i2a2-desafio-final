/** Fallback local: o runtime @oai/artifact-tool não está disponível nesta sessão. */
import pptxgen from "pptxgenjs";
import fs from "node:fs/promises";
import path from "node:path";
import { fileURLToPath } from "node:url";
const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..");
const out = path.join(root, "Projeto_Final_Artefatos");
await fs.mkdir(out, { recursive: true });
const pptx = new pptxgen();
pptx.layout = "LAYOUT_WIDE";
pptx.author = "Equipe InsurMinds";
pptx.subject = "Projeto Final I2A2 2026";
pptx.title = "InsurMinds - Análise e comparação de apólices D&O";
pptx.company = "InsurMinds";
pptx.lang = "pt-BR";
pptx.theme = {
  headFontFace: "Aptos Display",
  bodyFontFace: "Aptos",
  lang: "pt-BR",
};
const C = {
  bg: "F8F9F4",
  ink: "244B3B",
  muted: "66755D",
  accent: "5D7C42",
  line: "DEE5D5",
};
function text(slide, value, x, y, w, h, size = 22, extra = {}) {
  slide.addText(value, {
    x,
    y,
    w,
    h,
    fontFace: "Aptos",
    fontSize: size,
    color: C.ink,
    margin: 0,
    breakLine: false,
    vertAnchor: "top",
    ...extra,
  });
}
function base(title, num) {
  const s = pptx.addSlide();
  s.background = { color: C.bg };
  text(s, title, 0.7, 0.62, 11.9, 0.9, 34, {
    bold: true,
    fontFace: "Aptos Display",
  });
  text(s, "InsurMinds / I2A2 2026", 0.7, 7.04, 8, 0.2, 10, { color: C.muted });
  text(s, String(num).padStart(2, "0"), 12.05, 7.04, 0.5, 0.2, 10, {
    color: C.muted,
    align: "right",
  });
  return s;
}
let s = base("InsurMinds", 1);
text(s, "Clareza na comparação\nde apólices D&O", 0.7, 2.05, 11.8, 1.8, 48, {
  fontFace: "Aptos Display",
  bold: true,
});
text(s, "Extração com IA e evidências por página", 0.74, 4.35, 11.5, 0.65, 25, {
  color: C.muted,
});
text(
  s,
  "Projeto Final / Instituto de Inteligência Artificial Aplicada",
  0.74,
  5.7,
  11.5,
  0.5,
  17,
  { color: C.muted },
);
s.addNotes(
  "Enunciado do Projeto Final I2A2, fornecido pelo usuário, datado de 15/07/2026. Integrantes: identificação nominal pendente da equipe.",
);
s = base("O problema da leitura documental", 2);
text(
  s,
  "O limite de uma apólice não conta toda a história.",
  0.7,
  2.05,
  11.6,
  1.35,
  34,
  { bold: true },
);
text(
  s,
  "Franquias, sub-limites e exclusões mudam a interpretação de uma cobertura. A análise precisa conectar cada informação às condições do documento.",
  0.7,
  3.7,
  11.3,
  1.6,
  25,
  { color: C.muted },
);
text(
  s,
  "Necessidade: localizar diferenças e conferir a origem dos dados.",
  0.7,
  5.8,
  11.4,
  0.6,
  22,
  { color: C.accent },
);
s.addNotes(
  "Contexto extraído do enunciado I2A2. Não se apresentam números de mercado ou alegações de tempo economizado.",
);
s = base("A solução em funcionamento", 3);
const screenshot = path.join(root, "tmp/ui/overview.png");
if (await fs.stat(screenshot).catch(() => null)) {
  s.addImage({ path: screenshot, x: 6.8, y: 1.9, w: 5.76, h: 4.8 });
}
text(s, "16 critérios\npor documento", 0.7, 2.1, 5, 1.5, 35, { bold: true });
text(
  s,
  "Biblioteca pesquisável, comparação de até quatro apólices e consulta às evidências.",
  0.7,
  4.02,
  4.8,
  1.8,
  23,
  { color: C.muted },
);
s.addNotes(
  "Captura real da aplicação local. Dados exibidos são exemplos sintéticos e pré-preenchidos. Não representam execução real do modelo.",
);
s = base("Arquitetura do MVP", 4);
// Diagrama de arquitetura editável, exigido para explicar o projeto.
const nodes = [
  ["React / TypeScript", "Interface"],
  ["Python / Starlette", "API"],
  ["Texto + visão", "Leitura"],
  ["Gemini + Pydantic", "Extração e validação"],
  ["SQLite", "Persistência"],
  ["Comparação + PDF", "Resultado"],
];
nodes.forEach((n, i) => {
  const x = 0.7 + (i % 3) * 4.2,
    y = 2 + Math.floor(i / 3) * 2;
  text(s, n[0], x, y, 3.8, 0.55, 24, { bold: true });
  text(s, n[1], x, y + 0.73, 3.6, 0.5, 19, { color: C.muted });
});
text(
  s,
  "Pipeline especializado com IA na extração e na consulta.",
  0.7,
  6.3,
  11.9,
  0.5,
  20,
  { color: C.accent },
);
s.addNotes(
  "Fluxo: interface, API, recepção, leitura por página, extração multimodal, validação de evidências, SQLite e comparação. Documentação: docs/ARQUITETURA.md. Gemini structured output: https://ai.google.dev/gemini-api/docs/structured-output",
);
s = base("Cada informação tem uma origem", 5);
text(s, "Valor extraído", 0.7, 2.1, 4, 0.5, 20, { color: C.muted });
text(s, "R$ 15 milhões", 0.7, 2.87, 5, 1, 41, { bold: true });
text(s, "Evidência na página 1", 6.8, 2.1, 5.8, 0.5, 20, { color: C.muted });
text(
  s,
  "“Limite de responsabilidade: BRL 15.000.000,00.”",
  6.8,
  2.9,
  5.6,
  1.75,
  29,
  { bold: true },
);
text(
  s,
  "Trechos de texto são conferidos automaticamente. Leituras de imagens exigem revisão visual. Dado ausente permanece não identificado.",
  0.7,
  5.25,
  11.7,
  1.2,
  23,
  { color: C.muted },
);
s.addNotes(
  "Exemplo fictício autoral: Vértice, página 1. O verificador local valida presença textual, não a correção jurídica da interpretação.",
);
s = base("Comparação demonstrativa", 6);
s.addTable(
  [
    [
      { text: "Critério", options: { bold: true } },
      { text: "Aurora / fictícia", options: { bold: true } },
      { text: "Vértice / fictícia", options: { bold: true } },
    ],
    ["Limite agregado", "R$ 10 milhões", "R$ 15 milhões"],
    ["Prêmio total", "R$ 32.500", "R$ 41.800"],
    ["Franquia Side B", "R$ 50 mil", "R$ 100 mil"],
    ["Prazo complementar", "12 meses", "24 meses"],
  ],
  {
    x: 0.7,
    y: 2.0,
    w: 11.9,
    h: 3.25,
    colW: [4.2, 3.85, 3.85],
    fontFace: "Aptos",
    fontSize: 22,
    color: C.ink,
    border: { type: "solid", color: C.line, pt: 0.7 },
    margin: 12,
    fill: "FFFFFF",
    rowH: 0.65,
    autoPage: false,
  },
);
text(
  s,
  "10 diferenças textuais entre 16 critérios dos exemplos.",
  0.7,
  5.62,
  11.8,
  0.6,
  25,
  { bold: true },
);
text(
  s,
  "Valores sintéticos. A comparação não recomenda uma contratação.",
  0.7,
  6.3,
  11.8,
  0.4,
  17,
  { color: C.muted },
);
s.addNotes(
  "Fonte: backend/demo.py e comparação determinística. Não é benchmark de precisão da IA nem comparação de produtos reais.",
);
s = base("Validação e limitações", 7);
text(s, "18 testes automatizados", 0.7, 2, 11.6, 0.7, 32, { bold: true });
text(
  s,
  "Leitura de documentos, evidências, persistência, comparação e exportações. Fluxo de interface verificado em desktop e celular.",
  0.7,
  3.1,
  11.3,
  1.3,
  24,
  { color: C.muted },
);
text(
  s,
  "Pendente: validar uma chamada real de IA com a chave da equipe.",
  0.7,
  5.02,
  11.7,
  0.9,
  26,
  { color: C.accent, bold: true },
);
text(
  s,
  "Os testes usam respostas controladas. Ainda não há avaliação de precisão em apólices de mercado.",
  0.7,
  6.08,
  11.7,
  0.6,
  18,
  { color: C.muted },
);
s.addNotes(
  "Resultados da execução local de tests/test_pipeline.py e scripts/check_ui.py. Não houve acesso a credencial de IA. Comparação é textual e revisão humana continua necessária.",
);
s = base("Próximos passos da equipe", 8);
text(
  s,
  "Validação com documentos reais\ne revisão por especialistas",
  0.7,
  2,
  11.7,
  1.5,
  34,
  { bold: true },
);
text(
  s,
  "Evolução: múltiplas evidências por campo, comparação semântica, revisão versionada e fila persistente.",
  0.7,
  3.96,
  11.6,
  1.15,
  24,
  { color: C.muted },
);
text(
  s,
  "Entrega: identificar integrantes, concluir a demonstração com IA e tornar o repositório público.",
  0.7,
  5.47,
  11.5,
  1.1,
  23,
  { color: C.accent },
);
s.addNotes(
  "Prazo do enunciado: 06/10/2026 às 23h59. Repositório público: https://github.com/vicTmm/i2a2-desafio-final. A validação com IA real e a identificação nominal dos integrantes ainda precisam ser concluídas.",
);
await pptx.writeFile({
  fileName: path.join(out, "InsurMinds_Projeto_Final.pptx"),
});
console.log("Pitch: 8 slides editáveis.");
