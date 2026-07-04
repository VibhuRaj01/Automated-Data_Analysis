# Autonomous Data Analyst

An agentic AI-powered data analysis framework that automatically
analyzes tabular datasets, generates visualizations, debugs its own
code, produces insights, and builds an HTML report.

------------------------------------------------------------------------

## Features

-   Automatic dataset loading
-   Dataset profiling
-   LLM-driven analysis planning
-   Automatic Python code generation
-   Graph generation with Matplotlib
-   Automatic execution of generated code
-   Self-healing debugger for failed scripts
-   AI-generated business insights
-   Automated HTML report generation
-   Modular architecture

------------------------------------------------------------------------

## Pipeline

``` text
Dataset
    │
    ▼
Loader
    │
    ▼
Profiler
    │
    ▼
Insight Planner (LLM)
    │
    ▼
Code Generator (LLM)
    │
    ▼
Executor
    │
    ├──────────────┐
    │              │
 Success         Failure
    │              │
    ▼              ▼
Insight       Debugger (LLM)
 Writer            │
                   ▼
              Re-execution
                   │
                   ▼
            Report Builder
```

------------------------------------------------------------------------

## Project Structure

``` text
Data Analyst/
│
├── llm/
├── profiler/
├── planner/
├── generator/
├── executor/
├── debugger/
├── insight_writer/
├── report_builder/
├── pipeline/
├── templates/
├── outputs/
├── test/
├── run.py
└── README.md
```

------------------------------------------------------------------------

## Modules

### Module 1 --- Loader

Loads CSV, XLSX, XLS, JSON, Feather and Parquet datasets into a pandas
DataFrame.

### Module 2 --- Profiler

Builds a semantic profile containing: - Dataset metadata - Column
types - Missing values - Statistics - Sample values - Duplicate counts

### Module 3 --- Insight Planner

Uses Gemini to decide: - Which analyses should be performed - Which
columns should be used - Best visualization type - Analysis priority

### Module 4 --- Code Generator

Generates executable Python scripts that: - Load the dataset - Compute
statistics - Generate plots - Save figures - Emit structured metrics for
downstream insight generation

### Module 5 --- Executor

Runs generated scripts safely using `subprocess`, capturing: - stdout -
stderr - return code - execution time

### Module 6 --- Debugger

Automatically repairs failed Python scripts using Gemini and retries
execution.

### Module 7 --- Insight Writer

Generates concise business insights using: - Analysis objective -
Dataset profile - Computed statistics - Execution output

### Module 8 --- Report Builder

Produces a self-contained HTML report with: - Dataset summary - Charts -
AI-generated insights

------------------------------------------------------------------------

## Installation

``` bash
git clone <repository-url>
cd <repository>
python -m venv .venv
```

Install dependencies:

``` bash
pip install -r requirements.txt
```

Create a `.env` file:

``` text
GEMINI_API=YOUR_API_KEY
```

------------------------------------------------------------------------

## Running

``` bash
python run.py
```

The generated outputs are stored in:

``` text
outputs/
├── generated_code/
├── graphs/
├── reports/
└── logs/
```

------------------------------------------------------------------------

## Tech Stack

-   Python
-   Pandas
-   Matplotlib
-   Google Gemini
-   Jinja2
-   WeasyPrint (optional PDF export)

------------------------------------------------------------------------

## Roadmap

-   Docker sandbox for execution
-   Support additional LLM providers
-   Interactive dashboard
-   PowerPoint export
-   Multi-dataset analysis
-   SQL database support
-   Agent memory and planning improvements

------------------------------------------------------------------------

## Author

**Vibhu Raj**

Machine Learning Engineer \| Backend Engineer \| Building autonomous AI
systems.
