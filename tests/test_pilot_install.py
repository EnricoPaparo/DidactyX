from contextlib import closing
from copy import deepcopy
from pathlib import Path
import sys
import tempfile
import unittest

import test_lessons
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from install_lesson_pilot import install
from didactyx_engine.store import Store
from didactyx_engine.lesson_store import LessonStore
from didactyx_engine.planning_store import PlanningStore


class PilotInstallTests(unittest.TestCase):
    def setUp(self):
        self.case=test_lessons.LessonTests();self.case.setUp();self.case.generate(['L1','L2'])
        self.annual=PlanningStore(self.case.store).get_version(self.case.program['id'],self.case.plan_id)
        self.versions=[self.case.manager.store.head(self.case.plan_id,i) for i in ['L1','L2']]
        self.folder=tempfile.TemporaryDirectory();self.target=Store(self.folder.name)
        self.existing=self.target.create({'title':'Programma personale da conservare'})
    def tearDown(self):self.case.tearDown();self.folder.cleanup()
    def test_import_is_additive_and_rebinds_real_dependencies(self):
        result=install(self.folder.name,self.annual,self.versions)
        self.assertEqual(self.target.get(self.existing['id']),self.existing)
        self.assertEqual(len(self.target.list_programs()),2)
        lessons=LessonStore(self.target);second=lessons.version(result['program_id'],result['version_ids'][1])
        self.assertEqual(second['data']['continuity'][0]['version_id'],result['version_ids'][0])
        with closing(self.target.connect()) as c:self.assertEqual(c.execute('PRAGMA foreign_key_check').fetchall(),[])
        with self.assertRaises(ValueError):install(self.folder.name,self.annual,self.versions)
        self.assertEqual(len(self.target.list_programs()),2)
    def test_invalid_dependency_does_not_leave_a_partial_program(self):
        versions=deepcopy(self.versions);versions[1]['data']['continuity'][0]['version_id']='missing'
        with self.assertRaises(ValueError):install(self.folder.name,self.annual,versions)
        self.assertEqual(self.target.list_programs(),[self.existing])

if __name__=='__main__':unittest.main()
