"""External visual editor for Mario Party 4's board-space layouts."""

from __future__ import annotations

import copy
import subprocess
import sys
import tkinter as tk
from pathlib import Path
from tkinter import filedialog, messagebox, ttk

from board_format import BOARD_FILES, TYPE_NAMES, board_bytes, load_project, parse_spaces, replace_board, save_project, validate

HERE = Path(__file__).resolve().parent
GAME = HERE.parent
COLORS = {0: "#999999", 1: "#2288ee", 2: "#ed4848", 3: "#43c567", 4: "#ffe078",
          5: "#8425aa", 6: "#ff9950", 7: "#c16edb", 8: "#ffde38", 9: "#60cfc4",
          10: "#d4b2e5", 11: "#aaaaaa"}


class BoardEditor(tk.Tk):
    def __init__(self) -> None:
        super().__init__()
        self.title("Mario Party 4 Deluxe — Board Editor")
        self.geometry("1260x800")
        self.minsize(960, 620)
        self.board_id = "w01"
        self.original: Path | None = None
        self.project: Path | None = None
        self.spaces: list[dict] = []
        self.selected: int | None = None
        self.undo: list[list[dict]] = []
        self.redo: list[list[dict]] = []
        self.dragging = False
        self.changed = False
        self.scale = 1.0
        self.center_x = self.center_z = 0.0
        self._build_ui()
        self.bind("<Control-z>", lambda _: self._history(False))
        self.bind("<Control-y>", lambda _: self._history(True))
        self.bind("<Control-s>", lambda _: self.save())
        self.protocol("WM_DELETE_WINDOW", self._close)

    def _build_ui(self) -> None:
        bar = ttk.Frame(self, padding=8)
        bar.pack(fill="x")
        for label, action in (("Import from disc…", self.import_disc), ("Open archive…", self.open_archive),
                              ("Open project…", self.open_project), ("Save project", self.save),
                              ("Export to game", self.export), ("Undo", lambda: self._history(False)),
                              ("Redo", lambda: self._history(True))):
            ttk.Button(bar, text=label, command=action).pack(side="left", padx=2)
        self.board_var = tk.StringVar(value=self.board_id)
        selector = ttk.Combobox(bar, textvariable=self.board_var, width=5, state="readonly", values=list(BOARD_FILES))
        selector.pack(side="right")
        selector.bind("<<ComboboxSelected>>", self._choose_board)
        ttk.Label(bar, text="Board:").pack(side="right", padx=4)

        main = ttk.PanedWindow(self, orient="horizontal")
        main.pack(fill="both", expand=True)
        self.canvas = tk.Canvas(main, background="#202634", highlightthickness=0)
        main.add(self.canvas, weight=5)
        self.canvas.bind("<Configure>", lambda _: self.draw())
        self.canvas.bind("<Button-1>", self._click)
        self.canvas.bind("<B1-Motion>", self._drag)
        self.canvas.bind("<ButtonRelease-1>", self._release)
        side = ttk.Frame(main, padding=12)
        main.add(side, weight=1)
        self.heading = ttk.Label(side, text="Import a board to begin", font=("Segoe UI", 12, "bold"))
        self.heading.pack(anchor="w", pady=(0, 15))
        self.fields: dict[str, tk.StringVar] = {}
        for name, label in (("x", "X position"), ("y", "Height (Y)"), ("z", "Z position"),
                            ("type", "Space type"), ("flags", "Event flags (hex)"),
                            ("links", "Routes to spaces (IDs)")):
            ttk.Label(side, text=label).pack(anchor="w", pady=(7, 0))
            variable = tk.StringVar()
            self.fields[name] = variable
            if name == "type":
                widget = ttk.Combobox(side, textvariable=variable, state="readonly",
                                      values=[f"{i}: {TYPE_NAMES[i]}" for i in TYPE_NAMES])
                widget.bind("<<ComboboxSelected>>", lambda _: self.apply_fields())
            else:
                widget = ttk.Entry(side, textvariable=variable)
                widget.bind("<Return>", lambda _: self.apply_fields())
                widget.bind("<FocusOut>", lambda _: self.apply_fields())
            widget.pack(fill="x")
        ttk.Button(side, text="Apply values", command=self.apply_fields).pack(fill="x", pady=15)
        ttk.Label(side, text="Drag a space to move it. Edit route IDs to change a junction.\n"
                  "The view shows spaces and routes; board scenery is unchanged.", wraplength=240).pack(anchor="w")
        self.status = tk.StringVar(value="Select your own Europe Rev 2 RVZ, or open an extracted board archive.")
        ttk.Label(self, textvariable=self.status, padding=8).pack(fill="x")

    def _set_board(self, board_id: str, original: Path, spaces: list[dict], project: Path | None = None) -> None:
        self.board_id, self.original, self.project, self.spaces = board_id, original, project, spaces
        self.board_var.set(board_id)
        self.selected, self.undo, self.redo, self.changed = None, [], [], False
        self.status.set(f"{BOARD_FILES[board_id]} — {len(spaces)} spaces. Original: {original}")
        self._refresh_fields()
        self.draw()

    def _load_archive(self, path: Path) -> None:
        board_id = path.stem.lower()
        if board_id not in BOARD_FILES:
            raise ValueError("Choose w01.bin–w06.bin, w20.bin, or w21.bin")
        self._set_board(board_id, path, parse_spaces(board_bytes(path.read_bytes())))

    def _choose_board(self, _: object) -> None:
        board_id = self.board_var.get()
        archive = HERE / "original" / "files" / "data" / f"{board_id}.bin"
        if archive.is_file():
            self._open(lambda: self._load_archive(archive))
        else:
            self.board_var.set(self.board_id)
            messagebox.showinfo("Original needed", "Import your disc first to edit this board.")

    def import_disc(self) -> None:
        disc = filedialog.askopenfilename(title="Select your own Mario Party 4 disc image",
                                          filetypes=[("Disc images", "*.rvz *.iso *.gcm"), ("All files", "*.*")])
        if not disc:
            return
        tool = Path.home() / "Documents" / "Dolphin-x64" / "DolphinTool.exe"
        if not tool.is_file():
            selected = filedialog.askopenfilename(title="Select DolphinTool.exe", filetypes=[("Executable", "*.exe")])
            if not selected:
                return
            tool = Path(selected)

        def run() -> None:
            destination = HERE / "original"
            destination.mkdir(parents=True, exist_ok=True)
            for board_id in BOARD_FILES:
                self.status.set(f"Extracting {board_id} from your disc…")
                self.update_idletasks()
                result = subprocess.run([str(tool), "extract", "-i", disc, "-o", str(destination),
                                         "-s", f"data/{board_id}.bin"], capture_output=True, text=True)
                if result.returncode:
                    raise RuntimeError(f"Failed to extract {board_id}: {result.stderr or result.stdout}")
            self._load_archive(destination / "files" / "data" / f"{self.board_var.get()}.bin")
        self._open(run)

    def _open(self, action) -> None:
        if self.changed and not messagebox.askyesno("Unsaved changes", "Discard changes since your last save?"):
            return
        try:
            action()
        except Exception as error:
            messagebox.showerror("Board Editor", str(error))

    def open_archive(self) -> None:
        name = filedialog.askopenfilename(title="Open extracted board archive", filetypes=[("Board archive", "*.bin")])
        if name:
            self._open(lambda: self._load_archive(Path(name)))

    def open_project(self) -> None:
        name = filedialog.askopenfilename(title="Open board project", filetypes=[("Board project", "*.mp4board.json")])
        if name:
            self._open(lambda: self._set_board(*load_project(Path(name)), project=Path(name)))

    def save(self) -> None:
        if not self.spaces or self.original is None:
            return
        target = self.project
        if target is None:
            name = filedialog.asksaveasfilename(defaultextension=".mp4board.json", initialfile=f"{self.board_id}.mp4board.json",
                                                filetypes=[("Board project", "*.mp4board.json")])
            if not name:
                return
            target = Path(name)
        try:
            save_project(target, self.board_id, self.original, self.spaces)
            self.project, self.changed = target, False
            self.status.set(f"Saved editable project: {target}")
        except Exception as error:
            messagebox.showerror("Save failed", str(error))

    def export(self) -> None:
        if not self.spaces or self.original is None:
            return
        try:
            validate(self.spaces)
            if not self.original.is_file():
                raise FileNotFoundError("Original archive missing. Import your disc again, then open this project.")
            original = self.original.read_bytes()
            # Refuse accidental cross-board exports even if a project was hand-edited.
            if self.original.stem.lower() != self.board_id:
                raise ValueError("Project board does not match its original archive")
            output = GAME / "mods" / "board-edits" / "data" / f"{self.board_id}.bin"
            output.parent.mkdir(parents=True, exist_ok=True)
            candidate = replace_board(original, self.spaces)
            if parse_spaces(board_bytes(candidate)) != self.spaces:
                raise ValueError("Export verification failed")
            output.write_bytes(candidate)
            (GAME / "board-mods.txt").write_text(str(output.parent.parent.resolve()) + "\n", encoding="utf-8")
            self.status.set(f"Exported {output}. Launch with Play Edited Boards.cmd to test.")
            messagebox.showinfo("Exported", f"Board override ready:\n{output}\n\nStart with Play Edited Boards.cmd.")
        except Exception as error:
            messagebox.showerror("Export failed", str(error))

    def _record(self) -> None:
        self.undo.append(copy.deepcopy(self.spaces))
        self.undo = self.undo[-100:]
        self.redo.clear()
        self.changed = True

    def _history(self, forward: bool) -> None:
        source, target = (self.redo, self.undo) if forward else (self.undo, self.redo)
        if source:
            target.append(copy.deepcopy(self.spaces))
            self.spaces = source.pop()
            self.changed = True
            self._refresh_fields()
            self.draw()

    def _refresh_fields(self) -> None:
        if self.selected is None or self.selected >= len(self.spaces):
            self.heading.config(text="Select a space")
            for value in self.fields.values():
                value.set("")
            return
        space = self.spaces[self.selected]
        self.heading.config(text=f"Space {self.selected + 1} of {len(self.spaces)}")
        for field, value in zip(("x", "y", "z"), space["pos"]):
            self.fields[field].set(f"{value:.2f}")
        self.fields["type"].set(f'{space["type"]}: {TYPE_NAMES.get(space["type"], "Other")}')
        self.fields["flags"].set(f'0x{space["flags"]:08X}')
        self.fields["links"].set(", ".join(map(str, space["links"])))

    def apply_fields(self) -> None:
        if self.selected is None:
            return
        before = copy.deepcopy(self.spaces)
        try:
            space = self.spaces[self.selected]
            space["pos"] = [float(self.fields[key].get()) for key in ("x", "y", "z")]
            space["type"] = int(self.fields["type"].get().split(":", 1)[0])
            space["flags"] = int(self.fields["flags"].get(), 0)
            space["links"] = [int(part.strip()) for part in self.fields["links"].get().split(",") if part.strip()]
            validate(self.spaces)
        except Exception as error:
            self.spaces = before
            self._refresh_fields()
            messagebox.showerror("Invalid space", str(error))
            return
        if self.spaces != before:
            self.undo.append(before)
            self.redo.clear()
            self.changed = True
            self.draw()

    def _bounds(self) -> None:
        if not self.spaces:
            return
        xs, zs = [s["pos"][0] for s in self.spaces], [s["pos"][2] for s in self.spaces]
        self.center_x, self.center_z = (min(xs) + max(xs)) / 2, (min(zs) + max(zs)) / 2
        self.scale = min((self.canvas.winfo_width() - 100) / max(1, max(xs) - min(xs)),
                         (self.canvas.winfo_height() - 100) / max(1, max(zs) - min(zs)))

    def _screen(self, space: dict) -> tuple[float, float]:
        return (self.canvas.winfo_width() / 2 + (space["pos"][0] - self.center_x) * self.scale,
                self.canvas.winfo_height() / 2 - (space["pos"][2] - self.center_z) * self.scale)

    def draw(self) -> None:
        self.canvas.delete("all")
        if not self.spaces:
            self.canvas.create_text(24, 24, text="Import a board to begin", fill="white", anchor="nw")
            return
        self._bounds()
        for source_id, space in enumerate(self.spaces):
            x, y = self._screen(space)
            for link in space["links"]:
                target_x, target_y = self._screen(self.spaces[link - 1])
                self.canvas.create_line(x, y, target_x, target_y, fill="#8292ad", width=2, arrow="last")
        for index, space in enumerate(self.spaces):
            x, y = self._screen(space)
            radius = 14 if index == self.selected else 10
            self.canvas.create_oval(x-radius, y-radius, x+radius, y+radius,
                                    fill=COLORS.get(space["type"], "#aaaaaa"),
                                    outline="white" if index == self.selected else "#0b1020", width=3,
                                    tags=(f"space-{index}", "space"))
            self.canvas.create_text(x, y-18, text=str(index + 1), fill="white", font=("Segoe UI", 9),
                                    tags=(f"space-{index}", "space"))

    def _hit(self, event) -> int | None:
        for item in reversed(self.canvas.find_overlapping(event.x-8, event.y-8, event.x+8, event.y+8)):
            for tag in self.canvas.gettags(item):
                if tag.startswith("space-"):
                    return int(tag[6:])
        return None

    def _click(self, event) -> None:
        hit = self._hit(event)
        if hit is not None:
            self.selected = hit
            self._refresh_fields()
            self._record()
            self.dragging = True
            self.draw()

    def _drag(self, event) -> None:
        if not self.dragging or self.selected is None:
            return
        space = self.spaces[self.selected]
        space["pos"][0] = round(self.center_x + (event.x - self.canvas.winfo_width()/2) / self.scale, 2)
        space["pos"][2] = round(self.center_z - (event.y - self.canvas.winfo_height()/2) / self.scale, 2)
        self._refresh_fields()
        self.draw()

    def _release(self, _: object) -> None:
        if self.dragging and self.undo and self.undo[-1] == self.spaces:
            self.undo.pop()
        self.dragging = False

    def _close(self) -> None:
        if not self.changed or messagebox.askyesno("Unsaved changes", "Close without saving your project?"):
            self.destroy()


if __name__ == "__main__":
    BoardEditor().mainloop()
