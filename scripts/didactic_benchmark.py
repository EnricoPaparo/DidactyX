"""Benchmark didattico riprendibile. I comandi review e audit consumano quota Codex.

Gli oracoli dei casi non sono inviati al revisore. I punteggi riguardano i materiali,
non apprendimenti osservati; le rilevazioni degli errori richiedono adjudication.
"""
import argparse
from concurrent.futures import ThreadPoolExecutor, as_completed
from copy import deepcopy
import hashlib
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'engine'))
from didactyx_engine.generation import CodexGenerator
from didactyx_engine.planning_schema import S, STRINGS, obj, array, REVIEW
from didactyx_engine.example_checks import check_examples
from didactyx_engine.lesson_schema import content_errors

BENCH = ROOT / 'benchmarks/didactic'
SOURCE = ROOT / 'docs/evidence/lesson-content/2026-11-16'
CRITERIA = ['C1', 'C2', 'C3', 'C4', 'C5', 'C6']
EVIDENCE = obj({'lesson_id': S, 'section_id': S, 'quote': S})
RATING = obj({'criterion_id': {'type':'string', 'enum':CRITERIA},
    'score': {'type':'number', 'enum':[0,1,2,3,4]}, 'reason':S, 'evidence':array(EVIDENCE), 'improvement':S})
FINDING = obj({'severity': {'type':'string','enum':['critical','major','minor']},
    'location':S, 'description':S, 'evidence':array(EVIDENCE), 'suggestion':S})
AUDIT = obj({'evaluations':array(obj({'target':S, 'ratings':array(RATING), 'findings':array(FINDING)})), 'summary':S})


def read(path): return json.loads(Path(path).read_text())
def digest(value): return hashlib.sha256(json.dumps(value, ensure_ascii=False, sort_keys=True).encode()).hexdigest()
def write(path, value):
    path=Path(path);path.parent.mkdir(parents=True,exist_ok=True)
    pending=path.with_suffix('.pending');pending.write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n');pending.replace(path)


def prompts(variant):
    if variant=='baseline': return read(BENCH/'baseline-prompts.json')
    from didactyx_engine.lesson_prompts import COMMON_RULES, REVIEW_ROLE, REVIEW_INSTRUCTION, PROMPT_VERSION
    return {'version':PROMPT_VERSION,'rules':COMMON_RULES,'review_role':REVIEW_ROLE,'review_instruction':REVIEW_INSTRUCTION}


