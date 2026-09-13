"""CLI application for AutoForm with Vietnamese UI."""

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
            subtitle="Công cụ tự động điền Form thông minh (Intelligent Form Auto-Fill Tool)",
            border_style="blue",
            padding=(1, 4),
        )
    )
    console.print()


def _print_menu() -> None:
    """Print the main menu."""
    menu_items = [
        ("1", "Tự động điền Form", "Phân tích và điền biểu mẫu trực tuyến"),
        ("2", "Quản lý Profile", "Xem, tạo mới hoặc chỉnh sửa hồ sơ cá nhân"),
        ("3", "Cài đặt hệ thống", "Cấu hình tham số ứng dụng AutoForm"),
        ("0", "Thoát ứng dụng", "Đóng chương trình AutoForm"),
    ]

    for key, title, description in menu_items:
        console.print(f"  [bold cyan][{key}][/bold cyan]  {title:<22} [dim]{description}[/dim]")

    console.print()


async def _handle_fill_form(config: Config) -> None:
    """Handle the Fill Form workflow."""
    from autoform.application.orchestrator import Orchestrator
    from autoform.cli.display import display_fill_result, display_form_info, display_mapping_table
    from autoform.domain.enums import ConfidenceLevel

    url = Prompt.ask("[bold]Nhập địa chỉ URL biểu mẫu (Form URL)[/bold]")
    if not url:
        console.print("[red]Vui lòng nhập đường dẫn URL.[/red]")
        return

    orchestrator = Orchestrator(config)

    try:
        # Step 1: Analyze
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
        ) as progress:
            task = progress.add_task("Đang phân tích cấu trúc Form...", total=None)
            schema, mappings, profile = await orchestrator.analyze_form(url)
            progress.update(task, description="✅ Phân tích biểu mẫu hoàn tất!")

        # Step 2: Display results
        display_form_info(schema)
        display_mapping_table(mappings)

        # Step 3: Review
        console.print("[bold]Các tùy chọn duyệt (Review Options):[/bold]")
        console.print("  [cyan]a[/cyan] - Tự động chấp nhận tất cả các trường có độ tin cậy CAO (HIGH)")
        console.print("  [cyan]r[/cyan] - Xem và phê duyệt thủ công từng trường riêng biệt")
        console.print("  [cyan]q[/cyan] - Hủy bỏ và đóng trình duyệt")
        console.print()

        choice = Prompt.ask("Lựa chọn của bạn", choices=["a", "r", "q"], default="a")

        if choice == "q":
            console.print("[dim]Đã hủy bỏ.[/dim]")
            await orchestrator.close()
            return

        if choice == "a":
            # Auto-approve HIGH confidence
            Orchestrator.auto_approve_high_confidence(mappings)
            approved = sum(1 for m in mappings if m.approved)
            console.print(f"[green]Đã tự động phê duyệt {approved} trường có độ tin cậy CAO.[/green]")

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

                approve = Confirm.ask("    Phê duyệt trường này?", default=(level == ConfidenceLevel.HIGH))
                mapping.approved = approve

        # Step 4: Fill
        approved_count = sum(1 for m in mappings if m.approved)
        if approved_count == 0:
            console.print("[yellow]Không có trường nào được phê duyệt. Hủy thao tác điền.[/yellow]")
            await orchestrator.close()
            return

        console.print()
        if not Confirm.ask(f"[bold]Bắt đầu tự động điền {approved_count} trường đã chọn?[/bold]", default=True):
            console.print("[dim]Đã hủy thao tác điền.[/dim]")
            await orchestrator.close()
            return

        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
        ) as progress:
            task = progress.add_task("Đang tự động điền dữ liệu vào Form...", total=None)
            fill_result = await orchestrator.fill_form(mappings)
            progress.update(task, description="✅ Đã điền xong biểu mẫu!")

        console.print()
        display_fill_result(fill_result)

        # Step 5: Submit?
        if Confirm.ask("[bold yellow]Bạn có muốn thực hiện NỘP FORM (Submit) không?[/bold yellow]", default=False):
            submit_result = await orchestrator.submit_form(confirmed=True)
            if submit_result.success:
                console.print("[bold green]✅ Đã Nộp Form thành công![/bold green]")
            elif submit_result.needs_human_action:
                console.print(f"[bold yellow]⚠️  {submit_result.reason}[/bold yellow]")
            else:
                console.print(f"[bold red]❌ Nộp Form thất bại: {submit_result.reason}[/bold red]")
        else:
            console.print("[dim]Không nộp Form. Trình duyệt được giữ nguyên để bạn kiểm tra thủ công.[/dim]")
            Prompt.ask("[dim]Nhấn Enter để đóng trình duyệt[/dim]")

        await orchestrator.close()

    except Exception as e:
        console.print(f"[bold red]Lỗi hệ thống: {e}[/bold red]")
        await orchestrator.close()


