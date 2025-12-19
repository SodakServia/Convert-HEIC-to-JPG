# Convert HEIC to JPG

Simple Windows-friendly Tkinter app to convert multiple `.heic` / `.heif` images to `.jpg` at once. Successful conversions remove the original HEIC files so you end up with only JPEGs.

## Setup

1. Install dependencies (Python 3.10+):
   ```bash
   pip install -r requirements.txt
   ```

2. Run the app:
   ```bash
   python convert_heic_to_jpg.py
   ```
   - Windows shortcut: double-click `run_converter.bat` (after installing dependencies).
   - To build a standalone `.exe`, run `build_windows_exe.bat` (requires Python on PATH).

## Usage

1. Click **Choose Files** to pick individual HEIC/HEIF images, or **Choose Folder** to load all HEIC/HEIF files from a directory.
2. Click **Convert** to start converting. The app converts files concurrently and shows progress.
3. After each file is converted to JPG, the original HEIC file is removed automatically.

## Notes

- Conversion is limited to `.heic` / `.heif` extensions.
- The app uses [pillow-heif](https://pypi.org/project/pillow-heif/) to decode HEIC and Pillow to write JPGs.
- The packaged `.exe` produced by `build_windows_exe.bat` lives in `dist/heic_to_jpg.exe` and can be pinned to the Start menu or taskbar.