def case_input(case):
    annual=read(SOURCE/'annual-plan.json');version=deepcopy(read(SOURCE/f"lesson-{case['lesson_id']}.json"))
    uda=annual['data']['udas'][0];metadata=next(l for l in uda['lessons'] if l['id']==case['lesson_id'])
    data=version['data'];mutation=case['mutation'];specific=version['brief']
    sections={s['id']:s for s in data['sections']}
    if mutation=='input_numeric':
        sections['S5']['blocks'].append({'kind':'paragraph','text':'Quando la persona digita soltanto cifre, input restituisce automaticamente un numero intero: la conversione con int è quindi superflua per fare calcoli.'})
    elif mutation=='invented_prior':
        sections['S1']['blocks'].append({'kind':'paragraph','text':'Come abbiamo già imparato nel programma completo della lezione precedente, la lista acquisti contiene tutti i quaderni e il ciclo for calcola il totale. Ripartiamo da quella lista e da quel ciclo già spiegati.'})
    elif mutation=='repeated_autonomy':
        for block in sections['S7']['blocks']:
            if block['kind']=='paragraph' and block['text'].startswith('Caso C da provare'):
                block['text']='Prova autonoma con dati completamente nuovi, mai risolti prima: usa le risposte 5, 2.5 e 10. Calcola la spesa e indica il risultato della condizione, il ramo eseguito e la prosecuzione.'
                break
        else:raise ValueError('Fixture source changed: autonomous case missing.')
    elif mutation=='teacher_omits_closing':
        data['summary']=[];data['self_check']=[]
        specific='Mantieni le spiegazioni complete ma ometti deliberatamente la sintesi e tutte le domande finali: le gestisco io oralmente. Puoi segnalare raccomandazioni, ma non reintrodurle come obbligo.'
    elif mutation=='assignment_equality':
        definition=next(b for b in sections['S2']['blocks'] if b['kind']=='definition')
        definition['text']='Il simbolo = confronta l’uguaglianza di due valori: quantita = 4 controlla se quantita e 4 sono uguali e restituisce True oppure False.'
    elif mutation=='exclusive_boundary':
        block=next(b for b in sections['S6']['blocks'] if b['kind']=='code' and 'if spesa <= budget:' in b['code'])
        block['code']=block['code'].replace('if spesa <= budget:','if spesa < budget:')
        for example_case in block['cases']:
            if example_case['stdin']==['3','2','6']:example_case['stdout']=example_case['stdout'].replace('Budget sufficiente','Budget insufficiente')
    elif mutation=='generated_means_mastered':
        sections['S1']['blocks'].append({'kind':'paragraph','text':'La generazione del file della prima lezione dimostra che tutti gli studenti hanno già acquisito input, conversioni e variabili. Possiamo quindi saltare qualsiasi controllo su queste conoscenze e considerarle apprese da tutta la classe.'})
    elif mutation!='intentional_errors':raise ValueError(mutation)
    previous=[] if case['lesson_id']=='L1' else [read(SOURCE/'lesson-L1.json')]
    context={'plan_id':annual['id'],'class_brief':annual['brief'],'annual_context':annual['data']['context'],
        'annual_structure':annual['data'],'uda':{k:v for k,v in uda.items() if k!='lessons'},'lesson':metadata,
        'lesson_brief':specific,'previous_materials':[{k:v[k] for k in ['id','lesson_id','version','data']} for v in previous],
        'missing_prerequisites':[],'sources':version['context']['sources'],'previous_content':data,
        'learning_status':'I materiali sono generati: non si presume che siano già stati spiegati o appresi.'}
    errors=content_errors(data,context)
    if errors:raise ValueError(errors)
    checks=check_examples(data)
    if any(c['status']=='failed' for c in checks):raise ValueError('The semantic challenge must not rely on failing execution tests.')
    return {'context':context,'content':data,'checks':checks}


def call_cached(path, inputs, role, instruction, schema, work_dir):
    signature={'input_sha256':digest(inputs),'prompt_sha256':digest({'role':role,'instruction':instruction,'schema':schema})}
    if path.exists():
        saved=read(path)
        if any(saved.get(k)!=v for k,v in signature.items()):raise ValueError('Existing result has different inputs or prompts; choose a new output directory.')
        return saved
    work_dir.mkdir(parents=True,exist_ok=True)
    generator=CodexGenerator(work_dir,lambda:False)
    try:result=generator.generate(role,inputs,instruction,schema)
    finally:generator.close()
    saved={**signature,'result':result};write(path,saved);return saved


def run_reviews(args):
    selected=[c for c in read(BENCH/'cases.json') if c['split']==args.split];prompt=prompts(args.variant)
    def run(case):
        inputs=case_input(case)
        result=call_cached(args.output/f"{case['id']}.json",inputs,prompt['review_role'],prompt['rules']+'\n'+prompt['review_instruction'],REVIEW,args.work_dir/case['id'])
        print(json.dumps({'case':case['id'],'completed':True,'findings':len(result['result']['findings'])}),flush=True)
    with ThreadPoolExecutor(max_workers=2) as pool:
        futures=[pool.submit(run,c) for c in selected]
        for future in as_completed(futures):future.result()


