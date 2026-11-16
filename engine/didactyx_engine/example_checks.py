import json
import os
from pathlib import Path
import subprocess
import sys


def check_examples(data):
    checks=[]
    for section in data['sections']:
        for index, block in enumerate(section['blocks']):
            if block['kind']!='code':continue
            base={'section_id':section['id'],'block_index':index}
            if block['language'].lower() not in ('python','py','python3') or block['execution']!='check':
                checks.append({**base,'status':'not_run','message':'Codice illustrativo o linguaggio non eseguito automaticamente.'});continue
            for number,case in enumerate(block['cases'],1):
                command=[sys.executable,'--check-python'] if getattr(sys,'frozen',False) else [sys.executable,'-I',str(Path(__file__).with_name('example_runner.py'))]
                env={k:v for k,v in os.environ.items() if k not in {'OPENAI_API_KEY','CODEX_API_KEY'}}
                try:
                    result=subprocess.run(command,input=json.dumps({'code':block['code'],'stdin':case['stdin']}),capture_output=True,text=True,timeout=5,env=env)
                    actual=json.loads(result.stdout)
                    if 'error' in actual:status,message=('not_run' if actual['error'].startswith('UnsupportedExample:') else 'failed'),actual['error']
                    elif actual['stdout'].replace('\r\n','\n')!=case['stdout'].replace('\r\n','\n'):status,message='failed','Output osservato diverso da quello atteso: '+repr(actual['stdout'])
                    else:status,message='passed','Input e output corrispondono.'
                except (subprocess.TimeoutExpired,ValueError):status,message='failed','L’esempio non si è concluso entro il controllo isolato.'
                check={**base,'case':number,'status':status,'message':message}
                if status=='passed' and 'transcript' in actual:check['transcript']=actual['transcript']
                checks.append(check)
    return checks
