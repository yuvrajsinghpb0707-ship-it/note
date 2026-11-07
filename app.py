
import json
import os
import re
import uuid

from io import BytesIO
from pathlib import Path
from datetime import datetime

from flask import (
    Flask,
    render_template,
    request,
    redirect,
    url_for,
    flash,
    send_file,
    abort
)
from jinja2 import DictLoader
from werkzeug.utils import secure_filename


# =========================================================
# APPLICATION CONFIGURATION
# =========================================================

BASE_DIR = Path(__file__).resolve().parent

NOTES_FILE = BASE_DIR / "notes.json"
TASKS_FILE = BASE_DIR / "tasks.json"

app = Flask(__name__)

app.secret_key = os.environ.get(
    "CLOUDNOTE_SECRET_KEY",
    "change-this-secret-before-public-deployment"
)


# =========================================================
# JSON STORAGE
# =========================================================

def load_json(path):

    if not path.exists():
        return []

    try:
        with open(path, "r", encoding="utf-8") as file:
            data = json.load(file)

        return data if isinstance(data, list) else []

    except (json.JSONDecodeError, OSError):
        return []


def save_json(path, data):

    temporary_file = path.with_suffix(
        path.suffix + ".tmp"
    )

    with open(
        temporary_file,
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            data,
            file,
            indent=4,
            ensure_ascii=False
        )

        file.flush()
        os.fsync(file.fileno())

    os.replace(temporary_file, path)


def get_notes():
    return load_json(NOTES_FILE)


def get_tasks():
    return load_json(TASKS_FILE)


def timestamp():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def find_note(note_id):

    for note in get_notes():

        if note.get("id") == note_id:
            return note

    return None


def find_task(task_id):

    for task in get_tasks():

        if task.get("id") == task_id:
            return task

    return None


def clean_filename(value):

    value = secure_filename(value)

    return value or "CloudNote"


# =========================================================
# HTML TEMPLATES
# =========================================================

