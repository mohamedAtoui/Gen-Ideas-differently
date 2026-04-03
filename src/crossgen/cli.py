"""CrossGen CLI — cross-domain idea generator."""

from __future__ import annotations

import asyncio
import json
import sys

import typer
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn

from .knowledge.triz import INVENTIVE_PRINCIPLES, get_principle, find_parameter
from .knowledge.principles import UNIVERSAL_PRINCIPLES, search_principles

app = typer.Typer(
    name="crossgen",
    help="CrossGen: Cross-Domain Idea Generator",
    no_args_is_help=True,
)
console = Console()

STAGE_LABELS = {
    "decompose": "Stage 1: Decompose",
    "abstract": "Stage 2: Abstract",
    "expand": "Stage 3: Expand domains",
    "mine": "Stage 4: Mine analogies",
    "synthesize": "Stage 5: Synthesize solutions",
    "evaluate": "Stage 6: Evaluate & rank",
}


def _format_result_markdown(result, problem: str) -> str:
    """Format pipeline result as a readable markdown document."""
    lines = []
    lines.append(f"# CrossGen Results\n")
    lines.append(f"**Problem:** {problem}\n")

    # Stage 1
    lines.append(f"## Stage 1: Decomposition\n")
    lines.append(f"- **Domain:** {result.problem.domain}")
    lines.append(f"- **Primary Function:** {result.problem.primary_function}")
    if result.problem.elaborated_problem:
        lines.append(f"- **Elaborated:** {result.problem.elaborated_problem}")
    if result.problem.contradictions:
        lines.append(f"- **Contradictions:** {len(result.problem.contradictions)}")
        for c in result.problem.contradictions:
            lines.append(f"  - {c.description} (improving: {c.improving}, worsening: {c.worsening})")
    lines.append("")

    # Stage 2
    lines.append(f"## Stage 2: Abstractions\n")
    lines.append(f"### SAPPhIRE\n")
    lines.append(f"**Effect:** {result.abstractions.sapphire.effect}\n")
    lines.append(f"**Phenomenon:** {result.abstractions.sapphire.phenomenon}\n")
    if result.abstractions.biologize:
        lines.append(f"### Biologize\n")
        lines.append(f"**Nature Questions:**\n")
        for q in result.abstractions.biologize.nature_questions:
            lines.append(f"- {q}")
        lines.append("")
    else:
        lines.append("### Biologize\n*Skipped*\n")
    lines.append(f"### WordTree\n")
    for exp in result.abstractions.wordtree.expansions:
        terms = ", ".join(exp.cross_domain_terms) if exp.cross_domain_terms else ""
        lines.append(f"- **{exp.verb}** -> {terms}")
    lines.append("")
    lines.append(f"### TRIZ\n")
    for p in result.abstractions.triz.principles_suggested:
        lines.append(f"- #{p.get('number', '?')}: {p.get('name', '?')} -- {p.get('description', '?')}")
    lines.append("")

    # Stage 3
    lines.append(f"## Stage 3: Domain Expansion\n")
    lines.append(f"| Domain | Distance | Source Lens | Rationale |")
    lines.append(f"|--------|----------|-------------|-----------|")
    for d in result.expansion.candidate_domains:
        lines.append(f"| {d.domain} | {d.distance_from_home} | {d.source_lens} | {d.rationale[:80]}... |")
    lines.append("")

    # Stage 4-6: Scored solutions
    if result.evaluation.scored_solutions:
        lines.append(f"## Solutions Ranked by Score\n")
        lines.append(f"| # | Source Domain | Mechanism | Nov | Feas | Depth | Score |")
        lines.append(f"|---|-------------|-----------|-----|------|-------|-------|")
        for i, scored in enumerate(result.evaluation.scored_solutions, 1):
            lines.append(
                f"| {i} | {scored.solution.source_domain} "
                f"| {scored.solution.source_mechanism[:60]} "
                f"| {scored.novelty:.2f} | {scored.feasibility:.2f} "
                f"| {scored.structural_depth:.2f} | {scored.combined_score:.2f} |"
            )
        lines.append("")

        # Detailed write-up for each solution
        for i, scored in enumerate(result.evaluation.scored_solutions, 1):
            lines.append(f"---\n")
            lines.append(f"### #{i} -- {scored.solution.source_domain} (score: {scored.combined_score:.2f})\n")
            lines.append(f"**Mechanism:** {scored.solution.source_mechanism}\n")
            lines.append(f"**Transfer Strength:** {scored.solution.transfer_strength}\n")
            lines.append(f"#### Approach\n")
            lines.append(f"{scored.solution.concrete_approach}\n")
            if scored.solution.candidate_inferences:
                lines.append(f"#### Key Predictions\n")
                for ci in scored.solution.candidate_inferences:
                    lines.append(f"- {ci}")
                lines.append("")
            if scored.solution.key_predictions:
                lines.append(f"#### Testable Predictions\n")
                for kp in scored.solution.key_predictions:
                    lines.append(f"- {kp}")
                lines.append("")
            lines.append(f"#### Structural Mappings\n")
            if scored.analogy.mappings:
                lines.append(f"| Source Element | Target Element | Relation |")
                lines.append(f"|---------------|----------------|----------|")
                for m in scored.analogy.mappings:
                    lines.append(f"| {m.source_element} | {m.target_element} | {m.relation_type} |")
                lines.append("")
            lines.append(f"#### Where It Breaks\n")
            lines.append(f"{scored.analogy.where_it_breaks}\n")
            if scored.reasoning:
                lines.append(f"#### Evaluation Reasoning\n")
                lines.append(f"{scored.reasoning}\n")

    # Recommendation
    if result.evaluation.top_recommendation:
        lines.append(f"---\n")
        lines.append(f"## Recommendation\n")
        lines.append(f"{result.evaluation.top_recommendation}\n")

    return "\n".join(lines)


