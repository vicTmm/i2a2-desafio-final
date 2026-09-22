from typing import Literal
from pydantic import BaseModel, ConfigDict, Field

FIELDS = {
    "insurer": ("Seguradora", "Identificação"),
    "insured": ("Segurado", "Identificação"),
    "policy_number": ("Número da apólice", "Identificação"),
    "period": ("Vigência", "Condições"),
    "limit": ("Limite de responsabilidade", "Condições"),
    "premium": ("Prêmio total", "Condições"),
    "deductible": ("Franquia / participação", "Condições"),
    "territory": ("Abrangência territorial", "Condições"),
    "side_a": ("Side A · Administradores", "Coberturas"),
    "side_b": ("Side B · Reembolso à empresa", "Coberturas"),
    "side_c": ("Side C · Valores mobiliários", "Coberturas"),
    "defense": ("Custos de defesa", "Coberturas"),
    "investigation": ("Investigações", "Coberturas"),
    "exclusions": ("Exclusões", "Exclusões"),
    "retroactivity": ("Retroatividade", "Condições"),
    "reporting": ("Prazo complementar", "Condições"),
}

class Fact(BaseModel):
    model_config = ConfigDict(extra="forbid")
    key: str
    value: str | None
    quote: str | None
    page: int | None

class Extraction(BaseModel):
    model_config = ConfigDict(extra="forbid")
    document_type: Literal["do_policy", "other", "uncertain"]
    title: str
    facts: list[Fact]
    warnings: list[str]

class CompareRequest(BaseModel):
    policy_ids: list[str] = Field(min_length=2, max_length=4)

class QuestionRequest(BaseModel):
    question: str = Field(min_length=3, max_length=1000)
