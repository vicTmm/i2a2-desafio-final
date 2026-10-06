"""Atualiza o DOCX existente preservando seu template, imagens e tabelas."""
from pathlib import Path
from zipfile import ZipFile, ZIP_DEFLATED
from xml.etree import ElementTree as E
from io import BytesIO
from PIL import Image, ImageDraw, ImageFont
P=Path(__file__).resolve().parents[1]/'Projeto_Final_Artefatos/InsurMinds_System_Design.docx'
N={'w':'http://schemas.openxmlformats.org/wordprocessingml/2006/main'}
E.register_namespace('w',N['w'])
updates = {20: 'STATUS · MVP validado',
 22: 'RESPONSÁVEL · InsurMinds',
 24: 'REVISADO EM · 06/10/2026',
 26: 'Autores',
 28: 'Validação',
 29: 'Funcional com os PDFs fictícios do projeto',
 30: 'Documentação',
 32: 'Escopo',
 34: '1 Resumo',
 36: 'Limites: 20 MB, 300 páginas e 2 milhões de caracteres. O processamento usa blocos de até 60 mil '
     'caracteres, 20 páginas e 4 imagens. Evidências textuais são verificadas localmente; interpretações e '
     'leituras visuais exigem revisão humana.',
 38: '2 Objetivos e escopo',
 39: 'Objetivos',
 40: 'Fora do escopo',
 50: '3 Contexto e problema',
 51: 'Apólices D&O são extensas, heterogêneas e redigidas em linguagem jurídica. Comparar limites, '
     'franquias, coberturas e exclusões exige rastrear cada condição até sua página de origem.',
 53: '4 Arquitetura',
 58: 'Componentes',
 60: 'Componente',
 61: 'Responsabilidade',
 62: 'Persistência',
 63: 'Tratamento de falhas',
 77: 'Extrai JSON por bloco; retoma checkpoints.',
 78: 'Checkpoints locais / API Gemini',
 86: '5 Fluxo de processamento',
 88: 'A recepção valida conteúdo, tamanho, PDF criptografado e limites. A aplicação deve operar em loopback, '
     'sem autenticação ou isolamento multiusuário.',
 90: 'Cada bloco é enviado ao Gemini 3.8 Flash. Pydantic valida a estrutura e o verificador confere as '
     'citações nas páginas originais. A consolidação preserva múltiplas evidências e valores divergentes em '
     'variants, com needs_review.',
 92: 'Timeout de 90 segundos, até três tentativas por modelo, espera exponencial e intervalo mínimo de 15 '
     'segundos. Fallback para Gemini 3.7 em indisponibilidade, sem contornar cotas. Checkpoints atômicos '
     'permitem retomar blocos concluídos.',
 95: '6 Contratos de dados',
 96: 'Registro público da análise',
 98: 'Campo',
 99: 'Tipo',
 100: 'Obrigatório',
 101: 'Descrição',
 102: 'id',
 104: 'Sim',
 106: 'status',
 108: 'Sim',
 109: 'queued, reading, extracting, ready ou error.',
 112: 'Sim',
 116: 'Não',
 120: 'Não',
 121: 'Primeira citação; evidence contém todas as referências.',
 124: 'Não',
 125: 'Página original da primeira referência.',
 128: 'Sim',
 131: 'Garantias do contrato',
 134: 'Estados: queued, reading, extracting, ready e error. Comparações preservam uma fotografia dos fatos e '
      'usam um catálogo estável de 16 campos.',
 135: 'O registro guarda modelo configurado, models_used, progresso '
      'completed_chunks/total_chunks/cached_chunks, páginas, fatos, variants, needs_review e avisos.',
 140: '7 Consistência e retomada',
 142: 'Exemplos são idempotentes por IDs fixos. Uploads recebem UUID; blocos já concluídos podem ser '
      'reutilizados por hash de conteúdo, prompt, schema e modelos. A comparação é determinística e não '
      'considera a numeração da página ao comparar valores.',
 143: 'Situação',
 144: 'Comportamento',
 145: 'Finalidade',
 147: 'Novo UUID; reutiliza checkpoints compatíveis.',
 150: 'Retries, fallback e retomada; error se esgotados.',
 156: 'Registra models_used e invalida checkpoints incompatíveis.',
 159: '8 Dados e configuração',
 163: 'GEMINI_API_KEY permanece no servidor. GEMINI_MODEL define o modelo principal e GEMINI_FALLBACK_MODELS '
      'define as alternativas. O ZIP e o Git excluem .env, data e documentos privados.',
 168: '9 Operação local',
 169: 'Sinal',
 170: 'Verificação',
 171: 'Responsável',
 172: 'Cobertura',
 174: 'Estado de cada análise na biblioteca.',
 176: 'Interface',
 178: 'Progresso dos blocos na análise.',
 180: 'Interface',
 182: 'Erro acionável e nova tentativa.',
 184: 'API e interface',
 186: 'Chave apenas no ambiente do servidor.',
 188: 'Configuração',
 190: 'Suíte e registro dos PDFs de demonstração.',
 192: 'Testes',
 195: '10 Decisões de implementação',
 198: 'Alternativa',
 199: 'Finalidade',
 200: 'Decisão no MVP',
 214: '11 Limites da interpretação',
 215: 'A comparação identifica diferenças de texto e não determina equivalência jurídica.',
 216: 'Citações verificadas confirmam presença textual; a interpretação é conferida pelo usuário.',
 217: 'Informações ausentes permanecem não identificadas, sem presumir cobertura ou exclusão.',
 218: 'Leituras de páginas rasterizadas e valores divergentes são sinalizados para revisão.',
 220: '12 Validação do projeto',
 221: 'Os dois PDFs fictícios foram processados pelo Gemini 3.8 Flash, com 16 critérios e evidências '
      'verificadas por documento. A comparação apresentou 10 diferenças e nenhuma ausência; as exportações '
      'PDF e JSON passaram. O registro está em Validacao_IA_Exemplos.json. A suíte aprovou 32 testes Python '
      'e um teste Node, além do build e da verificação de interface em desktop e celular.',
 222: 'Verificação',
 223: 'Evidência',
 224: 'Resultado',
 225: 'Extração com IA',
 226: 'Dois PDFs fictícios / Gemini 3.8',
 227: '16 critérios verificados por documento',
 228: 'Comparação',
 229: '16 campos lado a lado',
 230: '10 diferenças e nenhuma ausência',
 231: 'Exportações',
 232: 'PDF e JSON',
 233: 'Conteúdo e formato aprovados',
 234: 'Interface e código',
 235: 'Desktop, celular e suíte',
 236: 'Build e testes aprovados'}
