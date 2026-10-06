"""Verifica integridade e extrai imagens dos artefatos para inspeção visual."""
from pathlib import Path
import os
import re
import subprocess
from zipfile import ZipFile
from xml.etree import ElementTree as ET
import pymupdf

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'Projeto_Final_Artefatos'
TMP=ROOT/'tmp'/'video-review'
TMP.mkdir(parents=True,exist_ok=True)
with ZipFile(OUT/'InsurMinds_Projeto_Final.pptx') as z:
    assert z.testzip() is None
    slides=[n for n in z.namelist() if re.fullmatch(r'ppt/slides/slide\d+.xml',n)]
    assert len(slides)==8
    for name in z.namelist():
        if name.endswith('.xml'):
            ET.fromstring(z.read(name))
    assert b'<a:tbl>' in z.read('ppt/slides/slide6.xml'), 'Tabela deve ser editável'
with pymupdf.open(OUT/'InsurMinds_Relatorio_Tecnico.pdf') as pdf:
    assert 3 <= len(pdf) <= 12
    text=''.join(p.get_text() for p in pdf)
    assert all(t in text for t in ['Componentes','Decisões','Limites','Fontes'])
ffmpeg=ROOT/'node_modules'/'ffmpeg-static'/('ffmpeg.exe' if os.name=='nt' else 'ffmpeg')
video=OUT/'InsurMinds_Projeto_Final.mp4'
assert video.exists(), 'Vídeo obrigatório na entrega final'
if video.exists():
    probe=subprocess.run([str(ffmpeg),'-i',str(video)],capture_output=True,text=True,encoding='utf-8',errors='replace')
    match=re.search(r'Duration: (\d+):(\d+):(\d+\.\d+)',probe.stderr)
    assert match,probe.stderr
    h,m,s=map(float,match.groups())
    duration=h*3600+m*60+s
    assert 60<duration<=300,duration
    assert 'h264' in probe.stderr and 'yuv420p' in probe.stderr and 'Audio: aac' in probe.stderr
    for second in [7,24,43,65,90,116,int(duration-7)]:
        subprocess.run([str(ffmpeg),'-y','-ss',str(second),'-i',str(video),'-frames:v','1',str(TMP/f'frame-{second}.png')],stdout=subprocess.DEVNULL,stderr=subprocess.PIPE,check=True)
    video_status=f'vídeo H.264 de {duration:.1f} segundos'
else:
    video_status='vídeo aguardando gravação da equipe'
print(f'Artefatos: PPTX íntegro, 8 slides, tabela editável; PDF íntegro; {video_status}.')

with ZipFile(OUT/'InsurMinds_System_Design.docx') as z:
    assert z.testzip() is None
    for name in z.namelist():
        if name.endswith('.xml') or name.endswith('.rels'):
            ET.fromstring(z.read(name))
    assert b'gemini' in z.read('word/document.xml').lower()
with ZipFile(OUT/'InsurMinds_Codigo_Fonte.zip') as z:
    assert z.testzip() is None
    required=['backend/checkpoints.py','src/lib/upload.ts','tests/test_chunks.py',
              'scripts/check_real_policies.py','scripts/record_demo.mjs',
              'Projeto_Final_Artefatos/InsurMinds_Projeto_Final.mp4',
              'Projeto_Final_Artefatos/Validacao_IA_Exemplos.json',
              'Projeto_Final_Artefatos/Validacao_Apolices_Reais.json']
    for relative in required:
        assert z.read('insurminds/'+relative)==(ROOT/relative).read_bytes(),relative
    assert not any('/data/' in n or '/tmp/' in n or '/node_modules/' in n or n.endswith('/.env') for n in z.namelist())
print('DOCX íntegro; ZIP contém código e vídeo atuais e exclui dados privados.')
