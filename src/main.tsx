import React, { useState, useEffect, useRef, useCallback } from "react";
import { createRoot } from "react-dom/client";
import {
  ShieldCheck,
  LayoutDashboard,
  Files,
  Columns3,
  History,
  Settings2,
  ArrowUpRight,
  ArrowRight,
  Plus,
  Search,
  Upload,
  FileText,
  Check,
  ChevronRight,
  ChevronDown,
  X,
  CircleHelp,
  Sparkles,
  ScanText,
  Download,
  CheckCheck,
  CircleAlert,
  LoaderCircle,
  ExternalLink,
  Send,
  Menu,
  SlidersHorizontal,
  BookOpen,
  Link2,
  CircleCheck,
  Layers3,
} from "lucide-react";
import type { Fact, Policy, Comparison, Health } from "./types";
import "./styles.css";

async function api<T>(path: string, options?: RequestInit): Promise<T> {
  const response = await fetch("/api" + path, options);
  const data = await response
    .json()
    .catch(() => ({ error: "Não foi possível conectar ao servidor." }));
  if (!response.ok)
    throw new Error(data.error || "A operação não pôde ser concluída.");
  return data;
}
const post = (body?: unknown): RequestInit => ({
  method: "POST",
  ...(body
    ? {
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(body),
      }
    : {}),
});
const getFact = (p: Policy, key: string) =>
  p.facts.find((f) => f.key === key)?.value;
const date = (s: string) =>
  new Date(s).toLocaleDateString("pt-BR", { day: "2-digit", month: "short" });
const statuses = {
  queued: "Na fila",
  reading: "Lendo documento",
  extracting: "Extraindo com IA",
  ready: "Analisada",
  error: "Falha na análise",
};
type Page =
  "overview" | "policies" | "compare" | "history" | "settings" | "guide";
const navItems = [
  { id: "overview", label: "Visão geral", icon: LayoutDashboard },
  { id: "policies", label: "Apólices", icon: Files },
  { id: "compare", label: "Comparar apólices", icon: Columns3 },
  { id: "history", label: "Histórico", icon: History },
] as const;

function Dialog({
  children,
  onClose,
  label,
  wide = false,
}: {
  children: React.ReactNode;
  onClose: () => void;
  label: string;
  wide?: boolean;
}) {
  const ref = useRef<HTMLDialogElement>(null);
  useEffect(() => {
    ref.current?.showModal();
    const old = document.body.style.overflow;
    document.body.style.overflow = "hidden";
    return () => {
      document.body.style.overflow = old;
    };
  }, []);
  return (
    <dialog
      ref={ref}
      className={wide ? "dialog wide" : "dialog"}
      aria-label={label}
      onCancel={onClose}
      onClick={(e) => {
        if (e.target === e.currentTarget) onClose();
      }}
    >
      <div className="dialog-head">
        <span className="eyebrow">{label}</span>
        <button className="icon-button" onClick={onClose} aria-label="Fechar">
          <X size={20} />
        </button>
      </div>
      {children}
    </dialog>
  );
}

