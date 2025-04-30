import tkinter as tk
from tkinter import simpledialog, messagebox
from env_manager import EnvironmentManager

class GUIManager:
    def __init__(self, master, manager: EnvironmentManager):
        self.master = master
        self.manager = manager
        master.title("Environment Manager")

        # Environment selector
        self.env_var = tk.StringVar(master)
        current = self.manager.get_current_env()
        self.env_var.set(current if current else "Select...")
        self.env_menu = tk.OptionMenu(
            master, self.env_var, *self.manager.list_envs(), command=self._switch
        )
        self.env_menu.pack(pady=5)

        # Package listbox
        self.pkg_list = tk.Listbox(master, width=40)
        self.pkg_list.pack(pady=5)

        # Buttons
        btn_frame = tk.Frame(master)
        btn_frame.pack(pady=5)
        tk.Button(btn_frame, text="Add Package", command=self._add).grid(row=0, column=0, padx=5)
        tk.Button(btn_frame, text="Remove Package", command=self._remove).grid(row=0, column=1, padx=5)
        tk.Button(btn_frame, text="Lockfile", command=self._lock).grid(row=0, column=2, padx=5)
        tk.Button(btn_frame, text="Check Vulns", command=self._vulns).grid(row=0, column=3, padx=5)

        self.status = tk.Label(master, text="")
        self.status.pack(pady=5)

        self._refresh()

    def _switch(self, choice):
        try:
            self.manager.switch_env(choice)
            self.status.config(text=f"Switched to '{choice}'")
            self._refresh()
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def _refresh(self):
        self.pkg_list.delete(0, tk.END)
        env = self.manager.get_current_env()
        if not env:
            return
        data = self.manager._load_env(env)
        for pkg, ver in data["packages"].items():
            self.pkg_list.insert(tk.END, f"{pkg}=={ver}")

    def _add(self):
        if not self.manager.get_current_env():
            messagebox.showerror("Error", "No environment selected")
            return
        pkg = simpledialog.askstring("Package", "Name:")
        ver = simpledialog.askstring("Version", "Version:")
        if pkg and ver:
            try:
                self.manager.install_package(pkg, ver)
                self.status.config(text=f"Added {pkg}=={ver}")
                self._refresh()
            except Exception as e:
                messagebox.showerror("Error", str(e))

    def _remove(self):
        sel = self.pkg_list.curselection()
        if not sel:
            return
        entry = self.pkg_list.get(sel[0])
        pkg = entry.split("==")[0]
        try:
            self.manager.remove_package(pkg)
            self.status.config(text=f"Removed {pkg}")
            self._refresh()
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def _lock(self):
        try:
            self.manager.generate_lockfile()
            self.status.config(text="Lockfile generated")
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def _vulns(self):
        try:
            alerts = self.manager.alert_vulnerabilities()
            if alerts:
                msg = "\n".join(f"{a['name']}=={a['version']} is vulnerable" for a in alerts)
                messagebox.showwarning("Vulnerabilities", msg)
            else:
                messagebox.showinfo("Vulnerabilities", "No vulnerabilities found")
        except Exception as e:
            messagebox.showerror("Error", str(e))

# Script entry point (optional)
if __name__ == "__main__":
    root = tk.Tk()
    mgr = EnvironmentManager()
    GUIManager(root, mgr)
    root.mainloop()