@app.command()
def solve(
    problem: str = typer.Argument(help="Problem statement to solve"),
    model: str = typer.Option("claude-sonnet-4-6", "--model", "-m", help="LLM model to use"),
    output_json: bool = typer.Option(False, "--json", help="Output raw JSON"),
    output_file: str = typer.Option("", "--output", "-o", help="Save results to markdown file (e.g. -o results.md)"),
    skip_biologize: bool = typer.Option(False, "--skip-biologize", help="Skip the Biologize lens (saves 1 LLM call, avoids biology bias)"),
    prefer_stem: bool = typer.Option(False, "--prefer-stem", help="Bias domain expansion toward physics/engineering/math"),
    prefer_categories: str = typer.Option("", "--prefer-categories", help="Comma-separated domain categories to prefer (e.g. 'physics,engineering,math')"),
) -> None:
    """Run the full CrossGen pipeline on a problem."""
    from .pipeline import run_pipeline

    # Resolve preferred categories
    preferred_cats = None
    if prefer_stem:
        preferred_cats = ["physics", "engineering", "mathematics", "aerospace", "materials science"]
    elif prefer_categories:
        preferred_cats = [c.strip() for c in prefer_categories.split(",") if c.strip()]

    async def _run() -> None:
        stage_status: dict[str, str] = {}

        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
        ) as progress:
            tasks: dict[str, object] = {}
            for stage_name, label in STAGE_LABELS.items():
                tasks[stage_name] = progress.add_task(label, total=None)

            async def on_stage(stage: str, number: int, data: dict) -> None:
                status = data.get("status", "")
                if status == "running":
                    progress.update(tasks[stage], description=f"[yellow]{STAGE_LABELS[stage]}...")
                elif status == "done":
                    progress.update(tasks[stage], description=f"[green]{STAGE_LABELS[stage]} ✓")
                    progress.stop_task(tasks[stage])

            result = await run_pipeline(
                problem, model=model, on_stage=on_stage,
                skip_biologize=skip_biologize,
                preferred_domain_categories=preferred_cats,
            )

        if output_json:
            console.print_json(json.dumps(result.model_dump(), default=str))
            return

        if output_file:
            md = _format_result_markdown(result, problem)
            from pathlib import Path
            Path(output_file).write_text(md)
            console.print(f"[green]Results saved to {output_file}[/green]")
            return

        # Display results
        console.print()
        console.print(Panel(f"[bold]{problem}[/bold]", title="Problem", border_style="blue"))

        # Problem analysis
        console.print(Panel(
            f"[bold]Domain:[/bold] {result.problem.domain}\n"
            f"[bold]Primary Function:[/bold] {result.problem.primary_function}\n"
            f"[bold]Contradictions:[/bold] {len(result.problem.contradictions)}",
            title="Stage 1: Decomposition",
            border_style="cyan",
        ))

        # Abstractions summary
        bio_line = (
            f"[bold]Nature Questions:[/bold] {len(result.abstractions.biologize.nature_questions)}\n"
            if result.abstractions.biologize
            else "[dim]Biologize: skipped[/dim]\n"
        )
        console.print(Panel(
            f"[bold]SAPPhIRE Effect:[/bold] {result.abstractions.sapphire.effect}\n"
            f"{bio_line}"
            f"[bold]Word Expansions:[/bold] {len(result.abstractions.wordtree.expansions)}\n"
            f"[bold]TRIZ Principles:[/bold] {len(result.abstractions.triz.principles_suggested)}",
            title="Stage 2: Abstractions",
            border_style="cyan",
        ))

        # Domains
        domain_list = ", ".join(d.domain for d in result.expansion.candidate_domains)
        console.print(Panel(
            f"[bold]Candidate Domains:[/bold] {domain_list}",
            title="Stage 3: Domain Expansion",
            border_style="cyan",
        ))

        # Scored solutions
        if result.evaluation.scored_solutions:
            table = Table(title="Solutions Ranked by Score", border_style="green")
            table.add_column("#", style="dim", width=3)
            table.add_column("Source Domain", style="cyan")
            table.add_column("Mechanism", style="white", max_width=40)
            table.add_column("Nov", justify="right", style="magenta")
            table.add_column("Feas", justify="right", style="green")
            table.add_column("Depth", justify="right", style="blue")
            table.add_column("Score", justify="right", style="bold yellow")

            for i, scored in enumerate(result.evaluation.scored_solutions, 1):
                table.add_row(
                    str(i),
                    scored.solution.source_domain,
                    scored.solution.source_mechanism[:40],
                    f"{scored.novelty:.2f}",
                    f"{scored.feasibility:.2f}",
                    f"{scored.structural_depth:.2f}",
                    f"{scored.combined_score:.2f}",
                )

            console.print(table)

            # Detail on top 3
            for i, scored in enumerate(result.evaluation.scored_solutions[:3], 1):
                console.print()
                console.print(Panel(
                    f"[bold]Source:[/bold] {scored.solution.source_domain} — {scored.solution.source_mechanism}\n\n"
                    f"[bold]Approach:[/bold]\n{scored.solution.concrete_approach}\n\n"
                    f"[bold]Key Predictions:[/bold]\n" +
                    "\n".join(f"  • {ci}" for ci in scored.solution.candidate_inferences) +
                    f"\n\n[bold]Transfer Strength:[/bold] {scored.solution.transfer_strength}"
                    f"\n[bold]Where It Breaks:[/bold] {scored.analogy.where_it_breaks}",
                    title=f"#{i} — {scored.solution.source_domain} (score: {scored.combined_score:.2f})",
                    border_style="green" if i == 1 else "white",
                ))

        console.print(Panel(
            result.evaluation.top_recommendation,
            title="Recommendation",
            border_style="bold green",
        ))

    asyncio.run(_run())