with ZipFile(P) as z: parts={i.filename:z.read(i.filename) for i in z.infolist()}
# Diagrama específico do projeto substitui a figura genérica do template.
im=Image.new('RGB',(1800,900),'#f5f9fc');draw=ImageDraw.Draw(im)
def diagram_font(size, bold=False):
 candidates=['/System/Library/Fonts/Supplemental/Arial'+(' Bold' if bold else '')+'.ttf', '/usr/share/fonts/truetype/dejavu/DejaVuSans'+('-Bold' if bold else '')+'.ttf', 'C:/Windows/Fonts/arial'+('bd' if bold else '')+'.ttf']
 for f in candidates:
  if Path(f).exists():return ImageFont.truetype(f,size)
 return ImageFont.load_default(size=size)
font=diagram_font(36)
bold=diagram_font(46,True)
draw.rectangle((0,0,1800,110),fill='#10324e');draw.text((55,30),'InsurMinds | Pipeline documental',font=bold,fill='white')
labels=[('React / TypeScript','Interface local'),('API Starlette','Upload e limites'),('Texto + visão','Páginas originais'),('Gemini 3.8 Flash','JSON por bloco'),('Comparação / PDF','16 campos / histórico'),('SQLite / arquivos','Fatos e fontes'),('Validação local','Citações / versões'),('Checkpoints','Retomada por hash')]
for i,(a,b) in enumerate(labels):
 x=45+(i%4)*445;y=200+(i//4)*360
 draw.rounded_rectangle((x,y,x+375,y+220),radius=18,fill='white',outline='#54788e',width=4)
 for j,t in enumerate([a,b]):
  box=draw.textbbox((0,0),t,font=font);draw.text((x+(375-box[2])/2,y+55+j*80),t,font=font,fill='#10324e')
 if i<3:
  draw.line((x+375,y+110,x+440,y+110),fill='#54788e',width=7);draw.polygon([(x+440,y+110),(x+420,y+98),(x+420,y+122)],fill='#54788e')
 if 4<=i<7:
  draw.line((x+440,y+110,x+385,y+110),fill='#54788e',width=7);draw.polygon([(x+380,y+110),(x+401,y+98),(x+401,y+122)],fill='#54788e')
draw.line((1565,420,1565,550),fill='#54788e',width=7);draw.polygon([(1565,555),(1552,533),(1578,533)],fill='#54788e')
draw.text((55,840),'Evidências preservadas; interpretação sujeita à revisão humana.',font=font,fill='#54788e')
buf=BytesIO();im.save(buf,format='PNG');parts['word/media/image1.png']=buf.getvalue()
E.register_namespace('', 'http://schemas.openxmlformats.org/package/2006/relationships')
rels=E.fromstring(parts['word/_rels/document.xml.rels'])
for rel in rels:
 if rel.get('Id')=='rId9':rel.set('Target','https://github.com/vicTmm/i2a2-desafio-final/blob/main/backend/models.py')
parts['word/_rels/document.xml.rels']=E.tostring(rels,encoding='utf-8',xml_declaration=True)
r=E.fromstring(parts['word/document.xml'])
ps=r.findall('.//w:p',N)
for i,value in updates.items():
 ts=ps[i].findall('.//w:t',N)
 if ts:
  ts[0].text=value
  for t in ts[1:]:t.text=''
for i in [53,54,55,86,87,131,132,133,134,135,159,160,161,162,163,164,195,196,197,214,215,216,217]:
 pp=ps[i].find('w:pPr',N)
 if pp is None:pp=E.SubElement(ps[i],'{'+N['w']+'}pPr')
 keep=pp.find('w:keepNext',N)
 if keep is None:keep=E.SubElement(pp,'{'+N['w']+'}keepNext')
 keep.set('{'+N['w']+'}val','1')
parts['word/document.xml']=E.tostring(r,encoding='utf-8',xml_declaration=True)
# Títulos pretos, conforme o estilo do relatório técnico.
r=E.fromstring(parts['word/styles.xml'])
for st in r.findall('w:style',N):
 if st.get('{'+N['w']+'}styleId','') in ['Title','Heading1','Heading2','Heading3']:
  rp=st.find('w:rPr',N)
  if rp is None:rp=E.SubElement(st,'{'+N['w']+'}rPr')
  color=rp.find('w:color',N)
  if color is None:color=E.SubElement(rp,'{'+N['w']+'}color')
  color.attrib.clear();color.set('{'+N['w']+'}val','000000')
parts['word/styles.xml']=E.tostring(r,encoding='utf-8',xml_declaration=True)
with ZipFile(P,'w',ZIP_DEFLATED) as z:
 for name,data in parts.items():z.writestr(name,data)
print('System Design atualizado.')
