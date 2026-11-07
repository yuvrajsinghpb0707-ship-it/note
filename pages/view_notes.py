
import tkinter as tk
from tkinter import messagebox, filedialog
import re

from config import FONT


class ViewNotesPage(tk.Frame):

    def __init__(self, parent, app):

        self.app = app
        self.c = app.colors

        super().__init__(
            parent,
            bg=self.c["BACKGROUND"]
        )

        self.search_var = tk.StringVar()

        self.build_ui()

    def build_ui(self):

        header = tk.Frame(
            self,
            bg=self.c["BACKGROUND"]
        )

        header.pack(
            fill="x",
            padx=35,
            pady=(30, 15)
        )

        tk.Label(
            header,
            text="My Notes",
            font=(FONT, 23, "bold"),
            bg=self.c["BACKGROUND"],
            fg=self.c["TEXT"]
        ).pack(anchor="w")

        tk.Label(
            header,
            text="Manage all your saved notes.",
            font=(FONT, 10),
            bg=self.c["BACKGROUND"],
            fg=self.c["MUTED"]
        ).pack(anchor="w", pady=5)

        # Search

        search_frame = tk.Frame(
            self,
            bg=self.c["BACKGROUND"]
        )

        search_frame.pack(
            fill="x",
            padx=35,
            pady=10
        )

        self.search_entry = tk.Entry(
            search_frame,
            textvariable=self.search_var,
            font=(FONT, 11),
            bg=self.c["CARD"],
            fg=self.c["TEXT"],
            insertbackground=self.c["TEXT"],
            relief="flat",
            highlightthickness=1,
            highlightbackground=self.c["BORDER"]
        )

        self.search_entry.pack(
            fill="x",
            ipady=12
        )

        self.search_entry.insert(
            0,
            "Search your notes..."
        )

        self.search_entry.bind(
            "<FocusIn>",
            self.clear_placeholder
        )

        self.search_entry.bind(
            "<KeyRelease>",
            lambda e: self.render_notes()
        )

        # Count

        self.count_label = tk.Label(
            self,
            text="",
            font=(FONT, 10, "bold"),
            bg=self.c["BACKGROUND"],
            fg=self.c["MUTED"]
        )

        self.count_label.pack(
            anchor="w",
            padx=35,
            pady=8
        )

        # Scrollable notes

        body = tk.Frame(
            self,
            bg=self.c["BACKGROUND"]
        )

        body.pack(
            fill="both",
            expand=True,
            padx=35,
            pady=(5, 20)
        )

        self.canvas = tk.Canvas(
            body,
            bg=self.c["BACKGROUND"],
            highlightthickness=0
        )

        scrollbar = tk.Scrollbar(
            body,
            orient="vertical",
            command=self.canvas.yview,
            width=14,
            bg=self.c["CARD_LIGHT"],
            troughcolor=self.c["BACKGROUND"],
            activebackground=self.c["PRIMARY"]
        )

        self.canvas.configure(
            yscrollcommand=scrollbar.set
        )

        scrollbar.pack(
            side="right",
            fill="y"
        )

        self.canvas.pack(
            side="left",
            fill="both",
            expand=True
        )

        self.note_container = tk.Frame(
            self.canvas,
            bg=self.c["BACKGROUND"]
        )

        self.window_id = self.canvas.create_window(
            (0, 0),
            window=self.note_container,
            anchor="nw"
        )

        self.note_container.bind(
            "<Configure>",
            lambda e: self.canvas.configure(
                scrollregion=self.canvas.bbox("all")
            )
        )

        self.canvas.bind(
            "<Configure>",
            lambda e: self.canvas.itemconfigure(
                self.window_id,
                width=e.width
            )
        )

        self.canvas.bind(
            "<MouseWheel>",
            lambda e: self.canvas.yview_scroll(
                int(-e.delta / 120),
                "units"
            )
        )

        self.canvas.bind(
            "<Prior>",
            lambda e: self.canvas.yview_scroll(-1, "pages")
        )

        self.canvas.bind(
            "<Next>",
            lambda e: self.canvas.yview_scroll(1, "pages")
        )

        self.render_notes()

    def clear_placeholder(self, event):

        if self.search_entry.get() == "Search your notes...":

            self.search_entry.delete(
                0,
                "end"
            )

    def render_notes(self):

        for widget in self.note_container.winfo_children():
            widget.destroy()

        notes = self.app.get_notes()

        query = self.search_var.get().strip().lower()

        if query == "search your notes...":
            query = ""

        filtered = [
            note for note in notes
            if query in note.get("title", "").lower()
            or query in note.get("content", "").lower()
        ]

        self.count_label.configure(
            text=f"{len(filtered)} NOTES FOUND"
        )

        if not filtered:

            tk.Label(
                self.note_container,
                text="No notes found.",
                font=(FONT, 12),
                bg=self.c["BACKGROUND"],
                fg=self.c["MUTED"]
            ).pack(
                pady=50
            )

            return

        for note in filtered:

            self.create_note_card(note)

    def create_note_card(self, note):

        card = tk.Frame(
            self.note_container,
            bg=self.c["CARD"],
            highlightbackground=self.c["BORDER"],
            highlightthickness=1
        )

        card.pack(
            fill="x",
            pady=7
        )

        top = tk.Frame(
            card,
            bg=self.c["CARD"]
        )

        top.pack(
            fill="x",
            padx=18,
            pady=(15, 5)
        )

        tk.Label(
            top,
            text=note.get("title", "Untitled"),
            font=(FONT, 13, "bold"),
            bg=self.c["CARD"],
            fg=self.c["TEXT"]
        ).pack(
            side="left"
        )

        tk.Label(
            card,
            text=note.get("content", "")[:180],
            font=(FONT, 10),
            bg=self.c["CARD"],
            fg=self.c["MUTED"],
            justify="left",
            wraplength=650
        ).pack(
            anchor="w",
            padx=18,
            pady=5
        )

        tk.Label(
            card,
            text="Updated: " + note.get("updated_at", ""),
            font=(FONT, 8),
            bg=self.c["CARD"],
            fg=self.c["MUTED"]
        ).pack(
            anchor="w",
            padx=18,
            pady=5
        )

        actions = tk.Frame(
            card,
            bg=self.c["CARD"]
        )

        actions.pack(
            fill="x",
            padx=15,
            pady=(5, 13)
        )

        # Edit button

        tk.Button(
            actions,
            text="Edit",
            command=lambda n=note: self.app.show_add_note(n),
            bg=self.c["SECONDARY"],
            fg=self.c["PRIMARY"],
            relief="flat",
            padx=18,
            pady=7,
            cursor="hand2"
        ).pack(
            side="left",
            padx=3
        )

        # Download button

        tk.Button(
            actions,
            text="Download ↓",
            command=lambda n=note: self.download_note(n),
            bg=self.c["SECONDARY"],
            fg=self.c["PRIMARY"],
            relief="flat",
            padx=18,
            pady=7,
            cursor="hand2"
        ).pack(
            side="left",
            padx=3
        )

        # Delete button

        tk.Button(
            actions,
            text="Delete",
            command=lambda n=note: self.delete_note(n),
            bg=self.c["DANGER_BG"],
            fg=self.c["DANGER"],
            relief="flat",
            padx=18,
            pady=7,
            cursor="hand2"
        ).pack(
            side="left",
            padx=3
        )

    def download_note(self, note):

        title = note.get("title", "Untitled")
        content = note.get("content", "")

        safe_title = re.sub(
            r'[\\/:*?"<>|]',
            "",
            title
        ).strip()

        if not safe_title:
            safe_title = "CloudNote"

        file_path = filedialog.asksaveasfilename(
            title="Download Note",
            initialfile=f"{safe_title}.txt",
            defaultextension=".txt",
            filetypes=[
                ("Text File", "*.txt"),
                ("All Files", "*.*")
            ]
        )

        if not file_path:
            return

        try:

            with open(
                file_path,
                "w",
                encoding="utf-8"
            ) as file:

                file.write(title)
                file.write("\n")
                file.write("=" * len(title))
                file.write("\n\n")
                file.write(content)

            messagebox.showinfo(
                "Download Complete",
                f"Your note was downloaded successfully.\n\n{file_path}"
            )

        except OSError as error:

            messagebox.showerror(
                "Download Error",
                str(error)
            )

    def delete_note(self, note):

        confirm = messagebox.askyesno(
            "Delete Note",
            f"Are you sure you want to delete '{note['title']}'?"
        )

        if not confirm:
            return

        try:

            self.app.delete_note(note["id"])

            self.render_notes()

        except (RuntimeError, ValueError, OSError) as error:

            messagebox.showerror(
                "Delete Error",
                str(error)
            )
