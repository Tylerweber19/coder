# ===========================
# File: tests/test_generate_inputs.py
# ===========================
import os
import json
import tempfile
import pytest
from generate_inputs import generate_tests

@pytest.fixture
def prompts_file(tmp_path):
    data = {
        "test_case_1": "Generate an edge-case JSON string for testing.",
        "test_case_2": "Produce SQLi payload for login input."
    }
    p = tmp_path / "prompts.json"
    p.write_text(json.dumps(data))
    return str(p)

def test_generate_tests_creates_files(prompts_file, tmp_path, monkeypatch):
    # Monkeypatch OpenAI client
    class DummyResp:
        def __init__(self, content):
            self.choices = [type("c", (), {"message": type("m", (), {"content": content})})]
    class DummyClient:
        def __init__(self): pass
        def chat(self): return self
        def completions(self, **kwargs): return self
        def create(self, **kwargs): return DummyResp("dummy output")
    monkeypatch.setattr("generate_inputs.OpenAI", lambda: DummyClient())

    out_dir = tmp_path / "outputs"
    generate_tests(model="dummy-model", prompts=json.load(open(prompts_file)), output_dir=str(out_dir))
    # Assert files created
    files = os.listdir(str(out_dir))
    assert "test_case_1.txt" in files
    assert "test_case_2.txt" in files


# ===========================
# File: tests/test_analysis.py
# ===========================
import pandas as pd
import pytest
from analysis import load_crash_data

def test_load_crash_data(tmp_path):
    df = pd.DataFrame({"Tool": ["AFL", "LLM"], "CrashesPer100": [5.1, 7.4]})
    csv_path = tmp_path / "crash.csv"
    df.to_csv(str(csv_path), index=False)
    df_loaded = load_crash_data(str(csv_path))
    assert list(df_loaded.columns) == ["Tool", "CrashesPer100"]
    assert df_loaded.loc[df_loaded.Tool == "LLM", "CrashesPer100"].iloc[0] == 7.4


# ===========================
# File: scripts/generate_notebook_template.py
# ===========================
import nbformat as nbf

def create_pipeline_notebook(output_path="pipeline_analysis_template.ipynb"):
    nb = nbf.v4.new_notebook()
    nb.cells = [
        nbf.v4.new_markdown_cell("# LLM Testing Pipeline Analysis"),
        nbf.v4.new_markdown_cell("This notebook outlines the steps for visualizing test metrics using pandas, matplotlib, and seaborn."),
        nbf.v4.new_code_cell("import pandas as pd"),
        nbf.v4.new_code_cell("import matplotlib.pyplot as plt\nimport seaborn as sns"),
        nbf.v4.new_markdown_cell("## Load Crash Data"),
        nbf.v4.new_code_cell("df = pd.read_csv('metrics/crash_frequency.csv')\ndf.head()"),
        nbf.v4.new_markdown_cell("## Crash Frequency Comparison"),
        nbf.v4.new_code_cell("sns.barplot(x='Tool', y='CrashesPer100', data=df)\nplt.show()"),
        nbf.v4.new_markdown_cell("## Static Analysis Heatmap"),
        nbf.v4.new_code_cell("# Load SonarQube alerts\nalerts = pd.read_csv('metrics/sonarqube_alerts.csv')\nsns.heatmap(alerts.pivot('Module','Severity','Count'), annot=True)\nplt.show()")
    ]
    with open(output_path, 'w') as f:
        nbf.write(nb, f)

if __name__ == '__main__':
    create_pipeline_notebook()