BASE_TEMPLATE = r"""
<!DOCTYPE html>
<html lang="en">

<head>

    <meta charset="UTF-8">

    <meta
        name="viewport"
        content="width=device-width, initial-scale=1.0"
    >

    <meta
        name="theme-color"
        content="#7667e8"
    >

    <title>{{ title }} | CloudNote</title>

    <style>

        :root {
            --background: #f5f7fc;
            --sidebar: #ffffff;
            --card: #ffffff;
            --card-light: #f1f3fa;
            --primary: #7667e8;
            --primary-hover: #6252d5;
            --secondary: #edeaff;
            --text: #25243a;
            --muted: #85869a;
            --border: #e9eaf1;
            --success: #269b70;
            --danger: #e45c69;
            --danger-bg: #fff0f1;
            --shadow: 0 8px 30px rgba(30, 30, 70, 0.05);
        }

        [data-theme="dark"] {
            --background: #151521;
            --sidebar: #1d1d2b;
            --card: #242437;
            --card-light: #303047;
            --primary: #9588ff;
            --primary-hover: #8172f2;
            --secondary: #37334f;
            --text: #f2f1fa;
            --muted: #a4a2b8;
            --border: #38384d;
            --success: #53c99a;
            --danger: #ff7181;
            --danger-bg: #492a35;
            --shadow: 0 8px 30px rgba(0, 0, 0, 0.15);
        }

        * {
            box-sizing: border-box;
        }

        body {
            margin: 0;
            background: var(--background);
            color: var(--text);
            font-family: Arial, Helvetica, sans-serif;
            transition: background 0.2s, color 0.2s;
        }

        a {
            color: inherit;
            text-decoration: none;
        }

        button,
        input,
        textarea {
            font: inherit;
        }

        .topbar {
            min-height: 72px;
            background: var(--sidebar);
            border-bottom: 1px solid var(--border);
            display: flex;
            align-items: center;
            justify-content: space-between;
            gap: 18px;
            padding: 12px 5%;
            position: sticky;
            top: 0;
            z-index: 10;
        }

        .brand {
            font-size: 23px;
            font-weight: 800;
            color: var(--primary);
            letter-spacing: -1px;
        }

        .brand small {
            display: block;
            color: var(--muted);
            font-size: 9px;
            letter-spacing: 2px;
            margin-top: 3px;
        }

        .nav {
            display: flex;
            align-items: center;
            gap: 8px;
            flex-wrap: wrap;
        }

        .nav a,
        .theme-button {
            padding: 10px 14px;
            border-radius: 10px;
            color: var(--muted);
            font-size: 13px;
            font-weight: 600;
        }

        .nav a:hover,
        .nav a.active {
            background: var(--secondary);
            color: var(--primary);
        }

        .theme-button {
            border: 1px solid var(--border);
            background: var(--card);
            cursor: pointer;
        }

        .container {
            width: min(1100px, 92%);
            margin: 32px auto;
        }

        .page-heading {
            display: flex;
            align-items: center;
            justify-content: space-between;
            flex-wrap: wrap;
            gap: 16px;
            margin-bottom: 24px;
        }

        h1 {
            font-size: clamp(25px, 4vw, 32px);
            margin: 0;
        }

        h2 {
            font-size: 19px;
        }

        .muted {
            color: var(--muted);
        }

        .small {
            font-size: 12px;
        }

        .button {
            display: inline-flex;
            align-items: center;
            justify-content: center;
            gap: 7px;
            padding: 11px 17px;
            border: 0;
            border-radius: 10px;
            background: var(--primary);
            color: white;
            cursor: pointer;
            font-weight: 700;
            font-size: 13px;
            text-align: center;
        }

        .button:hover {
            background: var(--primary-hover);
        }

        .button.secondary {
            background: var(--secondary);
            color: var(--primary);
        }

        .button.danger {
            background: var(--danger-bg);
            color: var(--danger);
        }

        .button.success {
            background: var(--success);
            color: white;
        }

        .button.outline {
            background: var(--card);
            border: 1px solid var(--border);
            color: var(--text);
        }

        .stats {
            display: grid;
            grid-template-columns: repeat(3, 1fr);
            gap: 16px;
            margin-bottom: 25px;
        }

        .stat-card,
        .card {
            background: var(--card);
            border: 1px solid var(--border);
            border-radius: 16px;
            box-shadow: var(--shadow);
        }

        .stat-card {
            padding: 22px;
        }

        .stat-card strong {
            display: block;
            font-size: 30px;
            margin-top: 9px;
        }

        .stat-label {
            color: var(--muted);
            font-size: 13px;
        }

        .card {
            padding: 20px;
            margin-bottom: 14px;
        }

        .card h3 {
            margin: 0 0 10px;
            font-size: 17px;
        }

        .card p {
            line-height: 1.6;
            overflow-wrap: anywhere;
        }

        .card-actions {
            display: flex;
            flex-wrap: wrap;
            gap: 8px;
            margin-top: 16px;
        }

        .search-form {
            display: flex;
            gap: 10px;
            margin-bottom: 18px;
        }

        .field {
            width: 100%;
            padding: 13px 14px;
            border-radius: 10px;
            border: 1px solid var(--border);
            outline: none;
            background: var(--card);
            color: var(--text);
        }

        .field:focus {
            border-color: var(--primary);
            box-shadow: 0 0 0 3px rgba(118, 103, 232, 0.12);
        }

        textarea.field {
            min-height: 260px;
            resize: vertical;
            line-height: 1.6;
        }

        label {
            display: block;
            margin: 17px 0 8px;
            font-size: 12px;
            font-weight: 800;
            color: var(--muted);
            letter-spacing: 0.6px;
        }

        .form-card {
            max-width: 850px;
            margin: auto;
        }

        .form-actions {
            display: flex;
            flex-wrap: wrap;
            justify-content: space-between;
            gap: 10px;
            margin-top: 20px;
        }

        .filters {
            display: flex;
            gap: 8px;
            flex-wrap: wrap;
            margin: 15px 0;
        }

        .filter {
            border: 1px solid var(--border);
            background: var(--card);
            color: var(--muted);
            padding: 9px 14px;
            border-radius: 20px;
            font-size: 12px;
            font-weight: 700;
        }

        .filter.active {
            color: var(--primary);
            background: var(--secondary);
            border-color: transparent;
        }

        .task-row {
            display: flex;
            align-items: flex-start;
            gap: 13px;
        }

        .task-check {
            width: 21px;
            height: 21px;
            accent-color: var(--primary);
            cursor: pointer;
            margin-top: 3px;
        }

        .task-main {
            flex: 1;
            min-width: 0;
        }

        .completed-title {
            text-decoration: line-through;
            color: var(--muted);
        }

        .due-date {
            display: inline-block;
            padding: 6px 9px;
            border-radius: 8px;
            background: var(--card-light);
            color: var(--muted);
            font-size: 11px;
            margin-top: 7px;
        }

        .flash {
            padding: 13px 16px;
            border-radius: 10px;
            margin-bottom: 15px;
            background: var(--secondary);
            color: var(--primary);
            font-size: 13px;
        }

        .flash.error {
            background: var(--danger-bg);
            color: var(--danger);
        }

        .empty {
            padding: 50px 20px;
            text-align: center;
            color: var(--muted);
        }

        .footer {
            text-align: center;
            color: var(--muted);
            font-size: 11px;
            padding: 30px 10px;
        }

        @media (max-width: 700px) {

            .topbar {
                align-items: flex-start;
                flex-direction: column;
                padding: 15px 4%;
            }

            .nav {
                width: 100%;
                display: grid;
                grid-template-columns: repeat(3, 1fr);
            }

            .nav a,
            .theme-button {
                text-align: center;
                padding: 10px 5px;
                font-size: 12px;
            }

            .container {
                width: 92%;
                margin: 23px auto;
            }

            .stats {
                grid-template-columns: 1fr;
                gap: 10px;
            }

            .stat-card {
                padding: 17px;
            }

            .stat-card strong {
                font-size: 25px;
            }

            .search-form {
                flex-direction: column;
            }

            .search-form .button {
                width: 100%;
            }

            .card {
                padding: 16px;
            }

            .form-actions {
                flex-direction: column;
            }

            .form-actions .button {
                width: 100%;
            }

            .page-heading .button {
                width: 100%;
            }

        }

    </style>

</head>

<body>

    <header class="topbar">

        <a href="{{ url_for('dashboard') }}" class="brand">
            CloudNote
            <small>YOUR PERSONAL WORKSPACE</small>
        </a>

        <nav class="nav">

            <a
                href="{{ url_for('dashboard') }}"
                class="{% if active == 'dashboard' %}active{% endif %}"
            >
                Dashboard
            </a>

            <a
                href="{{ url_for('notes') }}"
                class="{% if active == 'notes' %}active{% endif %}"
            >
                My Notes
            </a>

            <a
                href="{{ url_for('new_note') }}"
                class="{% if active == 'new_note' %}active{% endif %}"
            >
                + Note
            </a>

            <a
                href="{{ url_for('tasks') }}"
                class="{% if active == 'tasks' %}active{% endif %}"
            >
                Tasks
            </a>

            <button
                class="theme-button"
                type="button"
                onclick="toggleTheme()"
            >
                ☾ Theme
            </button>

        </nav>

    </header>

    <main class="container">

        {% with messages = get_flashed_messages(with_categories=true) %}

            {% for category, message in messages %}

                <div class="flash {{ category }}">
                    {{ message }}
                </div>

            {% endfor %}

        {% endwith %}

        {% block content %}{% endblock %}

    </main>

    <footer class="footer">
        CLOUDNOTE · PERSONAL PRODUCTIVITY WORKSPACE
    </footer>

    <script>

        function applyTheme(theme) {

            document.documentElement.setAttribute(
                "data-theme",
                theme
            );

            localStorage.setItem("cloudnote-theme", theme);
        }

        function toggleTheme() {

            const current =
                document.documentElement.getAttribute("data-theme");

            applyTheme(
                current === "dark" ? "light" : "dark"
            );
        }

        applyTheme(
            localStorage.getItem("cloudnote-theme") || "light"
        );

        function downloadEditorNote() {

            const title =
                document.getElementById("note-title").value.trim()
                || "CloudNote";

            const content =
                document.getElementById("note-content").value;

            if (!content.trim()) {
                alert("Write something before downloading.");
                return;
            }

            const text =
                title + "\n" +
                "=".repeat(title.length) +
                "\n\n" + content;

            const blob = new Blob(
                [text],
                { type: "text/plain;charset=utf-8" }
            );

            const link = document.createElement("a");

            link.href = URL.createObjectURL(blob);
            link.download = title.replace(
                /[\\/:*?"<>|]/g,
                ""
            ) + ".txt";

            link.click();

            URL.revokeObjectURL(link.href);
        }

    </script>

</body>
</html>
"""


