"""CLI application for AutoForm."""

from __future__ import annotations

import asyncio
import sys
from typing import Any

from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.prompt import Confirm, Prompt
from rich.text import Text

from autoform import __app_name__, __version__
from autoform.infrastructure import Config, setup_logging

console = Console()


def _print_banner() -> None:
    """Print the application banner."""
    banner = Text()
    banner.append("Auto", style="bold cyan")
    banner.append("Form", style="bold green")
    banner.append(f"  v{__version__}", style="dim")

    console.print(
        Panel(
            banner,
            subtitle="Intelligent Form Auto-Fill Tool",
            border_style="blue",
            padding=(1, 4),
        )
    )
    console.print()


def _print_menu() -> None:
    """Print the main menu."""
    menu_items = [
        ("1", "Fill Form", "Auto-fill a web form"),
        ("2", "Profile", "Manage your user profile"),
        ("3", "Settings", "Configure AutoForm"),
        ("0", "Exit", "Exit AutoForm"),
    ]

    for key, title, description in menu_items:
        console.print(f"  [bold cyan][{key}][/bold cyan]  {title:<15} [dim]{description}[/dim]")

    console.print()


async def _handle_fill_form(config: Config) -> None:
    """Handle the Fill Form workflow."""
    from autoform.application.orchestrator import Orchestrator
    from autoform.cli.display import display_fill_result, display_form_info, display_mapping_table
    from autoform.domain.enums import ConfidenceLevel

    url = Prompt.ask("[bold]Enter form URL[/bold]")
    if not url:
        console.print("[red]URL is required.[/red]")
        return

    orchestrator = Orchestrator(config)

    try:
        # Step 1: Analyze
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
        ) as progress:
            task = progress.add_task("Analyzing form...", total=None)
            schema, mappings, profile = await orchestrator.analyze_form(url)
            progress.update(task, description="✅ Analysis complete!")

        # Step 2: Display results
        display_form_info(schema)
        display_mapping_table(mappings)

        # Step 3: Review
        console.print("[bold]Review Options:[/bold]")
        console.print("  [cyan]a[/cyan] - Accept all HIGH confidence mappings")
        console.print("  [cyan]r[/cyan] - Review each mapping individually")
        console.print("  [cyan]q[/cyan] - Cancel and close browser")
        console.print()

        choice = Prompt.ask("Choose", choices=["a", "r", "q"], default="a")

        if choice == "q":
            console.print("[dim]Cancelled.[/dim]")
            await orchestrator.close()
            return

        if choice == "a":
            # Auto-approve HIGH confidence
            Orchestrator.auto_approve_high_confidence(mappings)
            approved = sum(1 for m in mappings if m.approved)
            console.print(f"[green]Auto-approved {approved} HIGH confidence mappings.[/green]")

        elif choice == "r":
            # Individual review
            for mapping in mappings:
                if mapping.confidence_level == ConfidenceLevel.NO_MATCH:
                    continue

                level = mapping.confidence_level
                color = level.color
                symbol = level.symbol

                console.print(
                    f"  [{color}]{symbol}[/{color}] "
                    f"[bold]{mapping.form_field.label}[/bold] → "
                    f"[{color}]{mapping.profile_path}[/{color}] "
                    f"({mapping.confidence:.0%})"
                )

                approve = Confirm.ask("    Approve?", default=(level == ConfidenceLevel.HIGH))
                mapping.approved = approve

        # Step 4: Fill
        approved_count = sum(1 for m in mappings if m.approved)
        if approved_count == 0:
            console.print("[yellow]No mappings approved. Nothing to fill.[/yellow]")
            await orchestrator.close()
            return

        console.print()
        if not Confirm.ask(f"[bold]Fill {approved_count} fields?[/bold]", default=True):
            console.print("[dim]Cancelled.[/dim]")
            await orchestrator.close()
            return

        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
        ) as progress:
            task = progress.add_task("Filling form...", total=None)
            fill_result = await orchestrator.fill_form(mappings)
            progress.update(task, description="✅ Fill complete!")

        console.print()
        display_fill_result(fill_result)

        # Step 5: Submit?
        if Confirm.ask("[bold yellow]Submit the form?[/bold yellow]", default=False):
            submit_result = await orchestrator.submit_form(confirmed=True)
            if submit_result.success:
                console.print("[bold green]✅ Form submitted successfully![/bold green]")
            elif submit_result.needs_human_action:
                console.print(f"[bold yellow]⚠️  {submit_result.reason}[/bold yellow]")
            else:
                console.print(f"[bold red]❌ Submit failed: {submit_result.reason}[/bold red]")
        else:
            console.print("[dim]Form not submitted. Browser remains open for manual review.[/dim]")
            Prompt.ask("[dim]Press Enter to close browser[/dim]")

        await orchestrator.close()

    except Exception as e:
        console.print(f"[bold red]Error: {e}[/bold red]")
        await orchestrator.close()


