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
    "abstract": "Stage 2: Abstract (4 lenses)",
    "expand": "Stage 3: Expand domains",
    "mine": "Stage 4: Mine analogies",
    "synthesize": "Stage 5: Synthesize solutions",
    "evaluate": "Stage 6: Evaluate & rank",
}


@app.command()
def solve(
    problem: str = typer.Argument(help="Problem statement to solve"),
    model: str = typer.Option("claude-sonnet-4-6", "--model", "-m", help="LLM model to use"),
    output_json: bool = typer.Option(False, "--json", help="Output raw JSON"),
) -> None:
    """Run the full CrossGen pipeline on a problem."""
    from .pipeline import run_pipeline

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

            result = await run_pipeline(problem, model=model, on_stage=on_stage)

        if output_json:
            console.print_json(json.dumps(result.model_dump(), default=str))
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
        console.print(Panel(
            f"[bold]SAPPhIRE Effect:[/bold] {result.abstractions.sapphire.effect}\n"
            f"[bold]Nature Questions:[/bold] {len(result.abstractions.biologize.nature_questions)}\n"
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