DASHBOARD_TEMPLATE = r"""
{% extends "base.html" %}

{% block content %}

<div class="page-heading">

    <div>
        <h1>Welcome to CloudNote</h1>
        <p class="muted">Your notes and daily tasks, all in one place.</p>
    </div>

    <a class="button" href="{{ url_for('new_note') }}">
        + Create Note
    </a>

</div>

<section class="stats">

    <div class="stat-card">
        <span class="stat-label">Total Notes</span>
        <strong>{{ note_count }}</strong>
    </div>

    <div class="stat-card">
        <span class="stat-label">Total Tasks</span>
        <strong>{{ task_count }}</strong>
    </div>

    <div class="stat-card">
        <span class="stat-label">Completed Tasks</span>
        <strong>{{ completed_count }}</strong>
    </div>

</section>

<div class="page-heading">
    <h2>Recent Notes</h2>
    <a class="button secondary" href="{{ url_for('notes') }}">
        View All Notes
    </a>
</div>

{% if recent_notes %}

    {% for note in recent_notes %}

        <article class="card">

            <h3>{{ note.get("title", "Untitled") }}</h3>

            <p class="muted">
                {{ note.get("content", "")[:180] }}
                {% if note.get("content", "")|length > 180 %}...{% endif %}
            </p>

            <div class="card-actions">

                <a
                    class="button secondary"
                    href="{{ url_for('edit_note', note_id=note['id']) }}"
                >
                    Open Note
                </a>

                <a
                    class="button outline"
                    href="{{ url_for('download_note', note_id=note['id']) }}"
                >
                    Download
                </a>

            </div>

        </article>

    {% endfor %}

{% else %}

    <div class="card empty">
        <h3>No notes yet</h3>
        <p>Create your first note to get started.</p>
        <a class="button" href="{{ url_for('new_note') }}">
            Create First Note
        </a>
    </div>

{% endif %}

<div class="page-heading" style="margin-top:30px;">
    <h2>Tasks Overview</h2>
    <a class="button secondary" href="{{ url_for('tasks') }}">
        View Tasks
    </a>
</div>

<div class="card">
    <p>
        You have <strong>{{ pending_count }}</strong>
        pending tasks.
    </p>
</div>

{% endblock %}
"""


