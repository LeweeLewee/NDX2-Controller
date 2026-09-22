"""Helper survives individual failures while retaining the fixture-only gate."""
import io
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import Mock, patch
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools'))
import m2_pipe

class PipeRecoveryTests(unittest.TestCase):
    def run_pipe(self, requests, client):
        vault=Mock(); vault.data={'controller':{'credential':'synthetic-fixture-only'}}
        stdin=io.TextIOWrapper(io.BytesIO((''.join(json.dumps(r)+'\n' for r in requests)).encode()))
        stdout=io.StringIO()
        with tempfile.TemporaryDirectory() as temporary:
            config=Path(temporary)/'config.json'
            config.write_text(json.dumps({'state':'unused','url':'https://127.0.0.1','trust':'unused'}))
            with patch.object(m2_pipe.sys,'argv',['m2_pipe',str(config)]), patch.object(m2_pipe.sys,'stdin',stdin), \
                 patch.object(m2_pipe.sys,'stdout',stdout), patch.object(m2_pipe,'Vault',return_value=vault), \
                 patch.object(m2_pipe,'Client',return_value=client):
                m2_pipe.main()
        vault.close.assert_called_once()
        return [json.loads(line) for line in stdout.getvalue().splitlines()]

    def test_offline_first_read_does_not_exit_helper(self):
        client=Mock(); client.post.side_effect=[OSError('offline'),{'fixture':True,'request_id':'second'}]
        replies=self.run_pipe([{'action':'snapshot'},{'action':'snapshot'}],client)
        self.assertEqual(replies,[{'transport_error':'UNAVAILABLE'},{'fixture':True,'request_id':'second'}])
        self.assertEqual(client.post.call_count,2)

    def test_live_mutation_still_blocked_without_configuration(self):
        client=Mock(); client.request.return_value={'fixture':False}
        replies=self.run_pipe([{'action':'play'},{'action':'amplifier'}],client)
        self.assertEqual(replies,[{'transport_error':'UNAVAILABLE'}]*2)
        client.post.assert_not_called()

    def test_lost_mutation_reply_is_not_retried(self):
        client=Mock(); client.request.return_value={'fixture':True}
        client.post.side_effect=[TimeoutError(),{'fixture':True}]
        replies=self.run_pipe([{'action':'amplifier'},{'action':'snapshot'}],client)
        self.assertEqual(replies,[{'transport_error':'UNAVAILABLE'},{'fixture':True}])
        self.assertEqual([c.args[1]['action'] for c in client.post.call_args_list],['amplifier','snapshot'])
