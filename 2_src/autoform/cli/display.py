"""CLI display utilities for rich terminal output."""

from __future__ import annotations

from typing import Any

from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

from autoform.domain.enums import ConfidenceLevel, FillStatus
from autoform.domain.models import FieldMapping, FillResult, FormSchema

console = Console()


def display_form_info(schema: FormSchema) -> None:
    """Display analyzed form information."""
    info = Text()
    info.append("Title: ", style="bold")
    info.append(f"{schema.title or 'Untitled'}\n")
    info.append("URL: ", style="bold")
    info.append(f"{schema.url}\n", style="dim")
    info.append("Platform: ", style="bold")
    info.append(f"{schema.platform.value}\n")
    info.append("Fields: ", style="bold")
    info.append(f"{schema.field_count}\n")

    if schema.has_captcha:
        info.append("⚠️  CAPTCHA detected\n", style="bold yellow")

    console.print(Panel(info, title="📋 Form Analysis", border_style="blue"))
    console.print()


def display_mapping_table(mappings: list[FieldMapping]) -> None:
    """Display mapping results in a color-coded table."""
    table = Table(
        title="🔗 Field Mapping Results",
        show_lines=True,
        border_style="dim",
    )

    table.add_column("#", style="dim", width=3, justify="right")
    table.add_column("Form Field", style="white", min_width=20)
    table.add_column("Type", style="cyan", width=10)
    table.add_column("Profile Path", min_width=22)
    table.add_column("Confidence", width=12, justify="center")
    table.add_column("Status", width=10, justify="center")

    for i, mapping in enumerate(mappings, 1):
        level = mapping.confidence_level
        confidence_text = f"{mapping.confidence:.0%}" if mapping.confidence > 0 else "—"

        # Color based on confidence
        if level == ConfidenceLevel.HIGH:
            conf_style = "bold green"
            status = "✓ AUTO"
            path_style = "green"
        elif level == ConfidenceLevel.MEDIUM:
            conf_style = "bold yellow"
            status = "⚠ REVIEW"
            path_style = "yellow"
        elif level == ConfidenceLevel.LOW:
            conf_style = "red"
            status = "❓ LOW"
            path_style = "red"
        else:
            conf_style = "dim"
            status = "✗ NONE"
            path_style = "dim"

        profile_path = mapping.profile_path or "—"

        table.add_row(
            str(i),
            mapping.form_field.label,
            mapping.form_field.field_type.value,
            Text(profile_path, style=path_style),
            Text(confidence_text, style=conf_style),
            Text(status, style=conf_style),
        )

    console.print(table)
    console.print()

    # Summary
    total = len(mappings)
    high = sum(1 for m in mappings if m.confidence_level == ConfidenceLevel.HIGH)
    medium = sum(1 for m in mappings if m.confidence_level == ConfidenceLevel.MEDIUM)
    low = sum(1 for m in mappings if m.confidence_level == ConfidenceLevel.LOW)
    no_match = sum(1 for m in mappings if m.confidence_level == ConfidenceLevel.NO_MATCH)

    summary = (
        f"  [green]✓ High: {high}[/green]  "
        f"[yellow]⚠ Medium: {medium}[/yellow]  "
        f"[red]❓ Low: {low}[/red]  "
        f"[dim]✗ No match: {no_match}[/dim]  "
        f"[bold]Total: {total}[/bold]"
    )
    console.print(summary)
    console.print()


def display_fill_result(result: FillResult) -> None:
    """Display fill results."""
    table = Table(
        title="📝 Fill Results",
        show_lines=True,
        border_style="dim",
    )

    table.add_column("Field", style="white", min_width=20)
    table.add_column("Status", width=10, justify="center")
    table.add_column("Details", style="dim")

    for fr in result.field_results:
        if fr.status == FillStatus.FILLED:
            status_text = Text("✓ Filled", style="green")
        elif fr.status == FillStatus.SKIPPED:
            status_text = Text("— Skip", style="dim")
        elif fr.status == FillStatus.FAILED:
            status_text = Text("✗ Failed", style="red")
        elif fr.status == FillStatus.BLOCKED:
            status_text = Text("🚫 Block", style="yellow")
        else:
            status_text = Text("⚠ Error", style="red")

        table.add_row(
            fr.field.label,
            status_text,
            fr.reason or "",
        )

    console.print(table)
    console.print()

    # Summary
    console.print(
        f"  [green]Filled: {result.filled_count}[/green]  "
        f"[dim]Skipped: {result.skipped_count}[/dim]  "
        f"[red]Failed: {result.failed_count}[/red]  "
        f"Success rate: [bold]{result.success_rate:.0%}[/bold]  "
        f"Time: {result.processing_time_ms:.0f}ms"
    )
    console.print()
