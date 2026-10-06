"""Atualiza o DOCX existente preservando seu template, imagens e tabelas."""
from pathlib import Path
from zipfile import ZipFile, ZIP_DEFLATED
from xml.etree import ElementTree as E
from io import BytesIO
from PIL import Image, ImageDraw, ImageFont
P=Path(__file__).resolve().parents[1]/'Projeto_Final_Artefatos/InsurMinds_System_Design.docx'
N={'w':'http://schemas.openxmlformats.org/wordprocessingml/2006/main'}
E.register_namespace('w',N['w'])
updates={20:'STATUS · MVP local validado',24:'LAST UPDATED · 05/10/2026',29:'Revisão especializada de precisão pendente',36:'Limites: 20 MB, 300 páginas e 2 milhões de caracteres. O processamento usa blocos de até 60 mil caracteres, 20 páginas e 4 imagens. Evidências textuais são verificadas localmente; interpretações e leituras visuais exigem revisão humana.',51:'Apólices D&O são extensas, heterogêneas e redigidas em linguagem jurídica. Comparar limites, franquias, coberturas e exclusões exige rastrear cada condição até sua página de origem.',77:'Extrai JSON por bloco; retoma checkpoints.',78:'Checkpoints locais / API Gemini',88:'A recepção valida conteúdo, tamanho, PDF criptografado e limites. A aplicação deve operar em loopback, sem autenticação ou isolamento multiusuário.',90:'Cada bloco é enviado ao Gemini 3.8 Flash. Pydantic valida a estrutura e o verificador confere as citações nas páginas originais. A consolidação preserva múltiplas evidências e valores divergentes em variants, com needs_review.',92:'Timeout de 90 segundos, até três tentativas por modelo, espera exponencial e intervalo mínimo de 15 segundos. Fallback para Gemini 3.7 em indisponibilidade, sem contornar cotas. Checkpoints atômicos permitem retomar blocos concluídos.',109:'do_policy, uncertain ou other.',121:'Primeira citação; evidence contém todas as referências.',125:'Página original da primeira referência.',134:'Estados: queued, reading, extracting, ready e error. Comparações preservam uma fotografia dos fatos e usam um catálogo estável de 16 campos.',135:'O registro guarda modelo configurado, models_used, progresso completed_chunks/total_chunks/cached_chunks, páginas, fatos, variants, needs_review e avisos.',142:'Exemplos são idempotentes por IDs fixos. Uploads recebem UUID; blocos já concluídos podem ser reutilizados por hash de conteúdo, prompt, schema e modelos. A comparação é determinística e não considera a numeração da página ao comparar valores.',147:'Novo UUID; reutiliza checkpoints compatíveis.',150:'Retries, fallback e retomada; error se esgotados.',156:'Registra models_used e invalida checkpoints incompatíveis.',163:'GEMINI_API_KEY permanece no servidor. GEMINI_MODEL define o modelo principal e GEMINI_FALLBACK_MODELS define as alternativas. O ZIP e o Git excluem .env, data e documentos privados.',221:'Validação funcional concluída com dois PDFs fictícios e Gemini 3.8 Flash: 16 critérios com evidências verificadas por documento, 10 diferenças e exportações PDF/JSON aprovadas. Registro: Validacao_IA_Exemplos.json. Suíte: 32 testes Python e um teste Node, build e QA da interface. A precisão contratual em documentos de mercado permanece sujeita à revisão especializada.',225:'M1 concluído',226:'Dois PDFs fictícios / IA real',227:'Extração, comparação e exportações aprovadas'}
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
for i in [53,54,55,86,87,131,132,133,134,135]:
 pp=ps[i].find('w:pPr',N)
 if pp is None:pp=E.SubElement(ps[i],'{'+N['w']+'}pPr')
 if pp.find('w:keepNext',N) is None:E.SubElement(pp,'{'+N['w']+'}keepNext')
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
