import importlib.util
from pathlib import Path
import tempfile
import unittest

import test_lessons


@unittest.skipUnless(importlib.util.find_spec('reportlab') and importlib.util.find_spec('pypdf'), 'Dipendenze di verifica PDF non installate')
class LessonRenderTests(unittest.TestCase):
    def test_pdf_retains_code_indentation_unicode_tables_and_all_content(self):
        from pypdf import PdfReader
        from didactyx_engine.lesson_render import export_pdf,render_html
        case=test_lessons.LessonTests();case.setUp()
        try:
            case.generate(['L1']);version=case.manager.store.head(case.plan_id,'L1')
            blocks=version['data']['sections'][0]['blocks']
            blocks += [
                {'kind':'definition','term':'Assegnazione','text':'Associa un nome a un valore.'},
                {'kind':'example','title':'Passaggi motivati','steps':['Individua i dati.','Scegli il tipo.'],'conclusion':'Il tipo guida l’operazione.'},
                {'kind':'list','items':['Prima osserva.','Poi verifica.']},
                {'kind':'table','headers':['Caso','Risultato'],'rows':[['Valore maggiore','Ramo vero'],['Valore minore','Ramo falso']]},
                {'kind':'formula','expression':'a² + b² = c²','explanation':'Esempio di notazione lineare Unicode.'},
                {'kind':'callout','title':'Errore frequente','text':'= assegna; == confronta.'},
                {'kind':'code','language':'python','code':'if 3 > 2:\n    print("È vero: perché 3 è maggiore di 2")','execution':'check','cases':[{'stdin':[],'stdout':'È vero: perché 3 è maggiore di 2\n'}],'explanation':'Il rientro delimita il blocco.'},
            ]
            with tempfile.TemporaryDirectory() as folder:
                result=export_pdf(version,folder);pdf=PdfReader(result['path']);text='\n'.join(p.extract_text() for p in pdf.pages)
                html=render_html(version)
                for phrase in ['Passaggi motivati','Ramo vero','Errore frequente','Il rientro delimita il blocco.','a² + b² = c²']:
                    self.assertIn(phrase,text);self.assertIn(phrase,html)
                self.assertIn('    print(',text)
                self.assertIn('Che cosa imparerai',text)
                self.assertNotIn('Note per il docente',text)
                self.assertGreaterEqual(len(pdf.pages),2)
        finally:case.tearDown()

if __name__=='__main__':unittest.main()
