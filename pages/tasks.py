
import tkinter as tk
from tkinter import messagebox

from config import FONT


class TasksPage(tk.Frame):

    def __init__(self, parent, app):
        super().__init__(parent, bg=app.colors["BACKGROUND"])

        self.app = app
        self.c = app.colors
        self.filter_mode = "All"

        self.build_ui()

    # =====================================
    # MAIN UI
    # =====================================

    def build_ui(self):

        header = tk.Frame(self, bg=self.c["BACKGROUND"])
        header.pack(fill="x", padx=30, pady=(25, 12))

        left = tk.Frame(header, bg=self.c["BACKGROUND"])
        left.pack(side="left")

        tk.Label(
            left,
            text="My Tasks ✓",
            font=(FONT, 23, "bold"),
            bg=self.c["BACKGROUND"],
            fg=self.c["TEXT"]
        ).pack(anchor="w")

        tk.Label(
            left,
            text="Organise your work and complete your goals.",
            font=(FONT, 10),
            bg=self.c["BACKGROUND"],
            fg=self.c["MUTED"]
        ).pack(anchor="w", pady=5)

        tk.Button(
            header,
            text="+ Add Task",
            command=self.open_task_dialog,
            bg=self.c["PRIMARY"],
            fg="#FFFFFF",
            activebackground=self.c["PRIMARY_HOVER"],
            activeforeground="#FFFFFF",
            font=(FONT, 10, "bold"),
            relief="flat",
            padx=18,
            pady=11,
            cursor="hand2"
        ).pack(side="right")

        # Statistics

        self.stats_frame = tk.Frame(
            self,
            bg=self.c["BACKGROUND"]
        )

        self.stats_frame.pack(
            fill="x",
            padx=25,
            pady=8
        )

        # Search

        search_frame = tk.Frame(
            self,
            bg=self.c["BACKGROUND"]
        )

        search_frame.pack(
            fill="x",
            padx=30,
            pady=8
        )

        self.search_entry = tk.Entry(
            search_frame,
            font=(FONT, 11),
            bg=self.c["CARD"],
            fg=self.c["TEXT"],
            insertbackground=self.c["TEXT"],
            relief="flat",
            highlightthickness=1,
            highlightbackground=self.c["BORDER"]
        )

        self.search_entry.pack(fill="x", ipady=11)

        self.search_entry.insert(0, "Search tasks...")
        self.search_entry.bind("<FocusIn>", self.clear_placeholder)
        self.search_entry.bind(
            "<KeyRelease>",
            lambda event: self.render_tasks()
        )

        # Filters

        self.filter_frame = tk.Frame(
            self,
            bg=self.c["BACKGROUND"]
        )

        self.filter_frame.pack(
            fill="x",
            padx=30,
            pady=8
        )

        self.build_filter_buttons()

        # Count

        self.count_label = tk.Label(
            self,
            text="",
            font=(FONT, 9, "bold"),
            bg=self.c["BACKGROUND"],
            fg=self.c["MUTED"]
        )

        self.count_label.pack(
            anchor="w",
            padx=30,
            pady=5
        )

        # Scrollable list

        body = tk.Frame(self, bg=self.c["BACKGROUND"])

        body.pack(
            fill="both",
            expand=True,
            padx=30,
            pady=(5, 18)
        )

        self.canvas = tk.Canvas(
            body,
            bg=self.c["BACKGROUND"],
            highlightthickness=0
        )

        self.scrollbar = tk.Scrollbar(
            body,
            orient="vertical",
            command=self.canvas.yview,
            width=14
        )

        self.canvas.configure(
            yscrollcommand=self.scrollbar.set
        )

        self.scrollbar.pack(side="right", fill="y")
        self.canvas.pack(side="left", fill="both", expand=True)

        self.task_container = tk.Frame(
            self.canvas,
            bg=self.c["BACKGROUND"]
        )

        self.window_id = self.canvas.create_window(
            (0, 0),
            window=self.task_container,
            anchor="nw"
        )

        self.task_container.bind(
            "<Configure>",
            lambda event: self.canvas.configure(
                scrollregion=self.canvas.bbox("all")
            )
        )

        self.canvas.bind(
            "<Configure>",
            lambda event: self.canvas.itemconfigure(
                self.window_id,
                width=event.width
            )
        )

        self.canvas.bind(
            "<MouseWheel>",
            self.mousewheel_scroll
        )

        self.canvas.bind(
            "<Prior>",
            lambda event: self.canvas.yview_scroll(-1, "pages")
        )

        self.canvas.bind(
            "<Next>",
            lambda event: self.canvas.yview_scroll(1, "pages")
        )

        self.render_tasks()

    # =====================================
    # FILTERS
    # =====================================

    def build_filter_buttons(self):

        for widget in self.filter_frame.winfo_children():
            widget.destroy()

        for name in ["All", "Pending", "Completed"]:

            selected = self.filter_mode == name

            tk.Button(
                self.filter_frame,
                text=name,
                command=lambda value=name: self.change_filter(value),
                bg=self.c["PRIMARY"] if selected else self.c["CARD"],
                fg="#FFFFFF" if selected else self.c["MUTED"],
                activebackground=self.c["SECONDARY"],
                relief="flat",
                bd=0,
                font=(FONT, 9, "bold"),
                padx=18,
                pady=9,
                cursor="hand2"
            ).pack(side="left", padx=(0, 7))

    def change_filter(self, mode):

        self.filter_mode = mode
        self.build_filter_buttons()
        self.render_tasks()

    # =====================================
    # SEARCH
    # =====================================

    def clear_placeholder(self, event):

        if self.search_entry.get() == "Search tasks...":
            self.search_entry.delete(0, "end")

    # =====================================
    # STATISTICS
    # =====================================

    def render_stats(self):

        for widget in self.stats_frame.winfo_children():
            widget.destroy()

        tasks = self.app.get_tasks()

        total = len(tasks)

        completed = sum(
            1 for task in tasks
            if task.get("completed", False)
        )

        pending = total - completed

        values = [
            ("TOTAL TASKS", total, self.c["PRIMARY"]),
            ("PENDING", pending, self.c["TEXT"]),
            ("COMPLETED", completed, self.c["SUCCESS"])
        ]

        for index, (heading, value, color) in enumerate(values):

            card = tk.Frame(
                self.stats_frame,
                bg=self.c["CARD"],
                highlightbackground=self.c["BORDER"],
                highlightthickness=1
            )

            card.grid(
                row=0,
                column=index,
                sticky="nsew",
                padx=5,
                pady=5
            )

            self.stats_frame.grid_columnconfigure(
                index,
                weight=1
            )

            tk.Label(
                card,
                text=heading,
                font=(FONT, 8, "bold"),
                bg=self.c["CARD"],
                fg=self.c["MUTED"]
            ).pack(anchor="w", padx=13, pady=(12, 3))

            tk.Label(
                card,
                text=str(value),
                font=(FONT, 20, "bold"),
                bg=self.c["CARD"],
                fg=color
            ).pack(anchor="w", padx=13, pady=(0, 12))

    # =====================================
    # DISPLAY TASKS
    # =====================================

    def render_tasks(self):

        for widget in self.task_container.winfo_children():
            widget.destroy()

        tasks = self.app.get_tasks()
        self.render_stats()

        query = self.search_entry.get().strip().lower()

        if query == "search tasks...":
            query = ""

        filtered = []

        for task in tasks:

            completed = task.get("completed", False)

            if self.filter_mode == "Pending" and completed:
                continue

            if self.filter_mode == "Completed" and not completed:
                continue

            searchable = (
                task.get("title", "") + " " +
                task.get("description", "") + " " +
                task.get("due_date", "")
            ).lower()

            if query and query not in searchable:
                continue

            filtered.append(task)

        self.count_label.configure(
            text=f"{len(filtered)} TASKS FOUND"
        )

        if not filtered:

            tk.Label(
                self.task_container,
                text="No tasks found. Add your first task!",
                font=(FONT, 12),
                bg=self.c["BACKGROUND"],
                fg=self.c["MUTED"]
            ).pack(pady=45)

            return

        for task in filtered:
            self.create_task_card(task)

    # =====================================
    # TASK CARD
    # =====================================

    def create_task_card(self, task):

        completed = task.get("completed", False)

        card = tk.Frame(
            self.task_container,
            bg=self.c["CARD"],
            highlightbackground=self.c["BORDER"],
            highlightthickness=1
        )

        card.pack(fill="x", pady=7)

        top = tk.Frame(card, bg=self.c["CARD"])
        top.pack(fill="x", padx=15, pady=(14, 5))

        tk.Button(
            top,
            text="✓" if completed else "○",
            command=lambda t=task: self.toggle_completed(t),
            bg=self.c["SUCCESS"] if completed else self.c["CARD_LIGHT"],
            fg="#FFFFFF" if completed else self.c["MUTED"],
            relief="flat",
            bd=0,
            font=(FONT, 12, "bold"),
            width=3,
            cursor="hand2"
        ).pack(side="left", padx=(0, 10))

        tk.Label(
            top,
            text=task.get("title", "Untitled Task"),
            font=(FONT, 12, "bold"),
            bg=self.c["CARD"],
            fg=self.c["MUTED"] if completed else self.c["TEXT"]
        ).pack(side="left", fill="x", expand=True)

        tk.Label(
            card,
            text="COMPLETED" if completed else "PENDING",
            font=(FONT, 8, "bold"),
            bg=self.c["CARD"],
            fg=self.c["SUCCESS"] if completed else self.c["PRIMARY"]
        ).pack(anchor="w", padx=58, pady=3)

        description = task.get("description", "")

        if description:

            tk.Label(
                card,
                text=description,
                font=(FONT, 10),
                bg=self.c["CARD"],
                fg=self.c["MUTED"],
                wraplength=700,
                justify="left"
            ).pack(anchor="w", padx=58, pady=4)

        due_date = task.get("due_date", "")

        if due_date:

            tk.Label(
                card,
                text=f"Due date: {due_date}",
                font=(FONT, 9),
                bg=self.c["CARD"],
                fg=self.c["MUTED"]
            ).pack(anchor="w", padx=58, pady=3)

        actions = tk.Frame(card, bg=self.c["CARD"])
        actions.pack(fill="x", padx=55, pady=(8, 12))

        tk.Button(
            actions,
            text="Edit",
            command=lambda t=task: self.open_task_dialog(t),
            bg=self.c["SECONDARY"],
            fg=self.c["PRIMARY"],
            relief="flat",
            padx=15,
            pady=7,
            cursor="hand2"
        ).pack(side="left", padx=(0, 7))

        tk.Button(
            actions,
            text="Delete",
            command=lambda t=task: self.delete_task(t),
            bg=self.c["DANGER_BG"],
            fg=self.c["DANGER"],
            relief="flat",
            padx=15,
            pady=7,
            cursor="hand2"
        ).pack(side="left")

        tk.Button(
            actions,
            text="Reopen" if completed else "Mark Complete",
            command=lambda t=task: self.toggle_completed(t),
            bg=self.c["CARD_LIGHT"],
            fg=self.c["TEXT"],
            relief="flat",
            padx=15,
            pady=7,
            cursor="hand2"
        ).pack(side="right")

    # =====================================
    # ADD / EDIT TASK DIALOG
    # =====================================

    def open_task_dialog(self, task=None):

        dialog = tk.Toplevel(self)

        dialog.title("Edit Task" if task else "Add New Task")
        dialog.geometry("520x620")
        dialog.minsize(400, 560)
        dialog.resizable(True, True)

        dialog.configure(bg=self.c["BACKGROUND"])
        dialog.transient(self.app.root)
        dialog.grab_set()

        tk.Label(
            dialog,
            text="Edit Task" if task else "Create New Task",
            font=(FONT, 20, "bold"),
            bg=self.c["BACKGROUND"],
            fg=self.c["TEXT"]
        ).pack(anchor="w", padx=25, pady=(25, 5))

        tk.Label(
            dialog,
            text="Add details for your task.",
            font=(FONT, 10),
            bg=self.c["BACKGROUND"],
            fg=self.c["MUTED"]
        ).pack(anchor="w", padx=25, pady=(0, 18))

        # Title

        tk.Label(
            dialog,
            text="TASK TITLE",
            font=(FONT, 9, "bold"),
            bg=self.c["BACKGROUND"],
            fg=self.c["MUTED"]
        ).pack(anchor="w", padx=25, pady=(5, 7))

        title_entry = tk.Entry(
            dialog,
            font=(FONT, 11),
            bg=self.c["CARD"],
            fg=self.c["TEXT"],
            insertbackground=self.c["TEXT"],
            relief="flat",
            highlightthickness=1,
            highlightbackground=self.c["BORDER"]
        )

        title_entry.pack(fill="x", padx=25, ipady=11)

        # Description

        tk.Label(
            dialog,
            text="DESCRIPTION",
            font=(FONT, 9, "bold"),
            bg=self.c["BACKGROUND"],
            fg=self.c["MUTED"]
        ).pack(anchor="w", padx=25, pady=(18, 7))

        description_text = tk.Text(
            dialog,
            height=5,
            font=(FONT, 10),
            bg=self.c["CARD"],
            fg=self.c["TEXT"],
            insertbackground=self.c["TEXT"],
            relief="flat",
            wrap="word",
            padx=10,
            pady=10
        )

        description_text.pack(fill="x", padx=25)

        # Due date

        tk.Label(
            dialog,
            text="DUE DATE (OPTIONAL)",
            font=(FONT, 9, "bold"),
            bg=self.c["BACKGROUND"],
            fg=self.c["MUTED"]
        ).pack(anchor="w", padx=25, pady=(16, 7))

        date_entry = tk.Entry(
            dialog,
            font=(FONT, 10),
            bg=self.c["CARD"],
            fg=self.c["TEXT"],
            insertbackground=self.c["TEXT"],
            relief="flat",
            highlightthickness=1,
            highlightbackground=self.c["BORDER"]
        )

        date_entry.pack(fill="x", padx=25, ipady=10)

        tk.Label(
            dialog,
            text="Example: 10 Nov 2026",
            font=(FONT, 8),
            bg=self.c["BACKGROUND"],
            fg=self.c["MUTED"]
        ).pack(anchor="w", padx=25, pady=4)

        if task:

            title_entry.insert(0, task.get("title", ""))

            description_text.insert(
                "1.0",
                task.get("description", "")
            )

            date_entry.insert(
                0,
                task.get("due_date", "")
            )

        # Fixed bottom button area

        buttons = tk.Frame(
            dialog,
            bg=self.c["BACKGROUND"]
        )

        buttons.pack(
            side="bottom",
            fill="x",
            padx=25,
            pady=20
        )

        tk.Button(
            buttons,
            text="Cancel",
            command=dialog.destroy,
            bg=self.c["CARD"],
            fg=self.c["TEXT"],
            relief="flat",
            bd=0,
            font=(FONT, 10),
            padx=22,
            pady=12,
            cursor="hand2"
        ).pack(side="left")

        def save():

            title = title_entry.get().strip()

            description = description_text.get(
                "1.0",
                "end-1c"
            ).strip()

            due_date = date_entry.get().strip()

            if not title:

                messagebox.showwarning(
                    "Missing Title",
                    "Please enter a task title.",
                    parent=dialog
                )

                title_entry.focus_set()
                return

            try:

                if task:

                    self.app.update_task(
                        task["id"],
                        title,
                        description,
                        due_date
                    )

                    message = "Task updated and saved successfully."

                else:

                    self.app.create_task(
                        title,
                        description,
                        due_date
                    )

                    message = "Task created and saved successfully."

                dialog.destroy()
                self.render_tasks()

                messagebox.showinfo(
                    "CloudNote",
                    message
                )

            except (RuntimeError, ValueError, OSError) as error:

                messagebox.showerror(
                    "Save Error",
                    str(error),
                    parent=dialog
                )

        # VISIBLE SAVE BUTTON

        tk.Button(
            buttons,
            text="💾  SAVE TASK",
            command=save,
            bg=self.c["PRIMARY"],
            fg="#FFFFFF",
            activebackground=self.c["PRIMARY_HOVER"],
            activeforeground="#FFFFFF",
            relief="flat",
            bd=0,
            font=(FONT, 11, "bold"),
            padx=28,
            pady=13,
            cursor="hand2"
        ).pack(side="right")

        title_entry.focus_set()

    # =====================================
    # COMPLETE / REOPEN
    # =====================================

    def toggle_completed(self, task):

        new_status = not task.get("completed", False)

        try:

            self.app.set_task_completed(
                task["id"],
                new_status
            )

            self.render_tasks()

        except (RuntimeError, ValueError, OSError) as error:

            messagebox.showerror(
                "Task Error",
                str(error)
            )

    # =====================================
    # DELETE PERMANENTLY
    # =====================================

    def delete_task(self, task):

        confirm = messagebox.askyesno(
            "Delete Task",
            f"Delete '{task['title']}' permanently?\n\nThis cannot be undone."
        )

        if not confirm:
            return

        try:

            self.app.delete_task(task["id"])
            self.render_tasks()

            messagebox.showinfo(
                "Deleted",
                "Task has been permanently deleted."
            )

        except (RuntimeError, ValueError, OSError) as error:

            messagebox.showerror(
                "Delete Error",
                str(error)
            )

    # =====================================
    # SCROLLING
    # =====================================

    def mousewheel_scroll(self, event):

        self.canvas.yview_scroll(
            int(-event.delta / 120),
            "units"
        )