# --- Principles subcommands ---

principles_app = typer.Typer(help="Browse TRIZ and universal principles")
app.add_typer(principles_app, name="principles")


@principles_app.command("list")
def principles_list(
    kind: str = typer.Option("all", help="triz|universal|all"),
) -> None:
    """List available principles."""
    if kind in ("triz", "all"):
        table = Table(title="TRIZ 40 Inventive Principles", border_style="blue")
        table.add_column("#", style="dim", width=4)
        table.add_column("Name", style="cyan")
        table.add_column("Description", style="white", max_width=60)

        for num, p in sorted(INVENTIVE_PRINCIPLES.items()):
            table.add_row(str(num), p["name"], p["description"][:60])
        console.print(table)

    if kind in ("universal", "all"):
        table = Table(title="Universal Cross-Domain Principles", border_style="green")
        table.add_column("Name", style="cyan")
        table.add_column("Domains", style="white", max_width=50)

        for p in UNIVERSAL_PRINCIPLES:
            table.add_row(p.name, ", ".join(p.domains[:4]) + "...")
        console.print(table)


@principles_app.command("search")
def principles_search(query: str = typer.Argument(help="Search term")) -> None:
    """Search principles by keyword."""
    # TRIZ
    triz_matches = find_parameter(query)
    if triz_matches:
        console.print(f"\n[bold]TRIZ parameters matching '{query}':[/bold]")
        for pid, name in triz_matches:
            console.print(f"  [{pid}] {name}")

    # Universal
    uni_matches = search_principles(query)
    if uni_matches:
        console.print(f"\n[bold]Universal principles matching '{query}':[/bold]")
        for p in uni_matches:
            console.print(f"  [cyan]{p.name}[/cyan]: {p.description[:80]}...")
            console.print(f"    Domains: {', '.join(p.domains)}")

    if not triz_matches and not uni_matches:
        console.print(f"[dim]No principles found matching '{query}'[/dim]")


def main() -> None:
    app()


if __name__ == "__main__":
    main()
