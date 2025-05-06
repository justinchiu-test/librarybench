"""
gui.py

A simple Tkinter-based GUI for managing packages.
"""

import tkinter as tk
from tkinter import ttk, messagebox
from package_manager.registry import Registry
from package_manager.manager import PackageManager
from utils import (
    format_pkg_display,
    get_selected_pkg,
    build_metadata_text
)

class PackageGUI:
    def __init__(self):
        self.registry = Registry()
        self.manager = PackageManager(self.registry)

        self.root = tk.Tk()
        self.root.title("Dependency Manager")

        # Search Frame
        sf = ttk.Frame(self.root, padding=10)
        sf.pack(fill=tk.X)
        ttk.Label(sf, text="Search:").pack(side=tk.LEFT)
        self.search_var = tk.StringVar()
        ttk.Entry(sf, textvariable=self.search_var, width=30).pack(side=tk.LEFT, padx=5)
        self.version_var = tk.StringVar()
        ttk.Entry(sf, textvariable=self.version_var, width=15).pack(side=tk.LEFT, padx=5)
        ttk.Button(sf, text="Search", command=self.on_search).pack(side=tk.LEFT)

        # Results Frame
        rf = ttk.Frame(self.root, padding=10)
        rf.pack(fill=tk.BOTH, expand=True)
        self.results = tk.Listbox(rf, height=10)
        self.results.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.results.bind("<<ListboxSelect>>", self.on_select)
        scrollbar = ttk.Scrollbar(rf, orient=tk.VERTICAL, command=self.results.yview)
        scrollbar.pack(side=tk.LEFT, fill=tk.Y)
        self.results.config(yscrollcommand=scrollbar.set)

        # Metadata & Pin Frame
        mf = ttk.Frame(self.root, padding=10)
        mf.pack(fill=tk.BOTH, expand=True)
        self.meta_text = tk.Text(mf, height=8)
        self.meta_text.pack(fill=tk.BOTH, expand=True)
        btn_frame = ttk.Frame(mf)
        btn_frame.pack(fill=tk.X, pady=5)
        ttk.Button(btn_frame, text="Pin", command=self.on_pin).pack(side=tk.LEFT)
        ttk.Button(btn_frame, text="Unpin", command=self.on_unpin).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Show Pins", command=self.on_show_pins).pack(side=tk.LEFT)

    def on_search(self):
        name = self.search_var.get().strip()
        ver = self.version_var.get().strip() or None
        pkgs = self.registry.search(name, ver)
        self.results.delete(0, tk.END)
        for pkg in pkgs:
            self.results.insert(tk.END, format_pkg_display(pkg))

    def on_select(self, event):
        name, version = get_selected_pkg(self.results)
        if not name:
            return
        metadata = self.registry.get_metadata(name, version)
        self.meta_text.delete("1.0", tk.END)
        if metadata:
            info = build_metadata_text(name, metadata)
            self.meta_text.insert(tk.END, info)

    def on_pin(self):
        name, version = get_selected_pkg(self.results)
        if not name:
            messagebox.showinfo("Info", "Select a package first.")
            return
        try:
            self.manager.pin(name, version)
            messagebox.showinfo("Pinned", f"Pinned {name}=={version}")
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def on_unpin(self):
        name, _ = get_selected_pkg(self.results)
        if not name:
            messagebox.showinfo("Info", "Select a package first.")
            return
        self.manager.unpin(name)
        messagebox.showinfo("Unpinned", f"Unpinned {name}")

    def on_show_pins(self):
        pins = self.manager.list_pins()
        if not pins:
            messagebox.showinfo("Pins", "No packages pinned.")
            return
        info = "\n".join(f"{n}=={v}" for n, v in pins.items())
        messagebox.showinfo("Pinned Packages", info)

    def run(self):
        self.root.mainloop()


if __name__ == "__main__":
    gui = PackageGUI()
    gui.run()
