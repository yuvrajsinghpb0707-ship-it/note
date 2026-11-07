
import tkinter as tk
from tkinter import messagebox, filedialog
import re

from config import FONT


class AddNotePage(tk.Frame):

    def __init__(self, parent, app, note=None):
        self.app = app
        self.c = app.colors
        self.note = note

        super().__init__(
            parent,
            bg=self.c["BACKGROUND"]
        )

        self.build_ui()

    def build_ui(self):

        header = tk.Frame(
            self,
            bg=self.c["BACKGROUND"]
        )

        header.pack(
            fill="x",
            padx=35,
            pady=(30, 20)
        )

        heading = (
            "Edit Note"
            if self.note
            else "Create New Note"
        )

        tk.Label(
            header,
            text=heading,
            font=(FONT, 23, "bold"),
            bg=self.c["BACKGROUND"],
            fg=self.c["TEXT"]
        ).pack(anchor="w")

        tk.Label(
            header,
            text="Write down your ideas and thoughts.",
            font=(FONT, 10),
            bg=self.c["BACKGROUND"],
            fg=self.c["MUTED"]
        ).pack(anchor="w", pady=5)

        # Scrollable editor

        body = tk.Frame(
            self,
            bg=self.c["BACKGROUND"]
        )

        body.pack(
            fill="both",
            expand=True,
            padx=35,
            pady=10
        )

        canvas = tk.Canvas(
            body,
            bg=self.c["BACKGROUND"],
            highlightthickness=0
        )

        scrollbar = tk.Scrollbar(
            body,
            orient="vertical",
            command=canvas.yview,
            width=14,
            bg=self.c["CARD_LIGHT"],
            troughcolor=self.c["BACKGROUND"],
            activebackground=self.c["PRIMARY"]
        )

        canvas.configure(
            yscrollcommand=scrollbar.set
        )

        scrollbar.pack(
            side="right",
            fill="y"
        )

        canvas.pack(
            side="left",
            fill="both",
            expand=True
        )

        form = tk.Frame(
            canvas,
            bg=self.c["BACKGROUND"]
        )

        window_id = canvas.create_window(
            (0, 0),
            window=form,
            anchor="nw"
        )

        form.bind(
            "<Configure>",
            lambda e: canvas.configure(
                scrollregion=canvas.bbox("all")
            )
        )

        canvas.bind(
            "<Configure>",
            lambda e: canvas.itemconfigure(
                window_id,
                width=e.width
            )
        )

        canvas.bind(
            "<MouseWheel>",
            lambda e: canvas.yview_scroll(
                int(-e.delta / 120),
                "units"
            )
        )

        canvas.bind(
            "<Prior>",
            lambda e: canvas.yview_scroll(-1, "pages")
        )

        canvas.bind(
            "<Next>",
            lambda e: canvas.yview_scroll(1, "pages")
        )

        # Title

        tk.Label(
            form,
            text="NOTE TITLE",
            font=(FONT, 9, "bold"),
            bg=self.c["BACKGROUND"],
            fg=self.c["MUTED"]
        ).pack(
            anchor="w",
            pady=(10, 8)
        )

        self.title_entry = tk.Entry(
            form,
            font=(FONT, 13),
            bg=self.c["CARD"],
            fg=self.c["TEXT"],
            insertbackground=self.c["TEXT"],
            relief="flat",
            highlightthickness=1,
            highlightbackground=self.c["BORDER"],
            highlightcolor=self.c["PRIMARY"]
        )

        self.title_entry.pack(
            fill="x",
            ipady=13
        )

        # Content

        tk.Label(
            form,
            text="YOUR CONTENT",
            font=(FONT, 9, "bold"),
            bg=self.c["BACKGROUND"],
            fg=self.c["MUTED"]
        ).pack(
            anchor="w",
            pady=(25, 8)
        )

        editor_box = tk.Frame(
            form,
            bg=self.c["CARD"],
            highlightbackground=self.c["BORDER"],
            highlightthickness=1
        )

        editor_box.pack(
            fill="both",
            expand=True
        )

        self.content_text = tk.Text(
            editor_box,
            height=15,
            font=(FONT, 11),
            bg=self.c["CARD"],
            fg=self.c["TEXT"],
            insertbackground=self.c["TEXT"],
            relief="flat",
            wrap="word",
            padx=15,
            pady=15,
            undo=True
        )

        text_scroll = tk.Scrollbar(
            editor_box,
            orient="vertical",
            command=self.content_text.yview,
            width=13,
            bg=self.c["CARD_LIGHT"],
            troughcolor=self.c["BACKGROUND"],
            activebackground=self.c["PRIMARY"]
        )

        self.content_text.configure(
            yscrollcommand=text_scroll.set
        )

        text_scroll.pack(
            side="right",
            fill="y"
        )

        self.content_text.pack(
            side="left",
            fill="both",
            expand=True
        )

        # Existing note values

        if self.note:

            self.title_entry.insert(
                0,
                self.note.get("title", "")
            )

            self.content_text.insert(
                "1.0",
                self.note.get("content", "")
            )

        # Buttons

        buttons = tk.Frame(
            form,
            bg=self.c["BACKGROUND"]
        )

        buttons.pack(
            fill="x",
            pady=25
        )

        tk.Button(
            buttons,
            text="Cancel",
            command=self.app.show_dashboard,
            bg=self.c["CARD"],
            fg=self.c["TEXT"],
            relief="flat",
            padx=20,
            pady=12,
            cursor="hand2"
        ).pack(
            side="left",
            padx=(0, 8)
        )

        tk.Button(
            buttons,
            text="Download ↓",
            command=self.download_current_note,
            bg=self.c["SECONDARY"],
            fg=self.c["PRIMARY"],
            relief="flat",
            font=(FONT, 10, "bold"),
            padx=18,
            pady=12,
            cursor="hand2"
        ).pack(
            side="right",
            padx=(8, 0)
        )

        tk.Button(
            buttons,
            text="Save Note  →",
            command=self.save_note,
            bg=self.c["PRIMARY"],
            fg="#FFFFFF",
            activebackground=self.c["PRIMARY_HOVER"],
            activeforeground="#FFFFFF",
            relief="flat",
            font=(FONT, 10, "bold"),
            padx=25,
            pady=12,
            cursor="hand2"
        ).pack(
            side="right"
        )

    def download_current_note(self):

        title = self.title_entry.get().strip()

        content = self.content_text.get(
            "1.0",
            "end-1c"
        ).strip()

        if not title:
            title = "CloudNote"

        if not content:
            messagebox.showwarning(
                "Empty Note",
                "Write something in your note before downloading."
            )
            return

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

    def save_note(self):

        title = self.title_entry.get().strip()

        content = self.content_text.get(
            "1.0",
            "end-1c"
        ).strip()

        if not title:

            messagebox.showwarning(
                "Missing Title",
                "Please enter a note title."
            )

            return

        if not content:

            messagebox.showwarning(
                "Empty Note",
                "Please write something in your note."
            )

            return

        try:

            if self.note:

                self.app.update_note(
                    self.note["id"],
                    title,
                    content
                )

                messagebox.showinfo(
                    "Updated",
                    "Your note has been updated."
                )

            else:

                self.app.create_note(
                    title,
                    content
                )

                messagebox.showinfo(
                    "Saved",
                    "Your note has been saved."
                )

            self.app.show_notes()

        except (RuntimeError, ValueError, OSError) as error:

            messagebox.showerror(
                "Save Error",
                str(error)
            )
