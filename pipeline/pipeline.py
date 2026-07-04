from pathlib import Path

from profiler.loader import load_dataset
from profiler.profiler import profile_dataset

from planner.planner import generate_analysis_plan

from generator.generator import generate_code

from executor.executor import execute_script

from debugger.debugger import repair_code

from insight_writer.insight_writer import generate_insight

from report_builder.report_builder import build_report

MAX_DEBUG_ATTEMPTS = 3


def run_pipeline(dataset_path: str | Path):

    dataset_path = Path(dataset_path)

    print("=" * 80)
    print("AUTONOMOUS DATA ANALYST")
    print("=" * 80)

    # -------------------------------------------------------------
    # Module 1
    # -------------------------------------------------------------

    print("\n[1] Loading Dataset...")

    df = load_dataset(dataset_path)

    profile = profile_dataset(df)

    print("✓ Dataset Loaded")

    # -------------------------------------------------------------
    # Module 2
    # -------------------------------------------------------------

    print("\n[2] Planning Analysis...")

    analysis_plan = generate_analysis_plan(profile)

    print(f"✓ {len(analysis_plan)} analyses planned")

    report_items = []

    # -------------------------------------------------------------
    # Process each analysis
    # -------------------------------------------------------------

    for analysis in analysis_plan:

        print("\n" + "=" * 80)
        print(analysis["title"])
        print("=" * 80)

        # ---------------------------------------------------------
        # Module 3
        # ---------------------------------------------------------

        print("[3] Generating Code...")

        generated_code, graph_filename = generate_code(
            dataset_path=str(dataset_path),
            profile=profile,
            analysis=analysis,
        )

        script_path = Path("outputs/generated_code") / graph_filename.replace(
            ".png", ".py"
        )

        script_path.write_text(
            generated_code,
            encoding="utf-8",
        )

        # ---------------------------------------------------------
        # Module 4 + 5
        # ---------------------------------------------------------

        attempts = 0

        while True:

            execution_result = execute_script(script_path)

            if execution_result["success"]:
                print("✓ Execution Successful")
                break

            attempts += 1

            if attempts > MAX_DEBUG_ATTEMPTS:
                print("✗ Failed after maximum repair attempts.")
                break

            print(f"[Repair Attempt {attempts}]")

            repaired_code = repair_code(
                original_code=script_path.read_text(encoding="utf-8"),
                profile=profile,
                analysis=analysis,
                execution_result=execution_result,
            )

            script_path.write_text(
                repaired_code,
                encoding="utf-8",
            )

        if not execution_result["success"]:
            continue

        # ---------------------------------------------------------
        # Module 6
        # ---------------------------------------------------------

        print("[6] Generating Insight...")

        insight = generate_insight(
            profile=profile,
            analysis=analysis,
            execution_result=execution_result,
        )

        report_items.append(
            {
                "analysis": analysis,
                "chart_path": f"outputs/graphs/{graph_filename}",
                "insight": insight,
            }
        )

    # -------------------------------------------------------------
    # Module 7
    # -------------------------------------------------------------

    print("\n[7] Building Report...")

    report_path = build_report(
        profile=profile,
        report_items=report_items,
        dataset_name=dataset_path.stem,
    )

    print(f"\nReport saved to: {report_path}")

    return report_path