NOTES_TEMPLATE = r"""
{% extends "base.html" %}

{% block content %}

<div class="page-heading">

    <div>
        <h1>My Notes</h1>
        <p class="muted">Manage and download your saved notes.</p>
    </div>

    <a class="button" href="{{ url_for('new_note') }}">
        + Create Note
    </a>

</div>

<form class="search-form" method="get">

    <input
        class="field"
        type="search"
        name="q"
        placeholder="Search your notes..."
        value="{{ query }}"
    >

    <button class="button" type="submit">
        Search
    </button>

</form>

<p class="muted small">
    {{ notes_list|length }} NOTES FOUND
</p>

{% if notes_list %}

    {% for note in notes_list %}

        <article class="card">

            <h3>{{ note.get("title", "Untitled") }}</h3>

            <p class="muted">
                {{ note.get("content", "")[:220] }}
                {% if note.get("content", "")|length > 220 %}...{% endif %}
            </p>

            <span class="small muted">
                Updated: {{ note.get("updated_at", "") }}
            </span>

            <div class="card-actions">

                <a
                    class="button secondary"
                    href="{{ url_for('edit_note', note_id=note['id']) }}"
                >
                    Edit
                </a>

                <a
                    class="button outline"
                    href="{{ url_for('download_note', note_id=note['id']) }}"
                >
                    ↓ Download
                </a>

                <form
                    method="post"
                    action="{{ url_for('delete_note', note_id=note['id']) }}"
                    onsubmit="return confirm('Delete this note permanently?')"
                >

                    <button class="button danger" type="submit">
                        Delete
                    </button>

                </form>

            </div>

        </article>

    {% endfor %}

{% else %}

    <div class="card empty">
        <h3>No notes found</h3>
        <p>Try another search or create a new note.</p>
    </div>

{% endif %}

{% endblock %}
"""


