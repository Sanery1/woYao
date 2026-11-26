"""Local protocol test. This is a scripted HTTP server, not an LLM."""
import contextlib
import io
import json
import os
import threading
import unittest
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from unittest.mock import patch

import agent


def call(ident="c1", name="quote", arguments='{"unit_cents":1299,"quantity":3}'):
    return {"id": ident, "type": "function",
            "function": {"name": name, "arguments": arguments}}


class LocalProtocolTest(unittest.TestCase):
    def scenario(self, batches, expected_error=None):
        requests = []

        class Handler(BaseHTTPRequestHandler):
            def log_message(self, *args):
                pass

            def do_POST(self):
                self.server.testcase.assertEqual(self.path, "/v1/chat/completions")
                req = json.loads(self.rfile.read(int(self.headers["Content-Length"])))
                requests.append(req)
                i = len(requests) - 1
                if i < len(batches):
                    msg = {"role": "assistant", "content": None,
                           "tool_calls": batches[i]}
                    reason = "tool_calls"
                else:
                    msg = {"role": "assistant", "content": "完成，结果见工具数据"}
                    reason = "stop"
                raw = json.dumps({"choices": [{"message": msg,
                                                "finish_reason": reason}]}).encode()
                self.send_response(200)
                self.send_header("Content-Type", "application/json")
                self.end_headers()
                self.wfile.write(raw)

        server = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
        server.testcase = self
        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()
        try:
            base = f"http://127.0.0.1:{server.server_port}/v1"
            with patch.dict(os.environ, {"AGENT_BASE_URL": base,
                                         "AGENT_API_KEY": "",
                                         "AGENT_MODEL": "mock-model"}), contextlib.redirect_stdout(io.StringIO()):
                if expected_error:
                    with self.assertRaises(expected_error):
                        agent.run("test", max_turns=3)
                    return requests
                answer, messages = agent.run("test", max_turns=3)
            self.assertTrue(answer)
            return messages, requests
        finally:
            server.shutdown()
            server.server_close()
            thread.join()

    def test_success_and_wire_history(self):
        messages, requests = self.scenario([[call()]])
        self.assertEqual(len(requests), 2)
        self.assertEqual(json.loads(messages[3]["content"]), {"ok": True, "total_cents": 3897})
        sent = requests[1]["messages"]
        self.assertEqual(sent[2]["tool_calls"][0]["id"], sent[3]["tool_call_id"])

    def test_two_calls(self):
        messages, _ = self.scenario([[call("c1"), call("c2")]])
        self.assertEqual([m["tool_call_id"] for m in messages if m["role"] == "tool"], ["c1", "c2"])

    def test_tool_errors_are_returned(self):
        cases = [(call(name="shell"), "unknown_tool"),
                 (call(arguments="{"), "invalid_json"),
                 (call(arguments='{"quantity":3}'), "invalid_fields"),
                 (call(arguments='{"unit_cents":true,"quantity":3}'), "integers_required"),
                 (call(arguments='{"unit_cents":1299,"quantity":0}'), "out_of_range")]
        for tool_call, code in cases:
            with self.subTest(code=code):
                messages, requests = self.scenario([[tool_call]])
                self.assertEqual(json.loads(messages[3]["content"])["error"], code)
                self.assertEqual(requests[1]["messages"][3]["tool_call_id"], "c1")

    def test_budget(self):
        requests = self.scenario([[call()], [call()], [call()]], RuntimeError)
        self.assertEqual(len(requests), 3)

    def test_bad_protocol_stops(self):
        self.scenario([[call("same"), call("same")]], agent.ProtocolError)


if __name__ == "__main__":
    unittest.main(verbosity=2)
