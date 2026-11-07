import tkinter as tk

from config import FONT


class DashboardPage(tk.Frame):

    def __init__(self, parent, app):

        self.app = app
        self.c = app.colors

        super().__init__(
            parent,
            bg=self.c["BACKGROUND"]
        )

        self.build_ui()

    def build_ui(self):

        # Header

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
            text="Good day! ✨",
            font=(FONT, 24, "bold"),
            bg=self.c["BACKGROUND"],
            fg=self.c["TEXT"]
        ).pack(anchor="w")

        tk.Label(
            header,
            text="Your Notes Dashboard",
            font=(FONT, 11),
            bg=self.c["BACKGROUND"],
            fg=self.c["MUTED"]
        ).pack(anchor="w", pady=5)

        # Scrollable body

        body = tk.Frame(
            self,
            bg=self.c["BACKGROUND"]
        )

        body.pack(
            fill="both",
            expand=True,
            padx=35,
            pady=15
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

        content = tk.Frame(
            canvas,
            bg=self.c["BACKGROUND"]
        )

        window_id = canvas.create_window(
            (0, 0),
            window=content,
            anchor="nw"
        )

        content.bind(
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
            "<Enter>",
            lambda e: canvas.focus_set()
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

        # Statistics

        notes = self.app.get_notes()

        stats = tk.Frame(
            content,
            bg=self.c["BACKGROUND"]
        )

        stats.pack(
            fill="x",
            pady=10
        )

        cards = [
            ("TOTAL NOTES", len(notes), "▤"),
            ("RECENT NOTES", len(notes[:5]), "◷"),
            ("STATUS", "Active", "✦")
        ]

        for i, (heading, value, icon) in enumerate(cards):

            card = tk.Frame(
                stats,
                bg=self.c["CARD"],
                highlightbackground=self.c["BORDER"],
                highlightthickness=1
            )

            card.grid(
                row=0,
                column=i,
                sticky="nsew",
                padx=6,
                pady=6
            )

            stats.grid_columnconfigure(
                i,
                weight=1
            )

            tk.Label(
                card,
                text=icon,
                font=(FONT, 19),
                bg=self.c["CARD"],
                fg=self.c["PRIMARY"]
            ).pack(
                anchor="w",
                padx=18,
                pady=(18, 5)
            )

            tk.Label(
                card,
                text=heading,
                font=(FONT, 9, "bold"),
                bg=self.c["CARD"],
                fg=self.c["MUTED"]
            ).pack(
                anchor="w",
                padx=18
            )

            tk.Label(
                card,
                text=str(value),
                font=(FONT, 20, "bold"),
                bg=self.c["CARD"],
                fg=self.c["TEXT"]
            ).pack(
                anchor="w",
                padx=18,
                pady=(5, 18)
            )

        # Banner

        banner = tk.Frame(
            content,
            bg=self.c["SECONDARY"]
        )

        banner.pack(
            fill="x",
            pady=20
        )

        tk.Label(
            banner,
            text="A fresh page, a fresh idea.",
            font=(FONT, 19, "bold"),
            bg=self.c["SECONDARY"],
            fg=self.c["PRIMARY"]
        ).pack(
            anchor="w",
            padx=22,
            pady=(20, 5)
        )

        tk.Label(
            banner,
            text="Capture your thoughts and keep everything organised.",
            font=(FONT, 10),
            bg=self.c["SECONDARY"],
            fg=self.c["TEXT"]
        ).pack(
            anchor="w",
            padx=22
        )

        tk.Button(
            banner,
            text="+  Create New Note",
            command=self.app.show_add_note,
            bg=self.c["PRIMARY"],
            fg="#FFFFFF",
            activebackground=self.c["PRIMARY_HOVER"],
            activeforeground="#FFFFFF",
            relief="flat",
            bd=0,
            font=(FONT, 10, "bold"),
            padx=20,
            pady=11,
            cursor="hand2"
        ).pack(
            anchor="w",
            padx=22,
            pady=18
        )

        # Recent notes

        tk.Label(
            content,
            text="Recent Notes",
            font=(FONT, 17, "bold"),
            bg=self.c["BACKGROUND"],
            fg=self.c["TEXT"]
        ).pack(
            anchor="w",
            pady=(10, 12)
        )

        if not notes:

            tk.Label(
                content,
                text="No notes yet. Create your first note!",
                font=(FONT, 11),
                bg=self.c["BACKGROUND"],
                fg=self.c["MUTED"]
            ).pack(
                anchor="w",
                pady=15
            )

        for note in notes[:5]:

            card = tk.Frame(
                content,
                bg=self.c["CARD"],
                highlightbackground=self.c["BORDER"],
                highlightthickness=1
            )

            card.pack(
                fill="x",
                pady=5
            )

            tk.Label(
                card,
                text=note.get("title", "Untitled"),
                font=(FONT, 12, "bold"),
                bg=self.c["CARD"],
                fg=self.c["TEXT"]
            ).pack(
                anchor="w",
                padx=18,
                pady=(13, 3)
            )

            tk.Label(
                card,
                text=note.get("content", "")[:110],
                font=(FONT, 9),
                bg=self.c["CARD"],
                fg=self.c["MUTED"]
            ).pack(
                anchor="w",
                padx=18,
                pady=(0, 5)
            )

            tk.Button(
                card,
                text="Open Note →",
                command=lambda n=note: self.app.show_add_note(n),
                bg=self.c["CARD"],
                fg=self.c["PRIMARY"],
                relief="flat",
                bd=0,
                cursor="hand2"
            ).pack(
                anchor="e",
                padx=15,
                pady=(0, 10)
            )