NOTE_FORM_TEMPLATE = r"""
{% extends "base.html" %}

{% block content %}

<div class="card form-card">

    <h1>{{ heading }}</h1>

    <p class="muted">
        Write down your ideas and thoughts.
    </p>

    <form method="post">

        <label for="note-title">NOTE TITLE</label>

        <input
            class="field"
            id="note-title"
            name="title"
            maxlength="200"
            required
            value="{{ note.get('title', '') if note else '' }}"
            placeholder="Enter note title..."
        >

        <label for="note-content">YOUR CONTENT</label>

        <textarea
            class="field"
            id="note-content"
            name="content"
            required
            placeholder="Start writing..."
        >{{ note.get('content', '') if note else '' }}</textarea>

        <div class="form-actions">

            <a class="button outline" href="{{ url_for('notes') }}">
                Cancel
            </a>

            <button
                class="button secondary"
                type="button"
                onclick="downloadEditorNote()"
            >
                ↓ Download
            </button>

            <button class="button" type="submit">
                Save Note
            </button>

        </div>

    </form>

</div>

{% endblock %}
"""


TASKS_TEMPLATE = r"""
{% extends "base.html" %}

{% block content %}

<div class="page-heading">

    <div>
        <h1>My Tasks ✓</h1>
        <p class="muted">Organise your work and complete your goals.</p>
    </div>

    <a class="button" href="{{ url_for('new_task') }}">
        + Add Task
    </a>

</div>

<section class="stats">

    <div class="stat-card">
        <span class="stat-label">All Tasks</span>
        <strong>{{ total }}</strong>
    </div>

    <div class="stat-card">
        <span class="stat-label">Pending</span>
        <strong>{{ pending }}</strong>
    </div>

    <div class="stat-card">
        <span class="stat-label">Completed</span>
        <strong>{{ completed }}</strong>
    </div>

</section>

<form class="search-form" method="get">

    <input
        class="field"
        type="search"
        name="q"
        value="{{ query }}"
        placeholder="Search tasks..."
    >

    <input type="hidden" name="filter" value="{{ filter_mode }}">

    <button class="button" type="submit">
        Search
    </button>

</form>

<div class="filters">

    <a
        class="filter {% if filter_mode == 'all' %}active{% endif %}"
        href="{{ url_for('tasks', filter='all', q=query) }}"
    >
        All
    </a>

    <a
        class="filter {% if filter_mode == 'pending' %}active{% endif %}"
        href="{{ url_for('tasks', filter='pending', q=query) }}"
    >
        Pending
    </a>

    <a
        class="filter {% if filter_mode == 'completed' %}active{% endif %}"
        href="{{ url_for('tasks', filter='completed', q=query) }}"
    >
        Completed
    </a>

</div>

<p class="muted small">
    {{ task_list|length }} TASKS FOUND
</p>

{% if task_list %}

    {% for task in task_list %}

        <article class="card">

            <div class="task-row">

                <form
                    method="post"
                    action="{{ url_for('toggle_task', task_id=task['id']) }}"
                >

                    <input
                        class="task-check"
                        type="checkbox"
                        {% if task.get('completed') %}checked{% endif %}
                        onchange="this.form.submit()"
                        aria-label="Toggle task completion"
                    >

                </form>

                <div class="task-main">

                    <h3 class="{% if task.get('completed') %}completed-title{% endif %}">
                        {{ task.get("title", "Untitled Task") }}
                    </h3>

                    {% if task.get("description") %}

                        <p class="muted">
                            {{ task.get("description") }}
                        </p>

                    {% endif %}

                    {% if task.get("due_date") %}

                        <span class="due-date">
                            Due: {{ task.get("due_date") }}
                        </span>

                    {% endif %}

                    <div class="card-actions">

                        <a
                            class="button secondary"
                            href="{{ url_for('edit_task', task_id=task['id']) }}"
                        >
                            Edit
                        </a>

                        <form
                            method="post"
                            action="{{ url_for('delete_task', task_id=task['id']) }}"
                            onsubmit="return confirm('Delete this task permanently?')"
                        >

                            <button class="button danger" type="submit">
                                Delete
                            </button>

                        </form>

                    </div>

                </div>

            </div>

        </article>

    {% endfor %}

{% else %}

    <div class="card empty">
        <h3>No tasks found</h3>
        <p>Add a task or change the selected filter.</p>
    </div>

{% endif %}

{% endblock %}
"""


