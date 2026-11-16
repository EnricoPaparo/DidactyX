"""Due renderer dello stesso contenuto salvato: lettore locale e PDF editoriale."""
from html import escape
from pathlib import Path
import re
import textwrap
import uuid
from urllib.parse import urlparse


def e(value): return escape(str(value))

def example_output(version, section_id, block_index, case_number, case):
    match=next((c for c in version['checks'] if c.get('section_id')==section_id and c.get('block_index')==block_index and c.get('case')==case_number and c.get('status')=='passed' and 'transcript' in c),None)
    return ('Esecuzione di esempio',match['transcript']) if match else ('Output atteso',case['stdout'])

def render_html(version):
    data=version['data']; body=[]
    if version['context'].get('objectives'):
        body.append('<h2>Che cosa imparerai</h2><ul>'+''.join('<li>'+e(o['description'])+'</li>' for o in version['context']['objectives'])+'</ul>')
    for section in data['sections']:
        body.append(f'<section id="{e(section["id"])}"><h2>{e(section["title"])}</h2>')
        for block_index,b in enumerate(section['blocks']):
            k=b['kind']
            if k=='paragraph':body.append('<p>'+e(b['text']).replace('\n','<br>')+'</p>')
            elif k=='definition':body.append('<aside><strong>'+e(b['term'])+'</strong><p>'+e(b['text'])+'</p></aside>')
            elif k=='example':body.append('<div class="example"><h3>'+e(b['title'])+'</h3><ol>'+''.join('<li>'+e(s)+'</li>' for s in b['steps'])+'</ol><p>'+e(b['conclusion'])+'</p></div>')
            elif k=='code':
                body.append('<pre><code>'+e(b['code'])+'</code></pre><p>'+e(b['explanation'])+'</p>')
                for i,c in enumerate(b['cases'],1):
                    body.append(f'<div class="case"><h4>Prova {i}</h4>')
                    if c['stdin']:body.append('<p class="small">Dati inseriti, in ordine</p><pre>'+e('\n'.join(c['stdin']))+'</pre>')
                    label,output=example_output(version,section['id'],block_index,i,c)
                    body.append('<p class="small">'+label+'</p>'+('<pre>'+e(output)+'</pre>' if output else '<p>Nessuna uscita visualizzata.</p>')+'</div>')
            elif k=='list':body.append('<ul>'+''.join('<li>'+e(s)+'</li>' for s in b['items'])+'</ul>')
            elif k=='table':body.append('<div class="table"><table><thead><tr>'+''.join('<th>'+e(c)+'</th>' for c in b['headers'])+'</tr></thead><tbody>'+''.join('<tr>'+''.join('<td>'+e(c)+'</td>' for c in row)+'</tr>' for row in b['rows'])+'</tbody></table></div>')
            elif k=='callout':body.append('<aside><strong>'+e(b['title'])+'</strong><p>'+e(b['text'])+'</p></aside>')
            elif k=='formula':body.append('<div class="formula">'+e(b['expression'])+'</div><p>'+e(b['explanation'])+'</p>')
        body.append('</section>')
    if data['summary']:body.append('<h2>In sintesi</h2><ul>'+''.join('<li>'+e(x)+'</li>' for x in data['summary'])+'</ul>')
    if data['terms']:
        body.append('<h2>Le parole della lezione</h2><dl>'+''.join('<dt>'+e(t['term'])+'</dt><dd>'+e(t['definition'])+'</dd>' for t in data['terms'])+'</dl>')
    if data['self_check']:
        body.append('<h2>Controlla la comprensione</h2>'+''.join('<details><summary>'+e(q['question'])+'</summary><p>'+e(q['answer'])+'</p></details>' for q in data['self_check']))
    sources=[s for s in version['context']['sources'] if s['id'] in data['source_ids']]
    if sources:
        body.append('<h2>Riferimenti</h2><ul>')
        for s in sources:
            url=s['url'];link=('<a href="'+e(url)+'">'+e(s['title'])+'</a>') if urlparse(url).scheme in ('http','https') else e(s['title'])
            body.append('<li>'+link+'</li>')
        body.append('</ul>')
    return '''<!doctype html><html lang="it"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><meta http-equiv="Content-Security-Policy" content="default-src 'none'; style-src 'unsafe-inline';"><style>
html{color-scheme:light;background:#e9edef;color:#202b32}*{box-sizing:border-box}body{margin:0;font-family:-apple-system,BlinkMacSystemFont,Arial,sans-serif;font-size:17px;line-height:1.75}article{max-width:850px;margin:28px auto;padding:55px 62px 72px;background:white;border:1px solid #dce2e5;border-radius:5px}header{border-bottom:1px solid #dce2e5;padding-bottom:24px;margin-bottom:34px}.eyebrow{font-size:12px;letter-spacing:.1em;color:#536976;text-transform:uppercase}h1{font-size:34px;line-height:1.2;letter-spacing:-.7px}h2{font-size:25px;line-height:1.3;margin:44px 0 20px;letter-spacing:-.4px}h3{font-size:19px;line-height:1.4}h4{font-size:14px;margin:12px 0 6px}p{margin:0 0 18px}li{margin:8px 0}aside,.example{background:#f3f7f8;border-left:3px solid #6d929f;padding:20px 24px;margin:26px 0}aside p{margin:8px 0 0}pre{font:14px/1.65 ui-monospace,Menlo,monospace;background:#f3f5f7;padding:18px 20px;border:1px solid #e2e7ea;border-radius:5px;white-space:pre;overflow-x:auto;tab-size:4}.case{border-left:2px solid #dce2e5;padding-left:18px;margin:20px 0}.case pre{margin-top:5px}.small{font-size:13px;color:#536976;margin:0}.formula{font-family:Georgia,serif;font-size:23px;text-align:center;padding:18px;overflow-wrap:anywhere}.table{overflow-x:auto}table{width:100%;border-collapse:collapse;font-size:15px}th,td{text-align:left;vertical-align:top;padding:10px 12px;border:1px solid #dce2e5}th{background:#f0f5f6}dt{font-weight:650}dd{margin:4px 0 16px}details{border-bottom:1px solid #dce2e5;padding:14px 0}summary{cursor:pointer;font-weight:600}details p{margin:16px 0}a{color:#23627c}section{scroll-margin-top:20px}@media(max-width:700px){article{margin:0;padding:30px 25px;border:0}h1{font-size:29px}}@media print{html{background:white}article{border:0;margin:0;padding:0}details p{display:block}}
</style></head><body><article><header><div class="eyebrow">'''+e(version['lesson_id'])+' · Lezione · versione '+str(version['version'])+'</div><h1>'+e(data['title'])+'</h1><p>'+e(data['lead'])+'</p></header>'+''.join(body)+'</article></body></html>'


