# File: Dockerfile
```dockerfile
FROM ubuntu:22.04

# Install system dependencies
RUN apt-get update && apt-get install -y \
    python3 python3-pip python3-venv \
    build-essential clang llvm libclang-dev \
    afl clang-tools valgrind \
    openjdk-11-jre-headless \
    curl git

# Install SonarScanner
RUN curl -sSLo /opt/sonar-scanner.zip https://binaries.sonarsource.com/Distribution/sonar-scanner-cli/sonar-scanner-cli-4.8.0.2856-linux.zip \
    && unzip /opt/sonar-scanner.zip -d /opt \
    && ln -s /opt/sonar-scanner-4.8.0.2856-linux/bin/sonar-scanner /usr/local/bin/sonar-scanner

# Install Semgrep and other tools
RUN pip3 install --no-cache-dir semgrep

# Set workdir
WORKDIR /workspace

ENTRYPOINT ["/bin/bash"]
``` 

# File: requirements.txt
```text
openai>=0.27.0
pandas>=1.4.0
matplotlib>=3.5.0
seaborn>=0.11.0
pytest>=7.0.0
jupyter>=1.0.0
``` 

# File: Makefile
```make
.PHONY: all build lint test run

all: build lint test

build:
	python3 -m venv venv && \
	source venv/bin/activate && pip install -r requirements.txt

lint:
	flake8 generate_inputs.py run_fuzzers.py static_analysis.py dynamic_analysis.py prompt_refinement.py analysis.py

test:
	pytest tests/

run:
	source venv/bin/activate && python generate_inputs.py && \
	python run_fuzzers.py && python dynamic_analysis.py && \
	python static_analysis.py && python analysis.py
``` 

# File: .github/workflows/ci.yml
```yaml
name: CI
on: [push, pull_request]
jobs:
  build-and-test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.10'
      - name: Install dependencies
        run: |
          python -m venv venv
          source venv/bin/activate
          pip install -r requirements.txt
      - name: Lint code
        run: |
          source venv/bin/activate
          flake8 .
      - name: Run tests
        run: |
          source venv/bin/activate
          pytest --maxfail=1 --disable-warnings -q
``` 

# File: prompts.json
```json
{
  "cjson_edge_cases": "Generate malformed JSON strings that test cJSON parser for nested arrays, missing commas, and extraneous characters.",
  "xml_boundary_tests": "Produce XML inputs with deep nesting levels and mismatched tags to test TinyXML-2 parser for stack overflow and invalid closure.",
  "sql_injection_tests": "Create SQL injection payloads for login form inputs, including tautology-based and UNION-based attacks.",
  "yaml_fuzz_cases": "Generate invalid YAML documents with recursive anchors and improper indentation to test LibYAML for memory errors.",
  "http_dos_attack": "Craft HTTP request payloads that induce infinite loops or heavy computation in a REST API handler to test denial-of-service resilience."
}