TASK_FORM_TEMPLATE = r"""
{% extends "base.html" %}

{% block content %}

<div class="card form-card">

    <h1>{{ heading }}</h1>

    <p class="muted">Organise your next activity.</p>

    <form method="post">

        <label for="task-title">TASK TITLE</label>

        <input
            class="field"
            id="task-title"
            name="title"
            maxlength="200"
            required
            value="{{ task.get('title', '') if task else '' }}"
            placeholder="Enter task title..."
        >

        <label for="task-description">DESCRIPTION</label>

        <textarea
            class="field"
            id="task-description"
            name="description"
            placeholder="Add task details..."
        >{{ task.get('description', '') if task else '' }}</textarea>

        <label for="task-date">DUE DATE (OPTIONAL)</label>

        <input
            class="field"
            id="task-date"
            type="date"
            name="due_date"
            value="{{ task.get('due_date', '') if task else '' }}"
        >

        <div class="form-actions">

            <a class="button outline" href="{{ url_for('tasks') }}">
                Cancel
            </a>

            <button class="button" type="submit">
                Save Task
            </button>

        </div>

    </form>

</div>

{% endblock %}
"""


# =========================================================
# REGISTER TEMPLATES
# =========================================================

app.jinja_loader = DictLoader({

    "base.html": BASE_TEMPLATE,
    "dashboard.html": DASHBOARD_TEMPLATE,
    "notes.html": NOTES_TEMPLATE,
    "note_form.html": NOTE_FORM_TEMPLATE,
    "tasks.html": TASKS_TEMPLATE,
    "task_form.html": TASK_FORM_TEMPLATE

})


# =========================================================
# DASHBOARD
# =========================================================

@app.get("/")
def dashboard():

    notes = get_notes()
    tasks_data = get_tasks()

    completed = sum(
        1 for task in tasks_data
        if task.get("completed", False)
    )

    pending = len(tasks_data) - completed

    recent_notes = sorted(
        notes,
        key=lambda item: item.get("updated_at", ""),
        reverse=True
    )[:5]

    return render_template(
        "dashboard.html",
        title="Dashboard",
        active="dashboard",
        note_count=len(notes),
        task_count=len(tasks_data),
        completed_count=completed,
        pending_count=pending,
        recent_notes=recent_notes
    )


# =========================================================
# NOTES LIST AND SEARCH
# =========================================================

@app.get("/notes")
def notes():

    query = request.args.get("q", "").strip().lower()

    all_notes = get_notes()

    filtered = [
        note for note in all_notes
        if query in note.get("title", "").lower()
        or query in note.get("content", "").lower()
    ]

    filtered.sort(
        key=lambda item: item.get("updated_at", ""),
        reverse=True
    )

    return render_template(
        "notes.html",
        title="My Notes",
        active="notes",
        notes_list=filtered,
        query=query
    )


# =========================================================
# CREATE NOTE
# =========================================================

