"""Régressions de l'intercalage Stop/tamponne, sans modifier l'état utilisateur."""
import contextlib
import io
import json
import os
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

import vive_memoire as m


class ForkConcurrencyTest(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        root = Path(self.temp.name)
        self.state = root / 'state'
        self.env = patch.dict(os.environ, {
            'VM_ETAT': str(self.state), 'VM_MEMOIRE': str(root / 'memory'),
            'CLAUDE_CONFIG_DIR': str(root / 'config'),
        })
        self.env.start()
        self.addCleanup(self.env.stop)
        entries = [{'type': 'user', 'origin': {'kind': 'human'},
                    'message': {'role': 'user', 'content': str(i)}} for i in range(5)]
        self.parent = root / 'parent.jsonl'
        self.parent.write_text('\n'.join(json.dumps(e) for e in entries) + '\n')
        self.child = root / 'child.jsonl'
        self.child.write_text('\n'.join(json.dumps(dict(e, forkedFrom={'sessionId': 'PARENT'}))
                                        for e in entries) + '\n')
        m.ecrire_json(self.state / 'PARENT.json', {'transcript': str(self.parent)})
        m.noter_dette('PARENT', 5)

    def summarize(self):
        with contextlib.redirect_stdout(io.StringIO()):
            return m.mode_tamponne('CHILD', str(self.child))

    def test_parent_stop_between_debt_cleanup_and_return_sees_coverage(self):
        clear = m.effacer_dette_si
        responses = []

        def interleave(session, predicate):
            result = clear(session, predicate)
            state_file = self.state / 'PARENT.json'
            with contextlib.redirect_stdout(io.StringIO()) as output:
                m.mode_stop({'transcript_path': str(self.parent)}, 'PARENT',
                            m.lire_json(state_file, {}), state_file)
            responses.append(output.getvalue())
            return result

        with patch.object(m, 'effacer_dette_si', interleave):
            self.assertEqual(self.summarize(), 0)
        self.assertEqual(len(responses), 1)
        self.assertNotIn('"block"', responses[0])
        self.assertNotIn('PARENT', m.lire_dettes())

    def test_failed_parent_coverage_write_preserves_debt(self):
        write = m.ecrire_json

        def fail_parent(path, value):
            return False if path == self.state / 'PARENT.json' else write(path, value)

        with patch.object(m, 'ecrire_json', fail_parent):
            self.assertEqual(self.summarize(), 0)
        self.assertIn('PARENT', m.lire_dettes())

    def test_newer_parent_debt_is_preserved(self):
        clear = m.effacer_dette_si

        def new_debt(session, predicate):
            m.noter_dette('PARENT', 13)
            return clear(session, predicate)

        with patch.object(m, 'effacer_dette_si', new_debt):
            self.assertEqual(self.summarize(), 0)
        self.assertEqual(m.lire_dettes()['PARENT']['nb'], 13)


if __name__ == '__main__':
    unittest.main()