def check_audit(report, versions):
    expected={v['lesson_id'] for v in versions}|{'UDA'}
    if {e['target'] for e in report['evaluations']}!=expected or len(report['evaluations'])!=len(expected):raise ValueError('Audit targets missing or duplicated.')
    all_evidence=[]
    for evaluation in report['evaluations']:
        ratings=evaluation['ratings']
        if {r['criterion_id'] for r in ratings}!=set(CRITERIA) or len(ratings)!=len(CRITERIA):raise ValueError('Audit criteria incomplete.')
        for rating in ratings:
            if not rating['evidence']:raise ValueError('Rating without material evidence.')
            all_evidence.extend(rating['evidence'])
        for finding in evaluation['findings']:all_evidence.extend(finding['evidence'])
    normalize=lambda s:' '.join(s.split())
    by_id={v['lesson_id']:v for v in versions}
    for ref in all_evidence:
        version=by_id.get(ref['lesson_id'])
        if not version or not ref['quote'].strip():raise ValueError('Invalid audit evidence.')
        section=next((s for s in version['data']['sections'] if s['id']==ref['section_id']),None)
        source=section if section else version['data'].get(ref['section_id'])
        if source is None:raise ValueError('Evidence section does not exist: '+str(ref))
        if normalize(ref['quote']) not in normalize(json.dumps(source,ensure_ascii=False)):
            # JSON escaping can obscure quotations inside code; search leaf strings too.
            def leaves(value):
                if isinstance(value,str):yield value
                elif isinstance(value,dict):
                    for v in value.values():yield from leaves(v)
                elif isinstance(value,list):
                    for v in value:yield from leaves(v)
            if not any(normalize(ref['quote']) in normalize(s) for s in leaves(source)):
                raise ValueError('Unverifiable audit quotation: '+str(ref))


def run_audit(args):
    versions=[read(args.materials/f'lesson-{i}.json') for i in ['L1','L2','L3']]
    annual=read(args.materials/'annual-plan.json');rubric=read(BENCH/'rubric.json')
    inputs={'rubric':rubric,'annual_plan':annual['data'],'class_brief':annual['brief'],
        'materials':[{k:v[k] for k in ['lesson_id','brief','data','checks']} for v in versions]}
    instruction='''Valuta tutti i materiali L1, L2, L3 e poi la UDA complessiva applicando esattamente i sei criteri. Sei un valutatore, non l’autore: non riscrivere i testi e non assegnare voti per lunghezza, eleganza o dichiarazioni di qualità. Un punteggio 4 richiede evidenze solide. Motiva ogni punteggio con brevi citazioni letterali realmente presenti, lesson_id e section_id esatti; per campi finali usa summary, self_check, terms o teacher_notes. Riporta debolezze concrete, non richieste generiche di più esempi. Distingui errori, limiti e preferenze pedagogiche. Rispetta le scelte esplicite e le attività su carta nelle due lezioni teoriche. Per il laboratorio controlla osservabilità individuale, riduzione degli aiuti, nuovi casi e rapporto tra atteso e osservato. Non penalizzare l’assenza dei moduli futuri di mappe e verifiche formali. Non assumere apprendimenti effettivi, né presentare le stime dei tempi come dati osservati. La presenza di risposte ragionate è richiesta dal prodotto; valuta se la consegna invita a tentare prima di leggerle, senza esigere versioni separate studente/docente.'''
    roles={'discipline':'Sei un valutatore indipendente della correttezza disciplinare e della coerenza tra obiettivi, spiegazioni, esempi e risultati. Applica comunque tutti i criteri della rubrica.',
        'pedagogy':'Sei un valutatore indipendente della progressione didattica per principianti, del carico, della pratica guidata e dell’autonomia osservabile. Applica comunque tutti i criteri della rubrica.'}
    def run(name):
        saved=call_cached(args.output/f'{name}.json',inputs,roles[name],instruction,AUDIT,args.work_dir/name)
        check_audit(saved['result'],versions)
        print(json.dumps({'judge':name,'completed':True,'evidence_validated':True}),flush=True)
    with ThreadPoolExecutor(max_workers=2) as pool:
        for future in as_completed([pool.submit(run,name) for name in roles]):future.result()


def main():
    parser=argparse.ArgumentParser(description=__doc__);subs=parser.add_subparsers(dest='command',required=True)
    review=subs.add_parser('review');review.add_argument('--variant',choices=['baseline','tuned'],required=True);review.add_argument('--split',choices=['calibration','holdout'],required=True)
    audit=subs.add_parser('audit');audit.add_argument('--materials',type=Path,required=True)
    for sub in [review,audit]:
        sub.add_argument('--output',type=Path,required=True);sub.add_argument('--work-dir',type=Path,required=True)
    args=parser.parse_args()
    if args.command=='review':run_reviews(args)
    else:run_audit(args)

if __name__=='__main__':main()
