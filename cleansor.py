import tempfile
from pathlib import Path
from datetime import datetime, timedelta
import tkinter as tk
from tkinter import messagebox, simpledialog, ttk

def get_temp_folder():
    return Path(tempfile.gettempdir())

def scan_temp_files(temp_dir):
    files = []
    for file in temp_dir.rglob("*"):
        if file.is_file():
            try:
                size = file.stat().st_size
                mtime = datetime.fromtimestamp(file.stat().st_mtime)
                files.append((file, size, mtime))
            except Exception:
                pass
    return files

def format_size(size_bytes):
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size_bytes < 1024:
            return f"{size_bytes:.2f} {unit}"
        size_bytes /= 1024
    return f"{size_bytes:.2f} TB"

def delete_files(files_to_delete):
    total_deleted = 0
    failed = []
    for file, size, _ in files_to_delete:
        try:
            file.unlink()
            total_deleted += size
        except Exception:
            failed.append(str(file))
    return total_deleted, failed

class TempCleanerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("🧹 Temp Folder Cleaner")
        self.temp_dir = get_temp_folder()
        self.files = scan_temp_files(self.temp_dir)
        self.files.sort(key=lambda x: x[1], reverse=True)

        self.setup_ui()
        self.refresh_summary()

    def setup_ui(self):
        self.frame = tk.Frame(self.root, padx=10, pady=10)
        self.frame.pack()

        self.summary_label = tk.Label(self.frame, text="Scanning...")
        self.summary_label.pack()

        btn_top = tk.Button(self.frame, text="Delete Top N Largest Files", command=self.delete_top_n)
        btn_top.pack(fill="x", pady=5)

        btn_old = tk.Button(self.frame, text="Delete Files Older Than N Days", command=self.delete_old)
        btn_old.pack(fill="x", pady=5)

        btn_all = tk.Button(self.frame, text="Delete ALL Temp Files", command=self.delete_all)
        btn_all.pack(fill="x", pady=5)

        btn_refresh = tk.Button(self.frame, text="🔄 Refresh", command=self.refresh_data)
        btn_refresh.pack(fill="x", pady=5)

        self.file_listbox = tk.Listbox(self.frame, width=80, height=12)
        self.file_listbox.pack(pady=5)

    def refresh_data(self):
        self.files = scan_temp_files(self.temp_dir)
        self.files.sort(key=lambda x: x[1], reverse=True)
        self.refresh_summary()

    def refresh_summary(self):
        total_size = sum(size for _, size, _ in self.files)
        self.summary_label.config(text=f"📁 Temp folder: {self.temp_dir}\n📦 Total size: {format_size(total_size)} | Files: {len(self.files)}")
        self.file_listbox.delete(0, tk.END)
        for i, (file, size, _) in enumerate(self.files[:10]):
            self.file_listbox.insert(tk.END, f"{i+1:2d}. {file.name} - {format_size(size)} - {file}")

    def delete_top_n(self):
        n = simpledialog.askinteger("Top N", "Delete how many of the largest files?", minvalue=1, maxvalue=len(self.files))
        if n:
            to_delete = self.files[:n]
            deleted_size, failed = delete_files(to_delete)
            self.refresh_data()
            messagebox.showinfo("Deleted", f"✅ Deleted {n} files.\n💾 Freed: {format_size(deleted_size)}\n⚠️ Failed: {len(failed)}")

    def delete_old(self):
        days = simpledialog.askinteger("Older Than", "Delete files older than how many days?", minvalue=1)
        if days:
            cutoff = datetime.now() - timedelta(days=days)
            old_files = [f for f in self.files if f[2] < cutoff]
            deleted_size, failed = delete_files(old_files)
            self.refresh_data()
            messagebox.showinfo("Deleted", f"✅ Deleted {len(old_files)} files older than {days} days.\n💾 Freed: {format_size(deleted_size)}\n⚠️ Failed: {len(failed)}")

    def delete_all(self):
        confirm = messagebox.askyesno("Confirm", "⚠️ Are you sure you want to delete ALL files in the temp folder?")
        if confirm:
            deleted_size, failed = delete_files(self.files)
            self.refresh_data()
            messagebox.showinfo("Deleted", f"✅ Deleted all temp files.\n💾 Freed: {format_size(deleted_size)}\n⚠️ Failed: {len(failed)}")

if __name__ == "__main__":
    root = tk.Tk()
    app = TempCleanerApp(root)
    root.mainloop()
