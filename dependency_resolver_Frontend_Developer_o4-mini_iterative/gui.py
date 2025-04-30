"""
gui.py

A simple Tkinter-based GUI for managing packages.
"""

import tkinter as tk
from tkinter import ttk, messagebox
from package_manager.registry import Registry
from package_manager.manager import PackageManager


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
        ver = self.version_var.get().strip()
        ver_spec = ver or None
        pkgs = self.registry.search(name, ver_spec)
        self.results.delete(0, tk.END)
        for pkg in pkgs:
            display = f"{pkg.name}=={pkg.metadata.version}"
            self.results.insert(tk.END, display)

    def on_select(self, event):
        sel = self.results.curselection()
        if not sel:
            return
        text = self.results.get(sel[0])
        name, version = text.split("==")
        metadata = self.registry.get_metadata(name, version)
        self.meta_text.delete("1.0", tk.END)
        if metadata:
            info = f"Name: {name}\nVersion: {metadata.version}\nDependencies:\n"
            for d in metadata.dependencies:
                info += f"  - {d}\n"
            self.meta_text.insert(tk.END, info)

    def on_pin(self):
        sel = self.results.curselection()
        if not sel:
            messagebox.showinfo("Info", "Select a package first.")
            return
        text = self.results.get(sel[0])
        name, version = text.split("==")
        try:
            self.manager.pin(name, version)
            messagebox.showinfo("Pinned", f"Pinned {name}=={version}")
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def on_unpin(self):
        sel = self.results.curselection()
        if not sel:
            messagebox.showinfo("Info", "Select a package first.")
            return
        text = self.results.get(sel[0])
        name, _ = text.split("==")
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