async def _handle_profile(config: Config) -> None:
    """Handle profile management."""
    from autoform.profile.manager import ProfileManager
    from autoform.profile.storage import ProfileStorage

    storage = ProfileStorage(config.profile_dir)
    manager = ProfileManager(storage)

    console.print()
    console.print("[bold]Profile Management[/bold]")
    console.print("  [cyan]1[/cyan] - View current profile")
    console.print("  [cyan]2[/cyan] - Create new profile")
    console.print("  [cyan]3[/cyan] - Edit profile field")
    console.print("  [cyan]4[/cyan] - List all profiles")
    console.print("  [cyan]0[/cyan] - Back to main menu")
    console.print()

    choice = Prompt.ask("Choose", choices=["0", "1", "2", "3", "4"], default="1")

    if choice == "0":
        return

    if choice == "1":
        # View profile
        profile_name = config.get("profile", "default_profile", "default")
        if not manager.profile_exists(profile_name):
            console.print(f"[yellow]No profile '{profile_name}' found.[/yellow]")
            return

        profile = manager.get_profile(profile_name)
        all_fields = profile.get_all_fields()

        from rich.table import Table

        table = Table(title=f"Profile: {profile_name}", show_lines=True, border_style="dim")
        table.add_column("Field", style="cyan")
        table.add_column("Value", style="white")

        for path, value in sorted(all_fields.items()):
            display_value = str(value) if value else "[dim]—[/dim]"
            table.add_row(path, display_value)

        console.print(table)

    elif choice == "2":
        # Interactive profile creation
        from autoform.profile.manager import PROFILE_SCHEMA

        console.print("[bold]Create New Profile[/bold]")
        console.print("[dim]Press Enter to skip optional fields.[/dim]\n")

        profile_name = Prompt.ask("Profile name", default="default")
        data: dict[str, dict[str, Any]] = {}

        for category, fields in PROFILE_SCHEMA.items():
            console.print(f"\n[bold cyan]— {category.title()} —[/bold cyan]")
            data[category] = {}

            for field_name, description in fields.items():
                value = Prompt.ask(f"  {description}", default="")
                if value:
                    # Handle comma-separated lists
                    if "comma-separated" in description.lower():
                        value = [v.strip() for v in value.split(",")]
                    data[category][field_name] = value

        profile = manager.create_profile(data, profile_name)
        console.print(f"\n[green]✅ Profile '{profile_name}' created![/green]")
        summary = manager.get_profile_summary(profile_name)
        total = sum(summary.values())
        console.print(f"[dim]Fields filled: {total}[/dim]")

    elif choice == "3":
        # Edit field
        profile_name = Prompt.ask("Profile name", default="default")
        if not manager.profile_exists(profile_name):
            console.print(f"[red]Profile '{profile_name}' not found.[/red]")
            return

        field_path = Prompt.ask("Field path (e.g. personal.full_name)")
        value = Prompt.ask("New value")

        manager.update_field(profile_name, field_path, value)
        console.print(f"[green]✅ Updated {field_path}[/green]")

    elif choice == "4":
        # List profiles
        profiles = manager.list_profiles()
        if not profiles:
            console.print("[yellow]No profiles found.[/yellow]")
        else:
            for p in profiles:
                console.print(f"  • {p}")


def main() -> None:
    """Main entry point for the CLI application."""
    # Load config
    config = Config()

    # Setup logging
    setup_logging(
        level=config.log_level,
        log_format=config.log_format,
        redact_pii=config.redact_pii,
    )

    # Check for command-line arguments
    if len(sys.argv) > 1:
        arg = sys.argv[1]
        if arg in ("--version", "-v"):
            console.print(f"{__app_name__} v{__version__}")
            return
        if arg in ("--help", "-h"):
            _print_banner()
            console.print("[bold]Usage:[/bold]  autoform [command]")
            console.print()
            console.print("[bold]Commands:[/bold]")
            console.print("  (interactive)   Run interactive menu")
            console.print("  --version, -v   Show version")
            console.print("  --help, -h      Show this help")
            console.print()
            return

    # Interactive mode
    _print_banner()
    console.print("[dim]Type a number to select an option, or 0 to exit.[/dim]")
    console.print()
    _print_menu()

    while True:
        try:
            choice = console.input("[bold blue]>[/bold blue] ").strip()

            if choice == "0":
                console.print("[dim]Goodbye! 👋[/dim]")
                break
            elif choice == "1":
                asyncio.run(_handle_fill_form(config))
            elif choice == "2":
                asyncio.run(_handle_profile(config))
            elif choice == "3":
                console.print("[yellow]Settings editor coming soon...[/yellow]")
            else:
                console.print("[red]Invalid option. Please try again.[/red]")

            console.print()
            _print_menu()

        except (KeyboardInterrupt, EOFError):
            console.print("\n[dim]Goodbye! 👋[/dim]")
            break


if __name__ == "__main__":
    main()
