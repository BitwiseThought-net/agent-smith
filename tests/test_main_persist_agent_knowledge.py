import json
import os
import glob
import pytest

import main


def _read_only_file(pattern, isolated_cwd):
    matches = glob.glob(str(isolated_cwd / pattern))
    assert len(matches) == 1, f"expected exactly one match for {pattern}, got {matches}"
    with open(matches[0]) as f:
        return f.read()


class TestPersistAgentKnowledgeDefaultTemplate:
    def test_writes_txt_ledger_with_default_template(self, isolated_cwd, no_env_leak):
        main.persist_agent_knowledge(
            agent_name="researcher",
            framework="crewai",
            task_index=1,
            description="Investigate topic X",
            result="Findings: topic X is well understood.",
        )
        content = _read_only_file("knowledge/knowledge_ledger_researcher_task_1_*.txt", isolated_cwd)
        assert "AGENT_NAME: researcher" in content
        assert "FRAMEWORK_CONTEXT: crewai" in content
        assert "TASK_INDEX: 1" in content
        assert "ASSIGNED_MISSION_PROMPT: Investigate topic X" in content
        assert "Findings: topic X is well understood." in content

    def test_creates_knowledge_dir_if_missing(self, isolated_cwd, no_env_leak):
        assert not (isolated_cwd / "knowledge").exists()
        main.persist_agent_knowledge("coder", "crewai", 2, "desc", "result")
        assert (isolated_cwd / "knowledge").is_dir()

    def test_respects_custom_knowledge_dir_config(self, isolated_cwd, no_env_leak, monkeypatch):
        monkeypatch.setenv("KNOWLEDGE_DIR", "custom_knowledge")
        main.persist_agent_knowledge("coder", "crewai", 1, "desc", "result")
        assert (isolated_cwd / "custom_knowledge").is_dir()
        assert list((isolated_cwd / "custom_knowledge").glob("*.txt"))


class TestPersistAgentKnowledgeDictTemplate:
    def test_writes_json_ledger_when_template_is_a_dict(self, isolated_cwd, no_env_leak):
        template = {
            "agent": "{agent_name}",
            "summary": "Task {task_index}: {description} -> {result}",
        }
        main.persist_agent_knowledge(
            agent_name="writer",
            framework="crewai",
            task_index=3,
            description="Write a report",
            result="Report written",
            agent_template=template,
        )
        content = _read_only_file("knowledge/knowledge_ledger_writer_task_3_*.json", isolated_cwd)
        data = json.loads(content)
        assert data["agent"] == "writer"
        assert data["summary"] == "Task 3: Write a report -> Report written"


class TestPersistAgentKnowledgeErrorHandling:
    def test_template_missing_placeholder_key_does_not_raise(self, isolated_cwd, no_env_leak, caplog):
        # str.format on a template referencing an unknown field raises KeyError,
        # which persist_agent_knowledge should catch and log rather than crash
        # the whole mission pipeline over a formatting mistake in one agent's
        # custom ledger_template.
        bad_template = "Ledger for {agent_name}: {this_field_does_not_exist}"
        main.persist_agent_knowledge(
            agent_name="auditor",
            framework="crewai",
            task_index=1,
            description="desc",
            result="result",
            agent_template=bad_template,
        )
        # No exception propagated; nothing should have been written since
        # formatting failed before the open() call.
        assert not glob.glob(str(isolated_cwd / "knowledge" / "*"))
