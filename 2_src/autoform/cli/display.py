"""CLI display utilities for rich terminal output in Vietnamese."""

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
    info.append("Tiêu đề: ", style="bold")
    info.append(f"{schema.title or 'Không có tiêu đề'}\n")
    info.append("Địa chỉ URL: ", style="bold")
    info.append(f"{schema.url}\n", style="dim")
    info.append("Nền tảng: ", style="bold")
    info.append(f"{schema.platform.value}\n")
    info.append("Số trường dữ liệu: ", style="bold")
    info.append(f"{schema.field_count}\n")

    if schema.has_captcha:
        info.append("⚠️  CẢNH BÁO: Phát hiện CAPTCHA trên Form\n", style="bold yellow")

    console.print(Panel(info, title="📋 Phân Tích Biểu Mẫu", border_style="blue"))
    console.print()


def display_mapping_table(mappings: list[FieldMapping]) -> None:
    """Display mapping results in a color-coded table."""
    table = Table(
        title="🔗 Kết Quả Ánh Xạ Trường Dữ Liệu",
        show_lines=True,
        border_style="dim",
    )

    table.add_column("STT", style="dim", width=4, justify="right")
    table.add_column("Trường trên Form", style="white", min_width=20)
    table.add_column("Loại trường", style="cyan", width=12)
    table.add_column("Đường dẫn Profile", min_width=22)
    table.add_column("Độ tin cậy", width=12, justify="center")
    table.add_column("Trạng thái", width=12, justify="center")

    for i, mapping in enumerate(mappings, 1):
        level = mapping.confidence_level
        confidence_text = f"{mapping.confidence:.0%}" if mapping.confidence > 0 else "—"

        # Color based on confidence
        if level == ConfidenceLevel.HIGH:
            conf_style = "bold green"
            status = "✓ TỰ ĐỘNG"
            path_style = "green"
        elif level == ConfidenceLevel.MEDIUM:
            conf_style = "bold yellow"
            status = "⚠ KIỂM TRA"
            path_style = "yellow"
        elif level == ConfidenceLevel.LOW:
            conf_style = "red"
            status = "❓ THẤP"
            path_style = "red"
        else:
            conf_style = "dim"
            status = "✗ KHÔNG KHỚP"
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
        f"  [green]✓ Cao (High): {high}[/green]  "
        f"[yellow]⚠ Trung bình (Medium): {medium}[/yellow]  "
        f"[red]❓ Thấp (Low): {low}[/red]  "
        f"[dim]✗ Không khớp: {no_match}[/dim]  "
        f"[bold]Tổng cộng: {total}[/bold]"
    )
    console.print(summary)
    console.print()


def display_fill_result(result: FillResult) -> None:
    """Display fill results."""
    table = Table(
        title="📝 Kết Quả Thực Thi Điền Form",
        show_lines=True,
        border_style="dim",
    )

    table.add_column("Trường dữ liệu", style="white", min_width=20)
    table.add_column("Trạng thái", width=14, justify="center")
    table.add_column("Chi tiết", style="dim")

    for fr in result.field_results:
        if fr.status == FillStatus.FILLED:
            status_text = Text("✓ Đã điền", style="green")
        elif fr.status == FillStatus.SKIPPED:
            status_text = Text("— Bỏ qua", style="dim")
        elif fr.status == FillStatus.FAILED:
            status_text = Text("✗ Thất bại", style="red")
        elif fr.status == FillStatus.BLOCKED:
            status_text = Text("🚫 Bị chặn", style="yellow")
        else:
            status_text = Text("⚠ Lỗi", style="red")

        table.add_row(
            fr.field.label,
            status_text,
            fr.reason or "",
        )

    console.print(table)
    console.print()

    # Summary
    console.print(
        f"  [green]Đã điền thành công: {result.filled_count}[/green]  "
        f"[dim]Bỏ qua: {result.skipped_count}[/dim]  "
        f"[red]Thất bại: {result.failed_count}[/red]  "
        f"Tỷ lệ thành công: [bold]{result.success_rate:.0%}[/bold]  "
        f"Thời gian: {result.processing_time_ms:.0f}ms"
    )
    console.print()
