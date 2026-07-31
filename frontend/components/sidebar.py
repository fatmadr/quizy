import base64
from pathlib import Path


def load_svg(icon_name: str, icons_dir: Path) -> str:
    icon_path = icons_dir / icon_name

    if not icon_path.exists():
        return ""

    return icon_path.read_text(encoding="utf-8")


def sidebar_item(
    label: str,
    icon_name: str,
    page_url: str,
    icons_dir: Path,
    active: bool = False,
) -> str:
    icon = load_svg(icon_name, icons_dir)
    active_class = " active" if active else ""

    return (
        f'<a href="{page_url}" '
        f'target="_self" '
        f'class="sidebar-btn{active_class}">'
        f'<span class="sidebar-icon">{icon}</span>'
        f'<span>{label}</span>'
        f'</a>'
    )


def build_teacher_sidebar(
    logo_path: Path,
    icons_dir: Path,
    teacher_name: str,
    active_page: str,
) -> str:
    logo_base64 = base64.b64encode(
        logo_path.read_bytes()
    ).decode("utf-8")

    return (
        f'<div class="sidebar-logo">'
        f'<img src="data:image/png;base64,{logo_base64}" '
        f'alt="Quizy logo" class="logo">'
        f'<div class="sidebar-brand-text">'
        f'<h1>Quizy</h1>'
        f'<p>Teach. Assess. Grow.</p>'
        f'</div>'
        f'</div>'

        f'{sidebar_item("Dashboard", "dashboard.svg", "/teacher_dashboard", icons_dir, active=(active_page == "dashboard"))}'
        f'{sidebar_item("Documents", "document.svg", "/documents", icons_dir, active=(active_page == "documents"))}'
        f'{sidebar_item("Quizzes", "quiz.svg", "/quizzes", icons_dir, active=(active_page == "quizzes"))}'
        f'{sidebar_item("Students", "student.svg", "/students", icons_dir, active=(active_page == "students"))}'
        f'{sidebar_item("Analytics", "analytics.svg", "/analytics", icons_dir, active=(active_page == "analytics"))}'
        f'{sidebar_item("Settings", "settings.svg", "/settings", icons_dir, active=(active_page == "settings"))}'

        f'<div class="profile-card">'
        f'<div class="profile-avatar">👤</div>'
        f'<div>'
        f'<b>{teacher_name}</b><br>'
        f'<small>Teacher</small>'
        f'</div>'
        f'</div>'

        f'<div class="sidebar-wave"></div>'
    )