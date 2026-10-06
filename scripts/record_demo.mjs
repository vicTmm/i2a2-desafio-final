/** Grava a aplicação real sobre o DATA_DIR dos PDFs fictícios analisados pelo Gemini. */
import fs from 'node:fs/promises';
import path from 'node:path';
import {execFileSync} from 'node:child_process';
const root=path.resolve('.'), tmp=path.join(root,'tmp/video'), out=path.join(root,'Projeto_Final_Artefatos');
await fs.mkdir(tmp,{recursive:true});
const cache=path.join(tmp,'playwright-browsers/ffmpeg-1011');await fs.mkdir(cache,{recursive:true});
const bin=path.join(cache,'ffmpeg-mac');await fs.unlink(bin).catch(()=>{});await fs.symlink(path.join(root,'node_modules/ffmpeg-static/ffmpeg'),bin);
process.env.PLAYWRIGHT_BROWSERS_PATH=path.join(tmp,'playwright-browsers');
const {chromium}=await import('playwright-core');
const browser=await chromium.launch({headless:true,executablePath:'/Applications/Google Chrome.app/Contents/MacOS/Google Chrome'});
const context=await browser.newContext({viewport:{width:1280,height:800},recordVideo:{dir:tmp,size:{width:1280,height:800}},acceptDownloads:true});
const page=await context.newPage();const video=page.video();const errors=[];page.on('pageerror',e=>errors.push(e.message));
const segments=[];const start=Date.now();
async function hold(title,body,narration,seconds=14){
 await page.evaluate(([title,body])=>{document.getElementById('video-caption')?.remove();const e=document.createElement('aside');e.id='video-caption';e.setAttribute('popover','manual');e.style.cssText='position:fixed;inset:auto 25px 18px 245px;margin:0;border:0;width:auto;max-width:none;background:#183d32;color:white;padding:18px 22px;border-radius:9px;font-family:Arial;pointer-events:none';const h=document.createElement('strong');h.textContent=title;h.style.cssText='display:block;font-size:21px;margin-bottom:6px';const p=document.createElement('div');p.textContent=body;p.style.cssText='font-size:17px;line-height:1.4';e.append(h,p);document.body.append(e);e.showPopover();},[title,body]);
 segments.push({offset:(Date.now()-start)/1000,narration});await page.waitForTimeout(seconds*1000);
}
async function title(title,body,narration,seconds=14){
 await page.setContent('<html lang="pt-BR"><meta charset="utf-8"><body style="margin:0;background:#f8f9f4;color:#244b3b;font-family:Arial"><main style="padding:110px 80px"><p style="font-size:18px">INSURMINDS / I2A2 2026</p><h1 style="font-size:48px;max-width:1080px"></h1><p id="body" style="font-size:28px;line-height:1.5;max-width:1080px;white-space:pre-line"></p><p style="font-size:15px;margin-top:70px">Documentos fictícios autorais · Narração sintética</p></main></body></html>');
 await page.locator('h1').evaluate((e,v)=>e.textContent=v,title);await page.locator('#body').evaluate((e,v)=>e.textContent=v,body);
 segments.push({offset:(Date.now()-start)/1000,narration});await page.waitForTimeout(seconds*1000);
}
try{
 await title('Clareza na comparação de apólices D&O','Organizar informações, identificar diferenças e conferir a origem de cada dado.','InsurMinds é uma plataforma de análise e comparação de apólices de responsabilidade de administradores. Ela organiza os dados e mantém a ligação com o documento de origem.');
 await title('Leitura em blocos, evidências e retomada','React → API Python → texto e visão → Gemini 3.8\nValidação → checkpoints → SQLite → comparação e PDF','O processamento divide documentos longos em blocos, conserva as páginas originais e salva respostas concluídas. Valores distintos permanecem disponíveis para revisão.');
 await page.goto(process.env.DEMO_URL||'http://127.0.0.1:8002',{waitUntil:'networkidle'});
 await page.getByRole('heading',{name:'Visão geral',exact:true}).waitFor();
 await fs.mkdir(path.join(root,'tmp/ui'),{recursive:true});await page.screenshot({path:path.join(root,'tmp/ui/overview.png')});
 await hold('Aplicação real, análise real com IA','Dois PDFs fictícios analisados pelo Gemini 3.8; exemplos pré-preenchidos não foram usados.','Esta biblioteca contém dois documentos fictícios enviados à análise real do Gemini três ponto oito. Cada documento retornou dezesseis critérios com citações verificadas no texto.');
 await page.locator('nav').getByRole('button',{name:'Apólices',exact:false}).first().click();
 const boxes=page.getByRole('checkbox');await boxes.nth(0).check();await boxes.nth(1).check();
 await hold('Biblioteca e seleção','Compare de duas a quatro apólices concluídas.','Na biblioteca podemos consultar as análises e selecionar documentos concluídos. A ferramenta compara de duas a quatro apólices pelos mesmos dezesseis critérios.');
 await page.evaluate(()=>document.getElementById('video-caption')?.remove());
 await page.locator('.selection-bar').getByRole('button',{name:'Comparar apólices'}).click();await page.locator('.comparison-table').waitFor();
 await hold('Comparação reproduzível','16 campos, 10 diferenças textuais, nenhuma ausência nesta execução.','O resultado desta execução apresenta dez diferenças textuais e nenhum campo ausente. A comparação é determinística e conserva uma fotografia dos fatos utilizados.');
 await page.getByLabel('Só diferenças e ausências').check();
 const cell=page.locator('.evidence-cell').filter({hasText:'15.000.000'}).first();await cell.scrollIntoViewIfNeeded();await cell.click();await page.locator('.quote-card').waitFor();
 await hold('Trecho e página de origem','Citação verificada significa presença textual; a interpretação exige revisão.','Ao abrir uma informação, encontramos o trecho e a página de origem. A verificação comprova a presença da citação, mas a interpretação contratual continua exigindo revisão humana.');
 await page.keyboard.press('Escape');await page.evaluate(()=>document.getElementById('video-caption')?.remove());
 const [download]=await Promise.all([page.waitForEvent('download'),page.getByRole('link',{name:'Exportar PDF'}).click()]);await download.saveAs(path.join(tmp,'comparacao-demo.pdf'));
 await hold('Exportação PDF e JSON','Relatório com os valores, evidências e limitações.','A exportação gera um relatório em PDF com valores, evidências e limitações. A mesma comparação pode ser obtida em JSON para auditoria ou integração.');
 await page.getByRole('button',{name:'Histórico',exact:true}).click();
 await hold('Histórico persistente','As comparações permanecem no SQLite local.','O histórico mantém as comparações no banco local. O arquivo original continua disponível para a conferência das evidências.');
 await title('Validação e próximos passos','32 testes Python + 1 teste Node aprovados\nBuild e interface verificados em desktop e celular\n\nPrecisão em apólices de mercado: revisão especializada pendente','A entrega passou por trinta e dois testes Python, um teste de upload em Node, build e verificação da interface. A precisão em apólices de mercado ainda depende de avaliação especializada.',16);
 if(errors.length)throw Error(errors.join('\n'));
}finally{await context.close();await browser.close();}
const source=await video.path();
const inputs=[];const filters=[];
for(let i=0;i<segments.length;i++){
 const audio=path.join(tmp,`narracao-${i}.aiff`);execFileSync('/usr/bin/say',['-v','Luciana','-r','155','-o',audio,segments[i].narration]);inputs.push('-i',audio);filters.push(`[${i+1}:a]adelay=${Math.round(segments[i].offset*1000)}:all=1[a${i}]`);
}
const filter=filters.join(';')+';'+segments.map((_,i)=>`[a${i}]`).join('')+`amix=inputs=${segments.length}:normalize=0[audio]`;
execFileSync(path.join(root,'node_modules/ffmpeg-static/ffmpeg'),['-y','-i',source,...inputs,'-filter_complex',filter,'-map','0:v','-map','[audio]','-c:v','libx264','-preset','fast','-crf','25','-pix_fmt','yuv420p','-c:a','aac','-b:a','96k','-movflags','+faststart','-shortest',path.join(out,'InsurMinds_Projeto_Final.mp4')],{stdio:['ignore','ignore','pipe']});
await fs.writeFile(path.join(tmp,'narracao.json'),JSON.stringify(segments,null,2));console.log('Vídeo concluído: navegação real e narração sintética.');