@app.route("/notes/new", methods=["GET", "POST"])
def new_note():

    if request.method == "POST":

        title = request.form.get("title", "").strip()
        content = request.form.get("content", "").strip()

        if not title or not content:

            flash(
                "Please enter a title and note content.",
                "error"
            )

            return redirect(url_for("new_note"))

        notes_data = get_notes()

        new_item = {
            "id": str(uuid.uuid4()),
            "title": title,
            "content": content,
            "created_at": timestamp(),
            "updated_at": timestamp()
        }

        notes_data.insert(0, new_item)

        try:
            save_json(NOTES_FILE, notes_data)

            flash("Note saved successfully.")

            return redirect(url_for("notes"))

        except OSError as error:

            flash(f"Could not save note: {error}", "error")

    return render_template(
        "note_form.html",
        title="Create Note",
        active="new_note",
        heading="Create New Note",
        note=None
    )


# =========================================================
# EDIT NOTE
# =========================================================

@app.route("/notes/<note_id>/edit", methods=["GET", "POST"])
def edit_note(note_id):

    note = find_note(note_id)

    if not note:
        abort(404)

    if request.method == "POST":

        title = request.form.get("title", "").strip()
        content = request.form.get("content", "").strip()

        if not title or not content:

            flash(
                "Please enter a title and note content.",
                "error"
            )

            return redirect(
                url_for("edit_note", note_id=note_id)
            )

        notes_data = get_notes()

        for item in notes_data:

            if item.get("id") == note_id:

                item["title"] = title
                item["content"] = content
                item["updated_at"] = timestamp()

                break

        try:
            save_json(NOTES_FILE, notes_data)

            flash("Note updated successfully.")

            return redirect(url_for("notes"))

        except OSError as error:

            flash(f"Could not update note: {error}", "error")

    return render_template(
        "note_form.html",
        title="Edit Note",
        active="notes",
        heading="Edit Note",
        note=note
    )


# =========================================================
# DOWNLOAD NOTE
# =========================================================

@app.get("/notes/<note_id>/download")
def download_note(note_id):

    note = find_note(note_id)

    if not note:
        abort(404)

    title = note.get("title", "CloudNote")
    content = note.get("content", "")

    export_text = (
        title
        + "\n"
        + "=" * len(title)
        + "\n\n"
        + content
    )

    file_data = BytesIO(
        export_text.encode("utf-8")
    )

    filename = clean_filename(title) + ".txt"

    return send_file(
        file_data,
        mimetype="text/plain",
        as_attachment=True,
        download_name=filename
    )


# =========================================================
# DELETE NOTE
# =========================================================

@app.post("/notes/<note_id>/delete")
def delete_note(note_id):

    notes_data = get_notes()

    updated = [
        note for note in notes_data
        if note.get("id") != note_id
    ]

    if len(updated) == len(notes_data):

        flash("Note not found.", "error")

        return redirect(url_for("notes"))

    try:
        save_json(NOTES_FILE, updated)

        flash("Note deleted permanently.")

    except OSError as error:

        flash(f"Could not delete note: {error}", "error")

    return redirect(url_for("notes"))


# =========================================================
# TASK LIST, SEARCH AND FILTERS
# =========================================================

@app.get("/tasks")
def tasks():

    query = request.args.get("q", "").strip().lower()

    filter_mode = request.args.get(
        "filter",
        "all"
    ).lower()

    if filter_mode not in ("all", "pending", "completed"):
        filter_mode = "all"

    all_tasks = get_tasks()

    total = len(all_tasks)

    completed = sum(
        1 for task in all_tasks
        if task.get("completed", False)
    )

    pending = total - completed

    filtered = []

    for task in all_tasks:

        is_completed = task.get("completed", False)

        if filter_mode == "pending" and is_completed:
            continue

        if filter_mode == "completed" and not is_completed:
            continue

        searchable = (
            task.get("title", "").lower()
            + " "
            + task.get("description", "").lower()
        )

        if query and query not in searchable:
            continue

        filtered.append(task)

    filtered.sort(
        key=lambda item: (
            item.get("completed", False),
            item.get("created_at", "")
        )
    )

    return render_template(
        "tasks.html",
        title="My Tasks",
        active="tasks",
        task_list=filtered,
        total=total,
        completed=completed,
        pending=pending,
        query=query,
        filter_mode=filter_mode
    )


# =========================================================
# CREATE TASK
# =========================================================

