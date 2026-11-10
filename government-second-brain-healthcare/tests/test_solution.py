import copy
import unittest
from gsb.audit import AuditTrail
from gsb.kb import PolicyKnowledgeBase
from gsb.orchestrator import load_scenarios, run_simulation
from gsb.security import safe_event, sanitized_question


class ScenarioTests(unittest.TestCase):
    def test_policies_have_traceable_urls(self):
        kb = PolicyKnowledgeBase.from_file()
        self.assertGreaterEqual(len(kb.records), 6)
        self.assertTrue(all(r["source_url"].startswith("https://") for r in kb.records))

    def test_vector_retrieval(self):
        ids = [r["id"] for r in PolicyKnowledgeBase.from_file().search("health privacy confidentiality", 6)]
        self.assertIn("U1", ids)

    def test_stage_progression(self):
        for stage in (1, 2, 3):
            r = run_simulation(stage)
            self.assertEqual(stage, len(r["events"]))
            self.assertEqual(6, len(r["assessments"]))
            self.assertTrue(r["decision"]["human_approval_required"])
            self.assertTrue(r["evaluation"]["audit_chain_valid"])

    def test_stage_two_blocks_external_transfer(self):
        r = run_simulation(2)
        self.assertIn("external_llm_transfer", r["decision"]["blocked_actions"])
        self.assertIn("restricted_data_ingestion", r["decision"]["blocked_actions"])

    def test_stage_three_blocks_eligibility_changes(self):
        r = run_simulation(3)
        self.assertIn("automatic_eligibility_change", r["decision"]["blocked_actions"])
        self.assertFalse(any("approved" == a["action"] for a in r["audit"]))

    def test_personal_identifier_rejected(self):
        with self.assertRaises(ValueError):
            sanitized_question("Please find Emirates ID 784-1990-1234567-1")
        event = copy.deepcopy(load_scenarios()[0]); event["patient_id"] = "xxx"
        with self.assertRaises(ValueError):
            safe_event(event)

    def test_audit_tampering_detected(self):
        log = AuditTrail()
        log.append("event_released", {"event_id": "T1"}, timestamp="2026-11-10T00:00:00+00:00")
        log.append("decision_gate", {"approved": False}, timestamp="2026-11-10T00:01:00+00:00")
        self.assertTrue(log.verify())
        log.entries[0]["detail"]["event_id"] = "modified"
        self.assertFalse(log.verify())


if __name__ == "__main__":
    unittest.main()
