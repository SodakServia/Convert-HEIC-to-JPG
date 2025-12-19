from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
import threading
import tkinter as tk
from tkinter import filedialog, messagebox, ttk

from PIL import Image
import pillow_heif


def is_heic(path: Path) -> bool:
    return path.suffix.lower() in {".heic", ".heif"}


def convert_heic_to_jpg(heic_path: Path) -> tuple[Path, bool, str | None]:
    target_path = heic_path.with_suffix(".jpg")
    pillow_heif.register_heif_opener()
    try:
        with Image.open(heic_path) as img:
            rgb_image = img.convert("RGB")
            rgb_image.save(target_path, format="JPEG", quality=95, optimize=True)
        heic_path.unlink(missing_ok=True)
        return target_path, True, None
    except Exception as exc:  # noqa: BLE001
        return target_path, False, str(exc)


class ConverterApp(tk.Tk):
    def __init__(self) -> None:
        super().__init__()
        self.title("HEIC to JPG Converter")
        self.geometry("500x320")
        self.resizable(False, False)
        self.files: list[Path] = []
        self._lock = threading.Lock()

        self._build_ui()

    def _build_ui(self) -> None:
        padding = {"padx": 12, "pady": 8}

        description = (
            "Select .heic/.heif files to convert them to .jpg. "
            "Original HEIC files will be removed after successful conversion."
        )
        ttk.Label(self, text=description, wraplength=460, justify="left").pack(**padding, anchor="w")

        button_frame = ttk.Frame(self)
        button_frame.pack(fill="x", **padding)

        ttk.Button(button_frame, text="Choose Files", command=self._choose_files).pack(side="left")
        ttk.Button(button_frame, text="Choose Folder", command=self._choose_folder).pack(side="left", padx=8)
        self.convert_button = ttk.Button(button_frame, text="Convert", command=self._start_conversion, state="disabled")
        self.convert_button.pack(side="right")

        self.status_var = tk.StringVar(value="No files selected.")
        ttk.Label(self, textvariable=self.status_var).pack(**padding, anchor="w")

        self.progress = ttk.Progressbar(self, mode="determinate", length=460)
        self.progress.pack(**padding)

        self.log_box = tk.Text(self, height=8, width=64, state="disabled", wrap="word")
        self.log_box.pack(**padding)

    def _choose_files(self) -> None:
        selected = filedialog.askopenfilenames(
            title="Select HEIC files", filetypes=[("HEIC Images", "*.heic *.heif"), ("All files", "*.*")]
        )
        paths = [Path(path) for path in selected if is_heic(Path(path))]
        self._update_file_list(paths)

    def _choose_folder(self) -> None:
        folder = filedialog.askdirectory(title="Select folder containing HEIC files")
        if not folder:
            return
        root = Path(folder)
        paths = [path for path in root.iterdir() if path.is_file() and is_heic(path)]
        self._update_file_list(paths)

    def _update_file_list(self, paths: list[Path]) -> None:
        unique_paths = {path.resolve() for path in paths if path.exists()}
        with self._lock:
            self.files = sorted(unique_paths)
        count = len(self.files)
        self.status_var.set(f"{count} file{'s' if count != 1 else ''} ready for conversion.")
        self.convert_button.config(state="normal" if count else "disabled")
        self._log(f"Selected {count} file(s).")
        self.progress["value"] = 0
        self.progress["maximum"] = max(count, 1)

    def _start_conversion(self) -> None:
        with self._lock:
            files_to_process = list(self.files)
        if not files_to_process:
            messagebox.showinfo("No files", "Please select HEIC files to convert.")
            return
        self.convert_button.config(state="disabled")
        self.progress["value"] = 0
        thread = threading.Thread(target=self._convert_files, args=(files_to_process,), daemon=True)
        thread.start()

    def _convert_files(self, files: list[Path]) -> None:
        successes = 0
        errors: list[str] = []

        with ThreadPoolExecutor(max_workers=min(8, len(files) or 1)) as executor:
            future_to_file = {executor.submit(convert_heic_to_jpg, path): path for path in files}
            for future in as_completed(future_to_file):
                heic_path = future_to_file[future]
                target, ok, err = future.result()
                if ok:
                    successes += 1
                    self._log(f"Converted: {heic_path.name} -> {target.name}")
                else:
                    errors.append(f"{heic_path.name}: {err}")
                    self._log(f"Failed: {heic_path.name} ({err})")
                self._increment_progress()

        summary = f"Conversion complete. {successes}/{len(files)} succeeded."
        if errors:
            summary += f" {len(errors)} file(s) failed."
        self.status_var.set(summary)
        self.convert_button.config(state="normal")
        if errors:
            messagebox.showwarning("Conversion completed with errors", "\n".join(errors))
        else:
            messagebox.showinfo("Conversion complete", summary)

    def _increment_progress(self) -> None:
        self.progress["value"] += 1

    def _log(self, message: str) -> None:
        self.log_box.config(state="normal")
        self.log_box.insert("end", f"{message}\n")
        self.log_box.see("end")
        self.log_box.config(state="disabled")


if __name__ == "__main__":
    app = ConverterApp()
    app.mainloop()