@app.route("/tasks/new", methods=["GET", "POST"])
def new_task():

    if request.method == "POST":

        title = request.form.get("title", "").strip()

        description = request.form.get(
            "description",
            ""
        ).strip()

        due_date = request.form.get(
            "due_date",
            ""
        ).strip()

        if not title:

            flash("Please enter a task title.", "error")

            return redirect(url_for("new_task"))

        tasks_data = get_tasks()

        new_item = {
            "id": str(uuid.uuid4()),
            "title": title,
            "description": description,
            "due_date": due_date,
            "completed": False,
            "created_at": timestamp(),
            "updated_at": timestamp()
        }

        tasks_data.insert(0, new_item)

        try:
            save_json(TASKS_FILE, tasks_data)

            flash("Task created successfully.")

            return redirect(url_for("tasks"))

        except OSError as error:

            flash(f"Could not save task: {error}", "error")

    return render_template(
        "task_form.html",
        title="Add Task",
        active="tasks",
        heading="Create New Task",
        task=None
    )


# =========================================================
# EDIT TASK
# =========================================================

@app.route("/tasks/<task_id>/edit", methods=["GET", "POST"])
def edit_task(task_id):

    task = find_task(task_id)

    if not task:
        abort(404)

    if request.method == "POST":

        title = request.form.get("title", "").strip()

        description = request.form.get(
            "description",
            ""
        ).strip()

        due_date = request.form.get(
            "due_date",
            ""
        ).strip()

        if not title:

            flash("Please enter a task title.", "error")

            return redirect(
                url_for("edit_task", task_id=task_id)
            )

        tasks_data = get_tasks()

        for item in tasks_data:

            if item.get("id") == task_id:

                item["title"] = title
                item["description"] = description
                item["due_date"] = due_date
                item["updated_at"] = timestamp()

                break

        try:
            save_json(TASKS_FILE, tasks_data)

            flash("Task updated successfully.")

            return redirect(url_for("tasks"))

        except OSError as error:

            flash(f"Could not update task: {error}", "error")

    return render_template(
        "task_form.html",
        title="Edit Task",
        active="tasks",
        heading="Edit Task",
        task=task
    )


# =========================================================
# COMPLETE OR REOPEN TASK
# =========================================================

@app.post("/tasks/<task_id>/toggle")
def toggle_task(task_id):

    tasks_data = get_tasks()
    found = False

    for task in tasks_data:

        if task.get("id") == task_id:

            task["completed"] = not task.get(
                "completed",
                False
            )

            task["updated_at"] = timestamp()

            found = True
            break

    if not found:
        abort(404)

    try:
        save_json(TASKS_FILE, tasks_data)

    except OSError as error:

        flash(f"Could not update task: {error}", "error")

    return redirect(url_for("tasks"))


# =========================================================
# DELETE TASK
# =========================================================

@app.post("/tasks/<task_id>/delete")
def delete_task(task_id):

    tasks_data = get_tasks()

    updated = [
        task for task in tasks_data
        if task.get("id") != task_id
    ]

    if len(updated) == len(tasks_data):

        flash("Task not found.", "error")

        return redirect(url_for("tasks"))

    try:
        save_json(TASKS_FILE, updated)

        flash("Task deleted permanently.")

    except OSError as error:

        flash(f"Could not delete task: {error}", "error")

    return redirect(url_for("tasks"))


# =========================================================
# ERROR PAGES
# =========================================================

@app.errorhandler(404)
def not_found(error):

    return (
        "<h1>404 - Page Not Found</h1>"
        "<p>The requested CloudNote page or record does not exist.</p>"
        '<a href="/">Return to Dashboard</a>',
        404
    )


# =========================================================
# START SERVER
# =========================================================

if __name__ == "__main__":

    print("=" * 50)
    print("CLOUDNOTE WEB APPLICATION")
    print("=" * 50)

    print("Laptop: http://127.0.0.1:5000")
    print("Phone:  Use your laptop IPv4 address on the same Wi-Fi")
    print("=" * 50)

    app.run(
        host="0.0.0.0",
        port=5000,
        debug=False
    )
