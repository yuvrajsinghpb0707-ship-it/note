import json
import os
import uuid

from pathlib import Path
from datetime import datetime


class LocalStorage:

    def __init__(self, filename="notes.json", tasks_filename=None):

        self.filename = Path(filename).resolve()

        if tasks_filename:
            self.tasks_filename = Path(tasks_filename).resolve()
        else:
            self.tasks_filename = self.filename.with_name("tasks.json")

        self.filename.parent.mkdir(parents=True, exist_ok=True)
        self.tasks_filename.parent.mkdir(parents=True, exist_ok=True)

    def _now(self):
        return datetime.now().strftime("%d %b %Y, %I:%M %p")

    # =====================================
    # GENERAL JSON STORAGE
    # =====================================

    def _load_data(self, path):

        if not path.exists():
            return []

        try:
            with path.open("r", encoding="utf-8") as file:
                data = json.load(file)

            if not isinstance(data, list):
                raise ValueError(f"Invalid database format: {path.name}")

            return data

        except (json.JSONDecodeError, OSError, ValueError) as error:
            raise RuntimeError(
                f"Unable to read {path.name}: {error}"
            )

    def _save_data(self, path, data):

        path.parent.mkdir(parents=True, exist_ok=True)

        temporary_file = path.with_suffix(path.suffix + ".tmp")

        try:
            with temporary_file.open("w", encoding="utf-8") as file:
                json.dump(
                    data,
                    file,
                    indent=4,
                    ensure_ascii=False
                )
                file.flush()
                os.fsync(file.fileno())

            os.replace(temporary_file, path)

        except OSError as error:

            if temporary_file.exists():
                try:
                    temporary_file.unlink()
                except OSError:
                    pass

            raise RuntimeError(
                f"Unable to save {path.name}: {error}"
            )

    # =====================================
    # NOTES
    # =====================================

    def load_notes(self):
        return self._load_data(self.filename)

    def save_notes(self, notes):
        self._save_data(self.filename, notes)

    def create_note(self, title, content):

        notes = self.load_notes()
        now = self._now()

        note = {
            "id": str(uuid.uuid4()),
            "title": title,
            "content": content,
            "created_at": now,
            "updated_at": now
        }

        notes.insert(0, note)
        self.save_notes(notes)

        return note

    def update_note(self, note_id, title, content):

        notes = self.load_notes()

        for note in notes:
            if note["id"] == note_id:

                note["title"] = title
                note["content"] = content
                note["updated_at"] = self._now()

                self.save_notes(notes)
                return note

        raise ValueError("Note not found.")

    def delete_note(self, note_id):

        notes = self.load_notes()

        updated = [
            note for note in notes
            if note["id"] != note_id
        ]

        if len(updated) == len(notes):
            raise ValueError("Note not found.")

        self.save_notes(updated)
        return True

    # =====================================
    # TASKS - PERMANENT LOCAL STORAGE
    # =====================================

    def load_tasks(self):
        return self._load_data(self.tasks_filename)

    def save_tasks(self, tasks):
        self._save_data(self.tasks_filename, tasks)

    def create_task(self, title, description="", due_date=""):

        tasks = self.load_tasks()
        now = self._now()

        task = {
            "id": str(uuid.uuid4()),
            "title": title,
            "description": description,
            "due_date": due_date,
            "completed": False,
            "created_at": now,
            "updated_at": now
        }

        tasks.insert(0, task)

        # Save immediately to tasks.json
        self.save_tasks(tasks)

        return task

    def update_task(
        self,
        task_id,
        title,
        description="",
        due_date=""
    ):

        tasks = self.load_tasks()

        for task in tasks:
            if task["id"] == task_id:

                task["title"] = title
                task["description"] = description
                task["due_date"] = due_date
                task["updated_at"] = self._now()

                # Save immediately after editing
                self.save_tasks(tasks)

                return task

        raise ValueError("Task not found.")

    def set_task_completed(self, task_id, completed):

        tasks = self.load_tasks()

        for task in tasks:
            if task["id"] == task_id:

                task["completed"] = bool(completed)
                task["updated_at"] = self._now()

                # Save completion status immediately
                self.save_tasks(tasks)

                return task

        raise ValueError("Task not found.")

    def delete_task(self, task_id):

        tasks = self.load_tasks()

        updated = [
            task for task in tasks
            if task["id"] != task_id
        ]

        if len(updated) == len(tasks):
            raise ValueError("Task not found.")

        # Permanently remove task from saved JSON database
        self.save_tasks(updated)

        return True