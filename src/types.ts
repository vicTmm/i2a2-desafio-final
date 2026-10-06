export type Evidence = {
  quote: string;
  page: number;
  evidence_status: "verified" | "visual_review";
};
export type Fact = {
  key: string;
  value: string | null;
  quote: string | null;
  page: number | null;
  evidence_status: "verified" | "visual_review" | "missing";
  evidence?: Evidence[];
  variants?: { value: string; evidence: Evidence[] }[];
  needs_review?: boolean;
};
export type Policy = {
  id: string;
  title: string;
  filename: string;
  status: "queued" | "reading" | "extracting" | "ready" | "error";
  demo: boolean;
  created_at: string;
  facts: Fact[];
  warnings: string[];
  model: string;
  error?: string;
  models_used?: string[];
  progress?: {
    completed_chunks: number;
    total_chunks: number;
    cached_chunks: number;
  };
  pages?: { page: number; text: string; visual: boolean }[];
};
export type Row = {
  key: string;
  label: string;
  group: string;
  status: "same" | "different" | "missing";
  cells: Fact[];
};
export type Comparison = {
  id: string;
  created_at: string;
  policies: Policy[];
  rows: Row[];
  summary: string;
};
export type Health = {
  ai_configured: boolean;
  model: string;
  fields: Record<string, [string, string]>;
};
