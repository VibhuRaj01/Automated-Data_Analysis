# Autonomous Data Analyst LLM

## Project Specification (`task.md`)

## Goal

Build an AI-powered data analysis system capable of taking a dataset
(CSV, Excel, SQL, Parquet, etc.), automatically understanding its
structure, planning meaningful analyses, generating Python code to
perform those analyses, executing the code, recovering from failures,
and finally producing a professional report containing visualizations
and insights.

Unlike traditional BI dashboards where users must ask questions
manually, this system should proactively discover interesting patterns
and present them to the user.

------------------------------------------------------------------------

# High-Level Workflow

    Dataset
        │
        ▼
    1. Data Profiler (Python)
        │
        ▼
    2. Insight Planner (LLM)
        │
        ▼
    For each planned analysis
        │
        ▼
    3. Code Generator (LLM)
        │
        ▼
    4. Code Executor (Python Sandbox)
        │
     ┌──┴─────────────┐
     │                │
    Success        Failure
     │                │
     ▼                ▼
    5. Insight      Debugger (LLM)
    Writer (LLM)       │
     │                 ▼
     └────── Retry Execution
        │
        ▼
    6. Report Builder (Python)
        │
        ▼
    HTML / PDF Report

------------------------------------------------------------------------

# Module 1 -- Data Profiler (Python)

## Objective

Understand the dataset without using an LLM.

## Responsibilities

-   Load the dataset.
-   Detect file type.
-   Infer column data types.
-   Compute summary statistics.
-   Detect missing values.
-   Detect duplicate rows.
-   Detect categorical vs numerical columns.
-   Detect datetime columns.
-   Generate metadata for downstream agents.

## Input

Dataset file.

## Output (JSON)

Example:

``` json
{
  "rows": 12054,
  "columns": 14,
  "column_info": [
    {
      "name": "Revenue",
      "dtype": "float",
      "mean": 245.8,
      "std": 41.3
    }
  ]
}
```

## Suggested Libraries

-   pandas
-   numpy
-   scipy
-   polars (future)

------------------------------------------------------------------------

# Module 2 -- Insight Planner (LLM)

## Objective

Reason about the dataset and decide which analyses are valuable.

The model should not write Python code. It should only decide *what*
should be analyzed.

## Input

-   Dataset profile
-   Column metadata
-   Optional business context

## Responsibilities

-   Identify useful analyses.
-   Prioritize analyses.
-   Select visualization types.
-   Choose required columns.
-   Explain why each analysis is useful.

## Output

``` json
[
  {
    "priority": 1,
    "title": "Revenue Trend",
    "chart": "line",
    "columns": ["Date", "Revenue"],
    "reason": "Understand long-term growth."
  }
]
```

------------------------------------------------------------------------

# Module 3 -- Code Generator (LLM)

## Objective

Generate Python code for a single analysis.

## Input

-   Analysis goal
-   Required columns
-   Dataset path
-   Visualization requirements

## Responsibilities

-   Load the dataset.
-   Perform aggregation/filtering.
-   Create the requested visualization.
-   Save graph to disk.
-   Return executable Python code only.

## Constraints

-   No explanations.
-   One graph per generation.
-   Use deterministic libraries.
-   Save figures to a predictable location.

Suggested libraries:

-   matplotlib
-   plotly (future)

------------------------------------------------------------------------

# Module 4 -- Code Executor (Python)

## Objective

Execute generated Python code safely.

## Why This Exists

LLMs cannot execute code. Python is responsible for execution.

## Execution Flow

1.  Receive generated Python.
2.  Save it as a temporary script.
3.  Execute the script in an isolated environment.
4.  Capture:
    -   Exit code
    -   Standard output
    -   Standard error
    -   Generated files

## Future Improvements

Run each script inside Docker with:

-   CPU limits
-   Memory limits
-   Execution timeout
-   Restricted filesystem
-   No internet access (optional)

## Output

``` json
{
  "status": "success",
  "stdout": "...",
  "stderr": "",
  "generated_files": [
    "graph1.png"
  ]
}
```

------------------------------------------------------------------------

# Module 5 -- Debugger (LLM)

## Objective

Automatically repair failed code.

## Trigger

Only execute when Module 4 reports a failure.

## Input

-   Original code
-   Stack trace
-   Dataset schema
-   Analysis objective

## Responsibilities

-   Identify the error.
-   Modify only what is required.
-   Preserve the original intent.
-   Return corrected Python code.

Retry until success or a configurable retry limit is reached.

------------------------------------------------------------------------

# Module 6 -- Insight Writer (LLM)

## Objective

Convert numerical results into human-readable insights.

## Input

-   Analysis goal
-   Summary statistics
-   Optional chart image
-   Computed metrics

## Responsibilities

-   Explain trends.
-   Highlight anomalies.
-   Describe correlations.
-   Mention possible business implications.
-   Avoid stating obvious facts.

Example:

-   Revenue increased steadily across Q2.
-   March contains a significant spike.
-   Category A contributes most of the total revenue.

------------------------------------------------------------------------

# Module 7 -- Report Builder (Python)

## Objective

Assemble a polished report.

## Responsibilities

-   Create HTML/PDF output.
-   Embed graphs.
-   Insert LLM-generated insights.
-   Maintain consistent formatting.
-   Generate a table of contents.

The report builder should use templates rather than an LLM for layout.

Suggested tools:

-   Jinja2
-   WeasyPrint (future)
-   ReportLab (optional)

------------------------------------------------------------------------

# Data Flow Between Modules

Every module should communicate using structured JSON.

Advantages:

-   Easier debugging
-   Replaceable models
-   Easier testing
-   Versioned interfaces
-   Reproducible pipeline

The only exceptions are:

-   Code Generator → Python source code
-   Insight Writer → Natural language text

------------------------------------------------------------------------

# Error Recovery Strategy

    Generate Code
          │
          ▼
    Execute
          │
     ┌────┴────┐
     │         │
    Pass     Fail
     │         │
     ▼         ▼
    Continue  Debugger
                │
                ▼
          Regenerate Code
                │
                ▼
             Execute

------------------------------------------------------------------------

# Suggested Project Structure

    project/
    │
    ├── data/
    ├── outputs/
    │   ├── graphs/
    │   ├── reports/
    │   └── logs/
    │
    ├── profiler/
    ├── planner/
    ├── generator/
    ├── executor/
    ├── debugger/
    ├── insight_writer/
    ├── report_builder/
    │
    ├── prompts/
    ├── templates/
    ├── tests/
    └── main.py

------------------------------------------------------------------------

# Future Enhancements

-   SQL database support
-   Natural language follow-up questions
-   Interactive dashboard
-   Multi-agent orchestration
-   Time-series forecasting
-   Statistical testing
-   Automatic anomaly detection
-   User feedback loop
-   Agent evaluation metrics
-   Local and cloud LLM support

------------------------------------------------------------------------

# Success Criteria

The project is successful if it can:

1.  Accept a dataset with no manual preprocessing.
2.  Understand the dataset automatically.
3.  Decide meaningful analyses.
4.  Generate executable Python code.
5.  Recover from execution failures automatically.
6.  Produce correct visualizations.
7.  Explain findings in natural language.
8.  Deliver a professional HTML or PDF report with minimal user
    intervention.