def export_pdf(version,directory):
    from reportlab.lib import colors
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.styles import ParagraphStyle
    from reportlab.pdfbase import pdfmetrics
    from reportlab.pdfbase.ttfonts import TTFont
    from reportlab.platypus import SimpleDocTemplate,Paragraph,Preformatted,LongTable,TableStyle,KeepTogether
    from .plan_pdf import FONT_LOCK
    with FONT_LOCK:
        fonts=Path(__file__).parent/'assets/fonts'
        for name,file in [('LessonText','DejaVuSans.ttf'),('LessonBold','DejaVuSans-Bold.ttf'),('LessonCode','DejaVuSansMono.ttf')]:
            if name not in pdfmetrics.getRegisteredFontNames():pdfmetrics.registerFont(TTFont(name,str(fonts/file)))
        pdfmetrics.registerFontFamily('LessonText',normal='LessonText',bold='LessonBold')
    styles={
        'body':ParagraphStyle('body',fontName='LessonText',fontSize=11,leading=17,spaceAfter=10),
        'title':ParagraphStyle('title',fontName='LessonBold',fontSize=24,leading=30,spaceAfter=18,keepWithNext=True),
        'h2':ParagraphStyle('h2',fontName='LessonBold',fontSize=16,leading=22,spaceBefore=20,spaceAfter=12,keepWithNext=True),
        'h3':ParagraphStyle('h3',fontName='LessonBold',fontSize=12,leading=18,spaceBefore=12,spaceAfter=8,keepWithNext=True),
        'code':ParagraphStyle('code',fontName='LessonCode',fontSize=10.2,leading=15,spaceBefore=10,spaceAfter=14),
        'small':ParagraphStyle('small',fontName='LessonText',fontSize=8.5,leading=12,spaceAfter=10),
        'cell':ParagraphStyle('cell',fontName='LessonText',fontSize=9.2,leading=14),
    }
    def clean(s):return e(s).replace('\u2011','-').replace('\u2013','-').replace('\u2014','-').replace('\n','<br/>')
    def p(s,style='body'):return Paragraph(clean(s),styles[style])
    class CodePanel(Preformatted):
        def draw(self):
            canvas=self.canv;canvas.saveState()
            canvas.setFillColor(colors.HexColor('#f2f5f7'))
            canvas.setStrokeColor(colors.HexColor('#dde4e8'));canvas.setLineWidth(.4)
            canvas.roundRect(-7,-4,self.width+14,self.height+8,3,fill=1,stroke=1)
            super().draw();canvas.restoreState()
    def code(s):
        lines=[]
        for line in s.expandtabs(4).splitlines():
            lines.extend(textwrap.wrap(line,width=76,replace_whitespace=False,drop_whitespace=False,subsequent_indent='    ',break_on_hyphens=False) or [''])
        return CodePanel('\n'.join(lines),styles['code'])
    data=version['data'];story=[p(version['lesson_id']+' · Lezione · versione '+str(version['version']),'small'),p(data['title'],'title'),p(data['lead'])]
    if version['context'].get('objectives'):
        story.append(p('Che cosa imparerai','h2'));story.extend(p('• '+o['description']) for o in version['context']['objectives'])
    for section in data['sections']:
        story.append(p(section['title'],'h2'))
        for block_index,b in enumerate(section['blocks']):
            k=b['kind']
            if k=='paragraph':story.append(p(b['text']))
            elif k=='definition':story.extend([p(b['term'],'h3'),p(b['text'])])
            elif k=='example':
                story.append(p(b['title'],'h3'))
                for i,s in enumerate(b['steps'],1):story.append(p(f'{i}. {s}'))
                story.append(p(b['conclusion']))
            elif k=='code':
                story.extend([KeepTogether([code(b['code'])]),p(b['explanation'])])
                for i,c in enumerate(b['cases'],1):
                    case_block=[p(f'Prova {i}','h3')]
                    if c['stdin']:case_block.extend([p('Dati inseriti, in ordine','small'),code('\n'.join(c['stdin']))])
                    label,output=example_output(version,section['id'],block_index,i,c)
                    case_block.extend([p(label,'small'),code(output) if output else p('Nessuna uscita visualizzata.')])
                    story.append(KeepTogether(case_block))
            elif k=='list':story.extend(p('• '+s) for s in b['items'])
            elif k=='table':
                rows=[[p(c,'cell') for c in b['headers']]]+[[p(c,'cell') for c in row] for row in b['rows']]
                table=LongTable(rows,colWidths=[(A4[0]-100)/len(b['headers'])]*len(b['headers']),repeatRows=1,splitInRow=1)
                table.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,0),colors.HexColor('#eef3f5')),('GRID',(0,0),(-1,-1),.4,colors.HexColor('#ccd5da')),('VALIGN',(0,0),(-1,-1),'TOP'),('LEFTPADDING',(0,0),(-1,-1),8),('RIGHTPADDING',(0,0),(-1,-1),8),('TOPPADDING',(0,0),(-1,-1),8),('BOTTOMPADDING',(0,0),(-1,-1),8)]));story.append(KeepTogether([table]))
            elif k=='callout':story.extend([p(b['title'],'h3'),p(b['text'])])
            elif k=='formula':story.extend([p(b['expression'],'h3'),p(b['explanation'])])
    if data['summary']:
        story.append(p('In sintesi','h2'));story.extend(p('• '+s) for s in data['summary'])
    if data['terms']:
        story.append(p('Le parole della lezione','h2'))
        for t in data['terms']:story.extend([p(t['term'],'h3'),p(t['definition'])])
    if data['self_check']:
        story.append(p('Controlla la comprensione','h2'))
        for q in data['self_check']:story.extend([p(q['question'],'h3'),p(q['answer'])])
    sources=[s for s in version['context']['sources'] if s['id'] in data['source_ids']]
    if sources:
        story.append(p('Riferimenti','h2'))
        for s in sources:story.extend([p(s['title'],'h3'),p(s['url'],'small')])
    directory=Path(directory).expanduser().resolve();directory.mkdir(parents=True,exist_ok=True)
    slug=re.sub(r'[^\w-]+','-',data['title']).strip('-')[:65] or 'lezione'
    target=directory/f'{slug}_v{version["version"]}_{uuid.uuid4().hex[:12]}.pdf';temporary=target.with_suffix('.pdf.tmp')
    def footer(canvas,doc):
        canvas.setFont('LessonText',8);canvas.drawString(50,25,'DidactyX · '+version['lesson_id']+' · versione '+str(version['version']));canvas.drawRightString(A4[0]-50,25,str(doc.page))
    try:
        SimpleDocTemplate(str(temporary),pagesize=A4,leftMargin=50,rightMargin=50,topMargin=45,bottomMargin=48,title=data['title'],author='DidactyX').build(story,onFirstPage=footer,onLaterPages=footer)
        temporary.replace(target)
    finally:temporary.unlink(missing_ok=True)
    return {'path':str(target),'version':version['version']}