async def _handle_profile(config: Config) -> None:
    """Handle profile management."""
    from autoform.profile.manager import ProfileManager
    from autoform.profile.storage import ProfileStorage

    storage = ProfileStorage(config.profile_dir)
    manager = ProfileManager(storage)

    console.print()
    console.print("[bold]Quản Lý Hồ Sơ Người Dùng (Profile Management)[/bold]")
    console.print("  [cyan]1[/cyan] - Xem thông tin profile hiện tại")
    console.print("  [cyan]2[/cyan] - Tạo profile mới")
    console.print("  [cyan]3[/cyan] - Chỉnh sửa trường trong profile")
    console.print("  [cyan]4[/cyan] - Danh sách tất cả các profile")
    console.print("  [cyan]0[/cyan] - Quay lại Menu chính")
    console.print()

    choice = Prompt.ask("Lựa chọn của bạn", choices=["0", "1", "2", "3", "4"], default="1")

    if choice == "0":
        return

    if choice == "1":
        # View profile
        profile_name = config.get("profile", "default_profile", "default")
        if not manager.profile_exists(profile_name):
            console.print(f"[yellow]Không tìm thấy Profile '{profile_name}'.[/yellow]")
            return

        profile = manager.get_profile(profile_name)
        all_fields = profile.get_all_fields()

        from rich.table import Table

        table = Table(title=f"Hồ Sơ: {profile_name}", show_lines=True, border_style="dim")
        table.add_column("Đường dẫn Trường", style="cyan")
        table.add_column("Giá trị Dữ liệu", style="white")

        for path, value in sorted(all_fields.items()):
            display_value = str(value) if value else "[dim]—[/dim]"
            table.add_row(path, display_value)

        console.print(table)

    elif choice == "2":
        # Interactive profile creation
        from autoform.profile.manager import PROFILE_SCHEMA

        console.print("[bold]Tạo Hồ Sơ Mới (Create New Profile)[/bold]")
        console.print("[dim]Nhấn Enter để bỏ qua các trường không bắt buộc.[/dim]\n")

        profile_name = Prompt.ask("Tên Profile mới", default="default")
        data: dict[str, dict[str, Any]] = {}

        for category, fields in PROFILE_SCHEMA.items():
            console.print(f"\n[bold cyan]— Danh mục: {category.title()} —[/bold cyan]")
            data[category] = {}

            for field_name, description in fields.items():
                value = Prompt.ask(f"  {description}", default="")
                if value:
                    if "comma-separated" in description.lower():
                        value = [v.strip() for v in value.split(",")]
                    data[category][field_name] = value

        profile = manager.create_profile(data, profile_name)
        console.print(f"\n[green]✅ Đã tạo thành công Profile '{profile_name}'![/green]")
        summary = manager.get_profile_summary(profile_name)
        total = sum(summary.values())
        console.print(f"[dim]Tổng số trường đã nhập: {total}[/dim]")

    elif choice == "3":
        # Edit field
        profile_name = Prompt.ask("Tên Profile cần sửa", default="default")
        if not manager.profile_exists(profile_name):
            console.print(f"[red]Không tìm thấy Profile '{profile_name}'.[/red]")
            return

        field_path = Prompt.ask("Đường dẫn trường (ví dụ: personal.full_name)")
        value = Prompt.ask("Giá trị mới")

        manager.update_field(profile_name, field_path, value)
        console.print(f"[green]✅ Đã cập nhật thành công {field_path}[/green]")

    elif choice == "4":
        # List profiles
        profiles = manager.list_profiles()
        if not profiles:
            console.print("[yellow]Chưa có Profile nào trong hệ thống.[/yellow]")
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
            console.print("[bold]Cú pháp sử dụng:[/bold]  autoform [command]")
            console.print()
            console.print("[bold]Danh sách câu lệnh:[/bold]")
            console.print("  (interactive)   Khởi chạy Menu tương tác")
            console.print("  --version, -v   Hiển thị phiên bản")
            console.print("  --help, -h      Hiển thị trợ giúp")
            console.print()
            return

    # Interactive mode
    _print_banner()
    console.print("[dim]Nhập số để lựa chọn chức năng, hoặc 0 để thoát chương trình.[/dim]")
    console.print()
    _print_menu()

    while True:
        try:
            choice = console.input("[bold blue]>[/bold blue] ").strip()

            if choice == "0":
                console.print("[dim]Cảm ơn bạn đã sử dụng AutoForm! Tạm biệt! 👋[/dim]")
                break
            elif choice == "1":
                asyncio.run(_handle_fill_form(config))
            elif choice == "2":
                asyncio.run(_handle_profile(config))
            elif choice == "3":
                console.print("[yellow]Chức năng chỉnh sửa cài đặt đang được phát triển...[/yellow]")
            else:
                console.print("[red]Lựa chọn không hợp lệ. Vui lòng thử lại.[/red]")

            console.print()
            _print_menu()

        except (KeyboardInterrupt, EOFError):
            console.print("\n[dim]Tạm biệt! 👋[/dim]")
            break


if __name__ == "__main__":
    main()