function App() {
  const [page, setPage] = useState<Page>("overview");
  const [policies, setPolicies] = useState<Policy[]>([]);
  const [history, setHistory] = useState<Comparison[]>([]);
  const [health, setHealth] = useState<Health | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [toast, setToast] = useState("");
  const [busy, setBusy] = useState(false);
  const [query, setQuery] = useState("");
  const [filter, setFilter] = useState("all");
  const [selected, setSelected] = useState<string[]>([]);
  const [uploadOpen, setUploadOpen] = useState(false);
  const [detail, setDetail] = useState<{ policy: Policy; fact?: Fact } | null>(
    null,
  );
  const [comparison, setComparison] = useState<Comparison | null>(null);
  const [onlyDifferences, setOnlyDifferences] = useState(false);
  const [group, setGroup] = useState("Todos os critérios");
  const [mobileOpen, setMobileOpen] = useState(false);
  const ready = policies.filter((p) => p.status === "ready");
  const processing = policies.filter(
    (p) => !["ready", "error"].includes(p.status),
  );
  const refresh = useCallback(async () => {
    try {
      const [p, h, c] = await Promise.all([
        api<Policy[]>("/policies"),
        api<Health>("/health"),
        api<Comparison[]>("/comparisons"),
      ]);
      setPolicies(p);
      setHealth(h);
      setHistory(c);
      setError("");
    } catch (e) {
      setError((e as Error).message);
    } finally {
      setLoading(false);
    }
  }, []);
  useEffect(() => {
    void refresh();
  }, [refresh]);
  useEffect(() => {
    window.scrollTo(0, 0);
  }, [page]);
  useEffect(() => {
    if (!processing.length) return;
    const timer = setInterval(() => void refresh(), 2500);
    return () => clearInterval(timer);
  }, [processing.length, refresh]);
  useEffect(() => {
    if (!toast) return;
    const timer = setTimeout(() => setToast(""), 5000);
    return () => clearTimeout(timer);
  }, [toast]);
  function navigate(p: Page) {
    setPage(p);
    setMobileOpen(false);
    setQuery("");
  }
  function toggle(id: string) {
    setSelected((s) =>
      s.includes(id)
        ? s.filter((x) => x !== id)
        : s.length < 4
          ? [...s, id]
          : s,
    );
  }
  async function loadDemo() {
    setBusy(true);
    try {
      const p = await api<Policy[]>("/demo", post());
      setPolicies(p);
      setToast("Dois exemplos fictícios adicionados à sua biblioteca.");
    } catch (e) {
      setError((e as Error).message);
    } finally {
      setBusy(false);
    }
  }
  async function compare() {
    setBusy(true);
    try {
      const c = await api<Comparison>(
        "/comparisons",
        post({ policy_ids: selected }),
      );
      setComparison(c);
      setPage("compare");
      setGroup("Todos os critérios");
      setOnlyDifferences(false);
      await refresh();
    } catch (e) {
      setError((e as Error).message);
    } finally {
      setBusy(false);
    }
  }
  async function openDetail(p: Policy, fact?: Fact) {
    try {
      const full = await api<Policy>("/policies/" + p.id);
      setDetail({ policy: full, fact });
    } catch (e) {
      setError((e as Error).message);
    }
  }
  const displayed = policies.filter(
    (p) =>
      `${p.title} ${p.filename} ${getFact(p, "insurer") || ""}`
        .toLowerCase()
        .includes(query.toLowerCase()) &&
      (filter === "all" || (filter === "demo" ? p.demo : p.status === filter)),
  );
  function policyTable(compact = false) {
    return (
      <div className="table-wrap">
        <table className="policy-table">
          <thead>
            <tr>
              <th className="check-cell">
                <input
                  type="checkbox"
                  aria-label="Selecionar até quatro apólices visíveis"
                  checked={
                    displayed.filter((p) => p.status === "ready").length > 0 &&
                    displayed
                      .filter((p) => p.status === "ready")
                      .slice(0, 4)
                      .every((p) => selected.includes(p.id))
                  }
                  onChange={(e) =>
                    setSelected(
                      e.target.checked
                        ? displayed
                            .filter((p) => p.status === "ready")
                            .slice(0, 4)
                            .map((p) => p.id)
                        : [],
                    )
                  }
                />
              </th>
              <th>Apólice / seguradora</th>
              <th>Status</th>
              <th>Limite de responsabilidade</th>
              {!compact && <th>Adicionada em</th>}
              <th aria-label="Ações" />
            </tr>
          </thead>
          <tbody>
            {displayed.slice(0, compact ? 5 : undefined).map((p) => (
              <tr
                key={p.id}
                className={selected.includes(p.id) ? "selected-row" : ""}
              >
                <td>
                  <input
                    type="checkbox"
                    aria-label={"Selecionar " + p.title}
                    checked={selected.includes(p.id)}
                    disabled={
                      p.status !== "ready" ||
                      (!selected.includes(p.id) && selected.length >= 4)
                    }
                    onChange={() => toggle(p.id)}
                  />
                </td>
                <td>
                  <button
                    className="policy-name"
                    onClick={() => void openDetail(p)}
                  >
                    <span className="file-symbol">
                      <FileText size={21} />
                    </span>
                    <span>
                      <strong>{p.title}</strong>
                      <small>
                        {getFact(p, "insurer") || p.filename}
                        {p.demo && <span className="demo-tag">Exemplo</span>}
                      </small>
                    </span>
                  </button>
                </td>
                <td>
                  <span className={"status " + p.status}>
                    {p.status === "ready" ? (
                      <span className="status-dot" />
                    ) : p.status === "error" ? (
                      <CircleAlert size={12} />
                    ) : (
                      <LoaderCircle className="spin" size={12} />
                    )}{" "}
                    {statuses[p.status]}
                  </span>
                </td>
                <td className="money">
                  {getFact(p, "limit")?.replace("BRL", "R$") || "—"}
                </td>
                {!compact && <td className="muted">{date(p.created_at)}</td>}
                <td>
                  <button
                    className="icon-button"
                    aria-label={"Ver " + p.title}
                    onClick={() => void openDetail(p)}
                  >
                    <ArrowUpRight size={17} />
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
        {!displayed.length && (
          <div className="empty-state">
            <Files size={30} />
            <h3>
              {query || filter !== "all"
                ? "Nenhuma apólice encontrada"
                : "Sua biblioteca começa aqui"}
            </h3>
            <p>
              {query || filter !== "all"
                ? "Experimente outro termo ou filtro."
                : "Envie um documento ou explore os dois exemplos fictícios."}
            </p>
            {!query && filter === "all" && (
              <button
                className="text-button"
                onClick={() => void loadDemo()}
                disabled={busy}
              >
                Explorar exemplos <ArrowRight size={15} />
              </button>
            )}
          </div>
        )}
      </div>
    );
  }

  return (
    <div className="app-shell">
      <aside className={"sidebar " + (mobileOpen ? "open" : "")}>
        <a
          className="brand"
          href="#"
          onClick={(e) => {
            e.preventDefault();
            navigate("overview");
          }}
        >
          <span className="brand-mark">
            <ShieldCheck size={25} />
          </span>
          InsurMinds<span className="brand-dot">.</span>
        </a>
        <div className="workspace">
          <span className="workspace-avatar">IM</span>
          <div>
            <strong>Workspace do projeto</strong>
            <small>I2A2 · Turma 2026</small>
          </div>
          <Layers3 size={16} />
        </div>
        <span className="nav-caption">PLATAFORMA</span>
        <nav aria-label="Navegação principal">
          {navItems.map((n) => (
            <button
              key={n.id}
              className={"nav-item " + (page === n.id ? "active" : "")}
              onClick={() => navigate(n.id)}
            >
              <n.icon size={19} />
              <span>{n.label}</span>
              {n.id === "policies" && (
                <span className="nav-count">{policies.length}</span>
              )}
            </button>
          ))}
        </nav>
        <div className="sidebar-bottom">
          <div className="sidebar-note">
            <span className="note-icon">
              <Sparkles size={18} />
            </span>
            <h4>
              Uma nova perspectiva
              <br />
              sobre suas apólices.
            </h4>
            <p>Transforme documentos em informações para sua análise.</p>
            <button onClick={() => navigate("guide")}>
              Conheça o processo <ArrowUpRight size={15} />
            </button>
          </div>
          <button
            className={"nav-item " + (page === "settings" ? "active" : "")}
            onClick={() => navigate("settings")}
          >
            <Settings2 size={18} />
            Configurações
          </button>
          <button className="nav-item" onClick={() => navigate("guide")}>
            <CircleHelp size={18} />
            Guia de uso
          </button>
          <div className="profile">
            <span className="profile-avatar">IM</span>
            <div>
              <strong>Equipe InsurMinds</strong>
              <small>Projeto acadêmico</small>
            </div>
            <span className="local-dot" title="Ambiente local" />
          </div>
        </div>
      </aside>
      {mobileOpen && (
        <button
          className="nav-backdrop"
          aria-label="Fechar navegação"
          onClick={() => setMobileOpen(false)}
        />
      )}
      <div className="main-shell">
        <header className="topbar">
          <div className="breadcrumb">
            <button
              className="icon-button mobile-menu"
              aria-label="Abrir navegação"
              onClick={() => setMobileOpen(true)}
            >
              <Menu size={20} />
            </button>
            <span>Workspace</span>
            <ChevronRight size={14} />
            <strong>
              {navItems.find((n) => n.id === page)?.label ||
                (page === "settings" ? "Configurações" : "Guia de uso")}
            </strong>
          </div>
          <div className="topbar-right">
            <span className="project-label">PROJETO FINAL · I2A2</span>
            <span className="topbar-divider" />
            <button
              className="icon-button"
              title="Guia de uso"
              aria-label="Guia de uso"
              onClick={() => navigate("guide")}
            >
              <CircleHelp size={18} />
            </button>
            <span className="small-avatar">IM</span>
          </div>
        </header>
        <main id="main-content">
          {error && (
            <div className="error-banner" role="alert">
              <CircleAlert size={18} />
              <span>{error}</span>
              <button className="text-button" onClick={() => void refresh()}>
                Tentar novamente
              </button>
              <button
                className="icon-button"
                aria-label="Dispensar erro"
                onClick={() => setError("")}
              >
                <X size={16} />
              </button>
            </div>
          )}
          {loading ? (
            <div className="loading">
              <LoaderCircle className="spin" />
              Carregando seu workspace…
            </div>
          ) : (
            <>
              {page === "overview" && (
                <>
                  <div className="page-heading">
                    <div>
                      <div className="eyebrow">INTELIGÊNCIA EM SEGUROS D&O</div>
                      <h1>
                        Visão geral<span className="heading-dot">.</span>
                      </h1>
                      <p>
                        Menos tempo entre documentos. Mais clareza na sua
                        análise.
                      </p>
                    </div>
                    <button
                      className="primary"
                      onClick={() => setUploadOpen(true)}
                    >
                      <Plus size={18} />
                      Nova análise
                    </button>
                  </div>
                  <section className="hero">
                    <div className="hero-copy">
                      <span className="hero-label">
                        <span /> ANÁLISE ASSISTIDA POR IA
                      </span>
                      <h2>
                        Os detalhes fazem
                        <br />
                        toda a diferença.
                      </h2>
                      <p>
                        Compare coberturas, identifique diferenças e
                        <br className="desktop-break" /> encontre as evidências
                        em cada apólice.
                      </p>
                      <button
                        className="hero-button"
                        onClick={() => {
                          navigate("compare");
                          setComparison(null);
                        }}
                      >
                        Comparar apólices <ArrowRight size={17} />
                      </button>
                    </div>
                    <div className="hero-art" aria-hidden="true">
                      <div className="orbit orbit-one" />
                      <div className="orbit orbit-two" />
                      <div className="art-card art-back">
                        <div className="art-card-title">
                          <div className="art-logo pale" />
                          <span>APÓLICE B</span>
                          <Check size={13} />
                        </div>
                        <div className="art-line long" />
                        <div className="art-line" />
                        <div className="art-value">D&O</div>
                        <div className="art-separator" />
                        <div className="art-line long" />
                        <div className="art-line short" />
                      </div>
                      <div className="art-card art-front">
                        <div className="art-card-title">
                          <div className="art-logo" />
                          <span>APÓLICE A</span>
                          <Check size={13} />
                        </div>
                        <div className="art-line long" />
                        <div className="art-line" />
                        <div className="art-value">D&O</div>
                        <div className="art-separator" />
                        <div className="art-row">
                          <div className="art-line long" />
                          <span className="art-check">
                            <Check size={12} />
                          </span>
                        </div>
                        <div className="art-row">
                          <div className="art-line" />
                          <span className="art-check">
                            <Check size={12} />
                          </span>
                        </div>
                      </div>
                      <div className="art-spark">
                        <Sparkles size={26} />
                      </div>
                      <span className="art-caption">
                        <Link2 size={13} /> Cada informação, uma evidência.
                      </span>
                    </div>
                  </section>
                  <section
                    className="metrics"
                    aria-label="Indicadores do workspace"
                  >
                    {[
                      {
                        label: "Apólices na biblioteca",
                        value: policies.length,
                        icon: Files,
                        sub: "Documentos organizados",
                      },
                      {
                        label: "Análises concluídas",
                        value: ready.length,
                        icon: ScanText,
                        sub: processing.length
                          ? `${processing.length} em processamento`
                          : "Prontas para consultar",
                      },
                      {
                        label: "Comparações realizadas",
                        value: history.length,
                        icon: Columns3,
                        sub: "Salvas no seu histórico",
                      },
                      {
                        label: "Critérios por comparação",
                        value: 16,
                        icon: CheckCheck,
                        sub: "Com referência à origem",
                      },
                    ].map((m, i) => (
                      <div className="metric" key={m.label}>
                        <div className="metric-top">
                          <span>{m.label}</span>
                          <m.icon size={18} />
                        </div>
                        <strong>{String(m.value).padStart(2, "0")}</strong>
                        <small>
                          {i === 1 && <span className="tiny-dot" />}
                          {m.sub}
                        </small>
                      </div>
                    ))}
                  </section>
                  <section className="library-section">
                    <div className="section-heading">
                      <div>
                        <h2>
                          Apólices recentes{" "}
                          <span className="count-badge">{policies.length}</span>
                        </h2>
                        <p>Seus documentos, organizados em um só lugar.</p>
                      </div>
                      <button
                        className="text-button"
                        onClick={() => navigate("policies")}
                      >
                        Ver todas <ArrowRight size={16} />
                      </button>
                    </div>
                    {policyTable(true)}
                  </section>
                  <section className="bottom-grid">
                    <button
                      className="upload-promo"
                      onClick={() => setUploadOpen(true)}
                    >
                      <span className="upload-symbol">
                        <Upload size={24} />
                      </span>
                      <div>
                        <h3>Da apólice à análise</h3>
                        <p>
                          Adicione PDFs ou imagens e deixe a IA organizar as
                          informações.
                        </p>
                        <span>
                          Enviar documentos <ArrowUpRight size={14} />
                        </span>
                      </div>
                      <Plus size={20} />
                    </button>
                    <div className="demo-promo">
                      <span className="eyebrow">EXPLORE NA PRÁTICA</span>
                      <h3>Primeira vez por aqui?</h3>
                      <p>Conheça a comparação com duas apólices fictícias.</p>
                      <button
                        className="text-button"
                        onClick={() => void loadDemo()}
                        disabled={busy}
                      >
                        {busy ? (
                          <LoaderCircle className="spin" size={15} />
                        ) : (
                          <BookOpen size={15} />
                        )}{" "}
                        Carregar exemplos <ArrowRight size={15} />
                      </button>
                    </div>
                  </section>
                </>
              )}
              {page === "policies" && (
                <>
                  <div className="page-heading">
                    <div>
                      <div className="eyebrow">SEUS DOCUMENTOS</div>
                      <h1>
                        Biblioteca de apólices
                        <span className="heading-dot">.</span>
                      </h1>
                      <p>
                        Consulte as informações e confira a origem de cada
                        extração.
                      </p>
                    </div>
                    <button
                      className="primary"
                      onClick={() => setUploadOpen(true)}
                    >
                      <Plus size={18} />
                      Nova análise
                    </button>
                  </div>
                  <div className="toolbar">
                    <label className="search">
                      <Search size={17} />
                      <input
                        placeholder="Buscar apólice ou seguradora…"
                        value={query}
                        onChange={(e) => setQuery(e.target.value)}
                      />
                    </label>
                    <label className="select-wrap">
                      <SlidersHorizontal size={16} />
                      <select
                        aria-label="Filtrar apólices"
                        value={filter}
                        onChange={(e) => setFilter(e.target.value)}
                      >
                        <option value="all">Todos os status</option>
                        <option value="ready">Analisadas</option>
                        <option value="extracting">Em extração</option>
                        <option value="error">Com falha</option>
                        <option value="demo">Exemplos fictícios</option>
                      </select>
                      <ChevronDown size={14} />
                    </label>
                  </div>
                  <div className="library-section standalone">
                    {policyTable()}
                  </div>
                  <div className="library-footer">
                    <span>
                      {displayed.length} documento
                      {displayed.length !== 1 ? "s" : ""}
                    </span>
                    <span>Selecione de 2 a 4 apólices para comparar</span>
                  </div>
                </>
              )}
              {page === "compare" && (
                <>
                  <div className="page-heading">
                    <div>
                      <div className="eyebrow">ANÁLISE LADO A LADO</div>
                      <h1>
                        Comparar apólices<span className="heading-dot">.</span>
                      </h1>
                      <p>
                        Entenda as diferenças e confira as condições de cada
                        documento.
                      </p>
                    </div>
                    {comparison ? (
                      <button
                        className="secondary"
                        onClick={() => setComparison(null)}
                      >
                        <Plus size={17} />
                        Nova comparação
                      </button>
                    ) : (
                      <button
                        className="primary"
                        disabled={selected.length < 2 || busy}
                        onClick={() => void compare()}
                      >
                        {busy ? (
                          <LoaderCircle className="spin" size={17} />
                        ) : (
                          <Columns3 size={17} />
                        )}
                        Comparar{" "}
                        {selected.length > 0 ? `(${selected.length})` : ""}
                      </button>
                    )}
                  </div>
                  {!comparison ? (
                    <>
                      <div className="selection-instruction">
                        <span className="step-circle">1</span>
                        <div>
                          <h3>Escolha suas apólices</h3>
                          <p>
                            Selecione de 2 a 4 documentos com a análise
                            concluída.
                          </p>
                        </div>
                        <span className="selection-count">
                          {selected.length} / 4 selecionadas
                        </span>
                      </div>
                      <div className="policy-cards">
                        {ready.map((p) => (
                          <button
                            className={
                              "select-policy " +
                              (selected.includes(p.id) ? "chosen" : "")
                            }
                            key={p.id}
                            aria-pressed={selected.includes(p.id)}
                            disabled={
                              !selected.includes(p.id) && selected.length >= 4
                            }
                            onClick={() => toggle(p.id)}
                          >
                            <div className="select-policy-top">
                              <span className="file-symbol">
                                <FileText size={24} />
                              </span>
                              <span className="fake-checkbox">
                                {selected.includes(p.id) && <Check size={14} />}
                              </span>
                            </div>
                            <small>
                              {p.demo ? "DOCUMENTO FICTÍCIO" : "APÓLICE D&O"}
                            </small>
                            <h3>{p.title}</h3>
                            <p>{getFact(p, "insurer") || p.filename}</p>
                            <div className="policy-card-limit">
                              <span>Limite de responsabilidade</span>
                              <strong>
                                {getFact(p, "limit")?.replace("BRL", "R$") ||
                                  "Não identificado"}
                              </strong>
                            </div>
                          </button>
                        ))}
                      </div>
                      {ready.length < 2 && (
                        <div className="empty-state">
                          <Columns3 size={32} />
                          <h3>Uma boa análise começa com duas apólices</h3>
                          <p>
                            Envie seus documentos ou carregue os exemplos para
                            experimentar.
                          </p>
                          <button
                            className="secondary"
                            disabled={busy}
                            onClick={() => void loadDemo()}
                          >
                            Carregar exemplos fictícios
                          </button>
                        </div>
                      )}
                      <div className="info-note">
                        <Link2 size={18} />
                        <p>
                          Os valores da comparação preservam as condições
                          extraídas. Clique em uma informação para consultar seu
                          trecho de origem.
                        </p>
                      </div>
                    </>
                  ) : (
                    <>
                      <div className="comparison-summary">
                        <div className="summary-icon">
                          <Sparkles size={22} />
                        </div>
                        <div>
                          <span className="eyebrow">RESUMO DA COMPARAÇÃO</span>
                          <p>{comparison.summary}</p>
                          {comparison.policies.some((p) => p.demo) && (
                            <small>
                              Contém exemplos fictícios com dados
                              pré-preenchidos.
                            </small>
                          )}
                        </div>
                        <a
                          className="secondary"
                          href={"/api/comparisons/" + comparison.id + "/export"}
                        >
                          <Download size={16} />
                          Exportar PDF
                        </a>
                      </div>
                      <div className="toolbar">
                        <div className="group-tabs">
                          {[
                            "Todos os critérios",
                            "Condições",
                            "Coberturas",
                            "Exclusões",
                          ].map((g) => (
                            <button
                              key={g}
                              className={group === g ? "active" : ""}
                              onClick={() => setGroup(g)}
                            >
                              {g}
                            </button>
                          ))}
                        </div>
                        <label className="switch-label">
                          <input
                            type="checkbox"
                            checked={onlyDifferences}
                            onChange={(e) =>
                              setOnlyDifferences(e.target.checked)
                            }
                          />
                          <span className="switch" />
                          Só diferenças e ausências
                        </label>
                      </div>
                      <div className="comparison-table-wrap">
                        <table className="comparison-table">
                          <thead>
                            <tr>
                              <th>
                                Critério de análise{" "}
                                <small>
                                  {comparison.rows.length} critérios disponíveis
                                </small>
                              </th>
                              {comparison.policies.map((p) => (
                                <th key={p.id}>
                                  <span className="column-mark" />
                                  {p.title}
                                  <small>{getFact(p, "insurer")}</small>
                                </th>
                              ))}
                            </tr>
                          </thead>
                          <tbody>
                            {comparison.rows
                              .filter(
                                (r) =>
                                  (group === "Todos os critérios" ||
                                    r.group === group) &&
                                  (!onlyDifferences || r.status !== "same"),
                              )
                              .map((r) => (
                                <tr key={r.key}>
                                  <th>
                                    {r.label}
                                    <span
                                      className={"difference-label " + r.status}
                                    >
                                      {r.status === "same"
                                        ? "Valores iguais"
                                        : r.status === "different"
                                          ? "Diferença textual"
                                          : "Informação ausente"}
                                    </span>
                                  </th>
                                  {r.cells.map((f, i) => (
                                    <td key={comparison.policies[i].id}>
                                      <button
                                        className="evidence-cell"
                                        onClick={() =>
                                          void openDetail(
                                            comparison.policies[i],
                                            f,
                                          )
                                        }
                                      >
                                        <span>
                                          {f.value || "Não identificado"}
                                        </span>
                                        <small>
                                          {f.page ? (
                                            <>
                                              <Link2 size={12} />
                                              Página {f.page}
                                              <ArrowUpRight size={12} />
                                            </>
                                          ) : (
                                            <>
                                              <CircleAlert size={12} />
                                              Conferir documento
                                            </>
                                          )}
                                        </small>
                                      </button>
                                    </td>
                                  ))}
                                </tr>
                              ))}
                          </tbody>
                        </table>
                      </div>
                      <div className="library-footer">
                        <span>
                          Comparação textual · Validação humana necessária
                        </span>
                        <a
                          href={
                            "/api/comparisons/" +
                            comparison.id +
                            "/export?format=json"
                          }
                        >
                          Baixar dados JSON <Download size={13} />
                        </a>
                      </div>
                    </>
                  )}
                </>
              )}
              {page === "history" && (
                <>
                  <div className="page-heading">
                    <div>
                      <div className="eyebrow">REGISTRO DAS ANÁLISES</div>
                      <h1>
                        Histórico<span className="heading-dot">.</span>
                      </h1>
                      <p>
                        Retome comparações e exporte os resultados quando
                        precisar.
                      </p>
                    </div>
                    <button
                      className="primary"
                      onClick={() => {
                        navigate("compare");
                        setComparison(null);
                      }}
                    >
                      <Plus size={17} />
                      Nova comparação
                    </button>
                  </div>
                  <div className="history-list">
                    {history.map((c) => (
                      <div className="history-item" key={c.id}>
                        <span className="file-symbol">
                          <Columns3 size={22} />
                        </span>
                        <div>
                          <h3>{c.policies.map((p) => p.title).join(" × ")}</h3>
                          <p>
                            {date(c.created_at)} · {c.policies.length} apólices
                            ·{" "}
                            {
                              c.rows.filter((r) => r.status === "different")
                                .length
                            }{" "}
                            diferenças textuais
                          </p>
                        </div>
                        <a
                          className="icon-button"
                          aria-label="Exportar comparação em PDF"
                          href={"/api/comparisons/" + c.id + "/export"}
                        >
                          <Download size={18} />
                        </a>
                        <button
                          className="secondary"
                          onClick={() => {
                            setComparison(c);
                            setPage("compare");
                            setOnlyDifferences(false);
                            setGroup("Todos os critérios");
                          }}
                        >
                          Abrir <ArrowRight size={15} />
                        </button>
                      </div>
                    ))}
                  </div>
                  {!history.length && (
                    <div className="empty-state bordered">
                      <History size={32} />
                      <h3>Suas comparações vão aparecer aqui</h3>
                      <p>
                        Compare duas apólices para salvar sua primeira análise.
                      </p>
                      <button
                        className="text-button"
                        onClick={() => navigate("compare")}
                      >
                        Começar comparação <ArrowRight size={15} />
                      </button>
                    </div>
                  )}
                </>
              )}
              {page === "settings" && (
                <>
                  <div className="page-heading">
                    <div>
                      <div className="eyebrow">AMBIENTE DO PROJETO</div>
                      <h1>
                        Configurações<span className="heading-dot">.</span>
                      </h1>
                      <p>Informações sobre processamento e armazenamento.</p>
                    </div>
                  </div>
                  <div className="settings-panel">
                    <div className="settings-row">
                      <span className="file-symbol">
                        <Sparkles size={22} />
                      </span>
                      <div>
                        <h3>Integração com OpenAI</h3>
                        <p>Modelo configurado: {health?.model}</p>
                      </div>
                      <span
                        className={
                          "status " +
                          (health?.ai_configured ? "ready" : "queued")
                        }
                      >
                        {health?.ai_configured
                          ? "Chave configurada"
                          : "Chave pendente"}
                      </span>
                    </div>
                    <div className="settings-body">
                      <p>
                        Para analisar novos documentos, copie{" "}
                        <code>.env.example</code> para <code>.env</code> na
                        pasta do projeto e preencha <code>OPENAI_API_KEY</code>.
                        Reinicie a API após a alteração.
                      </p>
                      <p>
                        A chave fica no servidor. O conteúdo enviado para
                        análise é processado pela API da OpenAI.
                      </p>
                      <button
                        className="secondary"
                        onClick={() => void refresh()}
                      >
                        Atualizar status
                      </button>
                    </div>
                  </div>
                  <div className="settings-panel">
                    <div className="settings-row">
                      <span className="file-symbol">
                        <Layers3 size={22} />
                      </span>
                      <div>
                        <h3>Armazenamento local</h3>
                        <p>SQLite e arquivos na pasta data/</p>
                      </div>
                      <span className="status ready">Ambiente local</span>
                    </div>
                    <div className="settings-body">
                      <p>
                        Os documentos e as comparações persistem ao reiniciar o
                        aplicativo. Este MVP foi projetado para uma demonstração
                        local com um workspace compartilhado.
                      </p>
                    </div>
                  </div>
                </>
              )}
              {page === "guide" && (
                <>
                  <div className="page-heading">
                    <div>
                      <div className="eyebrow">COMO FUNCIONA</div>
                      <h1>
                        Da leitura à comparação
                        <span className="heading-dot">.</span>
                      </h1>
                      <p>
                        Um processo simples, com evidências que você pode
                        conferir.
                      </p>
                    </div>
                  </div>
                  <div className="guide-steps">
                    {[
                      {
                        title: "Adicione seus documentos",
                        text: "Envie PDFs, PNG, JPG ou WebP. O limite é de 20 MB, 60 páginas por PDF e até 20 páginas digitalizadas.",
                        icon: Upload,
                      },
                      {
                        title: "Acompanhe a extração",
                        text: "A leitura combina extração de texto e visão multimodal. A IA estrutura 16 critérios, incluindo coberturas, exclusões, franquias e limites.",
                        icon: ScanText,
                      },
                      {
                        title: "Confira as evidências",
                        text: "Cada dado apresenta o trecho e a página de origem. Trechos de texto são conferidos automaticamente. Dados de imagens precisam de revisão visual.",
                        icon: Link2,
                      },
                      {
                        title: "Compare e compartilhe",
                        text: "Selecione de 2 a 4 apólices, filtre as diferenças e exporte a tabela e suas evidências em PDF ou JSON.",
                        icon: Columns3,
                      },
                    ].map((s, i) => (
                      <div className="guide-step" key={s.title}>
                        <span className="step-circle">{i + 1}</span>
                        <div>
                          <h3>{s.title}</h3>
                          <p>{s.text}</p>
                        </div>
                        <s.icon size={25} />
                      </div>
                    ))}
                  </div>
                  <div className="info-note">
                    <CircleAlert size={20} />
                    <p>
                      O aplicativo apoia a leitura documental. Diferenças
                      textuais exigem interpretação das condições contratuais.
                      Um campo não identificado não indica ausência de
                      cobertura.
                    </p>
                  </div>
                  <button
                    className="primary"
                    onClick={() => setUploadOpen(true)}
                  >
                    <Plus size={17} />
                    Começar uma análise
                  </button>
                </>
              )}
            </>
          )}
          <footer className="page-footer">
            <span>
              <ShieldCheck size={14} />
              InsurMinds · Inteligência com evidência.
            </span>
            <span>
              MVP acadêmico <span className="footer-dot">·</span> I2A2 2026
            </span>
          </footer>
        </main>
      </div>
      {selected.length > 0 && !(page === "compare" && comparison) && (
        <div className="selection-bar">
          <span>
            <span className="selected-number">{selected.length}</span> apólice
            {selected.length > 1 ? "s" : ""} selecionada
            {selected.length > 1 ? "s" : ""}
          </span>
          <button className="text-button" onClick={() => setSelected([])}>
            Limpar
          </button>
          <button
            className="primary"
            disabled={selected.length < 2 || busy}
            onClick={() => void compare()}
          >
            {busy ? (
              <LoaderCircle className="spin" size={16} />
            ) : (
              <Columns3 size={16} />
            )}
            Comparar apólices <ArrowRight size={15} />
          </button>
        </div>
      )}
      {toast && (
        <div className="toast" role="status">
          <CircleCheck size={19} />
          {toast}
          <button
            className="icon-button"
            aria-label="Fechar notificação"
            onClick={() => setToast("")}
          >
            <X size={16} />
          </button>
        </div>
      )}
      {uploadOpen && (
        <UploadDialog
          configured={!!health?.ai_configured}
          onClose={() => setUploadOpen(false)}
          onUploaded={() => {
            void refresh();
            setToast("Documento recebido. Acompanhe a análise na biblioteca.");
            setPage("policies");
          }}
          onDemo={async () => {
            await loadDemo();
            setUploadOpen(false);
          }}
        />
      )}
      {detail && (
        <DetailDialog
          policy={detail.policy}
          fact={detail.fact}
          health={health}
          onClose={() => setDetail(null)}
          onRetry={async () => {
            try {
              await api("/policies/" + detail.policy.id + "/retry", post());
              setDetail(null);
              void refresh();
            } catch (e) {
              setError((e as Error).message);
            }
          }}
        />
      )}
    </div>
  );
}

function UploadDialog({
  configured,
  onClose,
  onUploaded,
  onDemo,
}: {
  configured: boolean;
  onClose: () => void;
  onUploaded: () => void;
  onDemo: () => Promise<void>;
}) {
  const [files, setFiles] = useState<File[]>([]),
    [dragging, setDragging] = useState(false),
    [uploading, setUploading] = useState(false),
    [error, setError] = useState("");
  const input = useRef<HTMLInputElement>(null);
  function addFiles(list: FileList | null) {
    if (!list) return;
    const incoming = Array.from(list);
    if (incoming.some((f) => f.size > 20 * 1024 * 1024)) {
      setError("Cada arquivo deve ter até 20 MB.");
      return;
    }
    if (incoming.some((f) => !/\.(pdf|png|jpe?g|webp)$/i.test(f.name))) {
      setError("Use arquivos PDF, PNG, JPG ou WebP.");
      return;
    }
    setFiles((s) => [...s, ...incoming].slice(0, 4));
    setError("");
  }
  async function send() {
    setUploading(true);
    setError("");
    let completed = 0;
    try {
      for (const f of files) {
        const form = new FormData();
        form.append("file", f);
        await api("/upload", { method: "POST", body: form });
        completed++;
        onUploaded();
      }
      onClose();
    } catch (e) {
      setFiles((s) => s.slice(completed));
      setError((e as Error).message);
    } finally {
      setUploading(false);
    }
  }
  return (
    <Dialog
      label="NOVA ANÁLISE"
      onClose={() => {
        if (!uploading) onClose();
      }}
    >
      <h2>
        Adicione suas apólices<span className="heading-dot">.</span>
      </h2>
      <p className="dialog-description">
        A IA organiza as informações para você comparar.
      </p>
      {!configured && (
        <div className="info-note compact">
          <CircleAlert size={19} />
          <p>
            A chave de IA ainda não foi configurada no servidor.{" "}
            <button className="inline-link" onClick={() => void onDemo()}>
              Explorar exemplos fictícios
            </button>
          </p>
        </div>
      )}
      <button
        className={"dropzone " + (dragging ? "dragging" : "")}
        onClick={() => input.current?.click()}
        onDragOver={(e) => {
          e.preventDefault();
          setDragging(true);
        }}
        onDragLeave={() => setDragging(false)}
        onDrop={(e) => {
          e.preventDefault();
          setDragging(false);
          addFiles(e.dataTransfer.files);
        }}
        disabled={uploading}
      >
        <span className="upload-symbol">
          <Upload size={27} />
        </span>
        <strong>Arraste seus documentos até aqui</strong>
        <span>
          ou <u>selecione os arquivos</u>
        </span>
        <small>PDF, PNG, JPG ou WebP · Até 20 MB por arquivo</small>
      </button>
      <input
        ref={input}
        type="file"
        hidden
        multiple
        accept=".pdf,.png,.jpg,.jpeg,.webp"
        onChange={(e) => addFiles(e.target.files)}
      />
      {files.length > 0 && (
        <div className="file-queue">
          {files.map((f, i) => (
            <div key={i}>
              <FileText size={20} />
              <span>
                <strong>{f.name}</strong>
                <small>{(f.size / 1024 / 1024).toFixed(2)} MB</small>
              </span>
              <button
                className="icon-button"
                disabled={uploading}
                onClick={() => setFiles((s) => s.filter((_, n) => n !== i))}
                aria-label={"Remover " + f.name}
              >
                <X size={16} />
              </button>
            </div>
          ))}
        </div>
      )}
      {error && (
        <p className="inline-error" role="alert">
          {error}
        </p>
      )}
      <p className="upload-consent">
        <ShieldCheck size={15} />
        Ao analisar, o conteúdo dos documentos será enviado à OpenAI. Os
        arquivos ficam salvos neste workspace local.
      </p>
      <div className="dialog-actions">
        <button className="secondary" disabled={uploading} onClick={onClose}>
          Cancelar
        </button>
        <button
          className="primary"
          disabled={!configured || !files.length || uploading}
          onClick={() => void send()}
        >
          {uploading ? (
            <LoaderCircle className="spin" size={17} />
          ) : (
            <Sparkles size={17} />
          )}{" "}
          {uploading ? "Enviando…" : "Analisar documentos"}
        </button>
      </div>
    </Dialog>
  );
}

function DetailDialog({
  policy,
  fact,
  health,
  onClose,
  onRetry,
}: {
  policy: Policy;
  fact?: Fact;
  health: Health | null;
  onClose: () => void;
  onRetry: () => Promise<void>;
}) {
  const [tab, setTab] = useState<"facts" | "source" | "ask">(
    fact ? "source" : "facts",
  );
  const [chosen, setChosen] = useState<Fact | undefined>(fact);
  const [question, setQuestion] = useState(""),
    [answer, setAnswer] = useState(""),
    [busy, setBusy] = useState(false),
    [error, setError] = useState("");
  async function ask() {
    setBusy(true);
    setError("");
    try {
      const a = await api<{ answer: string }>(
        "/policies/" + policy.id + "/question",
        post({ question }),
      );
      setAnswer(a.answer);
    } catch (e) {
      setError((e as Error).message);
    } finally {
      setBusy(false);
    }
  }
  return (
    <Dialog label="DETALHES DA APÓLICE" wide onClose={onClose}>
      <div className="detail-title">
        <span className="file-symbol">
          <FileText size={25} />
        </span>
        <div>
          <h2>{policy.title}</h2>
          <p>{policy.filename}</p>
        </div>
      </div>
      {policy.demo && (
        <div className="demo-banner">
          <BookOpen size={16} />
          Documento fictício · Dados pré-preenchidos, sem processamento por IA.
        </div>
      )}
      <div className="detail-tabs">
        {(
          [
            { id: "facts", label: "Informações extraídas" },
            { id: "source", label: "Documento e evidências" },
            { id: "ask", label: "Consultar com IA" },
          ] as const
        ).map((t) => (
          <button
            key={t.id}
            className={tab === t.id ? "active" : ""}
            onClick={() => setTab(t.id)}
          >
            {t.label}
          </button>
        ))}
      </div>
      {policy.status === "error" ? (
        <div className="empty-state">
          <CircleAlert size={30} />
          <h3>A análise não foi concluída</h3>
          <p>{policy.error}</p>
          <button className="primary" onClick={() => void onRetry()}>
            Tentar novamente
          </button>
        </div>
      ) : policy.status !== "ready" ? (
        <div className="empty-state">
          <LoaderCircle className="spin" />
          <h3>{statuses[policy.status]}</h3>
          <p>Acompanhe o andamento na biblioteca.</p>
        </div>
      ) : (
        <>
          {tab === "facts" && (
            <div className="detail-facts">
              {policy.facts.map((f) => (
                <button
                  className="detail-fact"
                  key={f.key}
                  onClick={() => {
                    setChosen(f);
                    setTab("source");
                  }}
                >
                  <span>{health?.fields[f.key]?.[0] || f.key}</span>
                  <strong>{f.value || "Não identificado"}</strong>
                  <small>
                    {f.evidence_status === "verified" ? (
                      <CheckCheck size={13} />
                    ) : (
                      <CircleAlert size={13} />
                    )}{" "}
                    {f.page
                      ? `p. ${f.page} · ${f.evidence_status === "verified" ? "Trecho localizado" : "Revisão visual"}`
                      : "Sem evidência"}
                    <ArrowUpRight size={13} />
                  </small>
                </button>
              ))}
            </div>
          )}
          {tab === "source" && (
            <div className="source-content">
              {chosen && (
                <div className="quote-card">
                  <span className="eyebrow">
                    {health?.fields[chosen.key]?.[0]}{" "}
                    {chosen.page && `/ PÁGINA ${chosen.page}`}
                  </span>
                  <blockquote>
                    {chosen.quote
                      ? `“${chosen.quote}”`
                      : "Não foi identificada uma evidência para este critério. Confira o documento original."}
                  </blockquote>
                  <small>
                    {chosen.evidence_status === "verified"
                      ? "O trecho foi localizado no texto da página. A interpretação ainda precisa de revisão."
                      : "Confira visualmente a informação no documento."}
                  </small>
                </div>
              )}
              <div className="source-toolbar">
                <span>{policy.pages?.length || "—"} página(s)</span>
                <a
                  className="text-button"
                  href={
                    "/api/policies/" +
                    policy.id +
                    "/source#page=" +
                    (chosen?.page || 1)
                  }
                  target="_blank"
                  rel="noreferrer"
                >
                  Abrir original <ExternalLink size={14} />
                </a>
              </div>
              <div className="source-text">
                {(chosen?.page
                  ? policy.pages?.filter((p) => p.page === chosen.page)
                  : policy.pages
                )?.map((p) => (
                  <section key={p.page}>
                    <span className="page-label">PÁGINA {p.page}</span>
                    {p.text ? (
                      <pre>{p.text}</pre>
                    ) : (
                      <p>
                        Esta página foi lida visualmente. Abra o original para
                        conferir a imagem.
                      </p>
                    )}
                  </section>
                ))}
              </div>
            </div>
          )}
          {tab === "ask" && (
            <div className="ask-panel">
              <span className="note-icon">
                <Sparkles size={24} />
              </span>
              <h3>Consulte os dados desta apólice</h3>
              <p>
                A resposta considera as informações extraídas e cita as páginas
                disponíveis.
              </p>
              <div className="suggestions">
                {[
                  "Qual é o limite de responsabilidade?",
                  "Quais exclusões foram identificadas?",
                ].map((q) => (
                  <button key={q} onClick={() => setQuestion(q)}>
                    {q}
                  </button>
                ))}
              </div>
              <form
                onSubmit={(e) => {
                  e.preventDefault();
                  void ask();
                }}
              >
                <label className="sr-only" htmlFor="question">
                  Sua pergunta
                </label>
                <input
                  id="question"
                  value={question}
                  maxLength={1000}
                  onChange={(e) => setQuestion(e.target.value)}
                  placeholder="Pergunte sobre a apólice…"
                />
                <button
                  className="primary"
                  disabled={
                    busy || question.trim().length < 3 || !health?.ai_configured
                  }
                  aria-label="Enviar pergunta"
                >
                  {busy ? (
                    <LoaderCircle className="spin" size={18} />
                  ) : (
                    <Send size={18} />
                  )}
                </button>
              </form>
              {!health?.ai_configured && (
                <small>
                  Configure a chave de IA no servidor para fazer consultas.
                </small>
              )}
              {error && (
                <p className="inline-error" role="alert">
                  {error}
                </p>
              )}
              {answer && (
                <div className="ai-answer">
                  <span className="eyebrow">
                    RESPOSTA DA IA · CONFIRA AS FONTES
                  </span>
                  <p>{answer}</p>
                </div>
              )}
            </div>
          )}
          {policy.warnings.length > 0 && (
            <details className="warnings">
              <summary>
                <CircleAlert size={15} />
                Notas de revisão ({policy.warnings.length})
              </summary>
              {policy.warnings.map((w, i) => (
                <p key={i}>{w}</p>
              ))}
            </details>
          )}
        </>
      )}
    </Dialog>
  );
}

createRoot(document.getElementById("root")!).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>,
);
