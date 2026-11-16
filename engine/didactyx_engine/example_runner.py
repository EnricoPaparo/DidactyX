"""Controllo isolato di esempi Python limitati alle operazioni didattiche supportate."""
import ast
import builtins
import contextlib
import io
import json
import sys

ALLOWED = {'print','input','int','float','str','bool','len','abs','round','min','max','range','sum','list','tuple','dict','set','sorted','enumerate','zip','isinstance'}
METHODS = {'append','extend','pop','count','index','sort','reverse','strip','lower','upper','split','join','replace','startswith','endswith','items','keys','values','get'}
BLOCKED = (ast.Import, ast.ImportFrom, ast.ClassDef, ast.AsyncFunctionDef, ast.With, ast.AsyncWith,
           ast.Global, ast.Nonlocal, ast.Lambda, ast.Delete, ast.Yield, ast.YieldFrom, ast.Await)

class UnsupportedExample(ValueError): pass


def run(code, lines):
    tree = ast.parse(code)
    functions = {n.name for n in ast.walk(tree) if isinstance(n, ast.FunctionDef)}
    for node in ast.walk(tree):
        if isinstance(node, BLOCKED): raise UnsupportedExample('Costrutto non supportato dal controllo isolato')
        if isinstance(node, ast.Name) and node.id.startswith('_'): raise UnsupportedExample('Nome non consentito')
        if isinstance(node, ast.FunctionDef) and (node.decorator_list or node.name.startswith('_')): raise UnsupportedExample('Definizione non supportata')
        if isinstance(node, ast.Attribute) and node.attr not in METHODS: raise UnsupportedExample('Metodo non supportato dal controllo isolato')
        if isinstance(node, ast.Call):
            if isinstance(node.func, ast.Name) and node.func.id not in ALLOWED | functions: raise UnsupportedExample('Funzione non supportata dal controllo isolato')
            if not isinstance(node.func, (ast.Name, ast.Attribute)): raise UnsupportedExample('Chiamata non supportata')
    transcript=io.StringIO()
    class LimitedOutput(io.StringIO):
        def write(self, value):
            if self.tell()+len(value)>100000: raise ValueError('Output eccessivo per un esempio')
            transcript.write(value)
            return super().write(value)
    output = LimitedOutput(); inputs = iter(lines)
    def read(prompt=''):
        output.write(str(prompt))
        try:
            value=next(inputs);transcript.write(value+'\n');return value
        except StopIteration:raise EOFError('Input di prova insufficiente') from None
    safe = {name:getattr(builtins,name) for name in ALLOWED if name!='input'}; safe['input']=read
    with contextlib.redirect_stdout(output): exec(compile(tree,'<esempio>','exec'),{'__builtins__':safe})
    return {'stdout':output.getvalue(),'transcript':transcript.getvalue()}


def main():
    try:
        import resource
        limits=[(resource.RLIMIT_CPU,3),(resource.RLIMIT_FSIZE,0)]
        if sys.platform!='darwin':limits.append((resource.RLIMIT_DATA,256*1024*1024))
        for kind,limit in limits:
            hard=resource.getrlimit(kind)[1]
            value=limit if hard==resource.RLIM_INFINITY else min(hard,limit)
            resource.setrlimit(kind,(value,hard))
        value=json.load(sys.stdin); result=run(value['code'],value['stdin'])
    except BaseException as error:result={'error':type(error).__name__+': '+str(error)}
    print(json.dumps(result,ensure_ascii=False))

if __name__ == '__main__': main()
