import tkinter as tk
from tkinter import simpledialog, messagebox
from Full_Stack_Developer.env_manager import EnvironmentManager

class GUIManager:
    def __init__(self, master, manager: EnvironmentManager):
        self.master = master
        self.manager = manager
        master.title("Environment Manager")

        self.env_var = tk.StringVar(master)
        current = manager.get_current_env() or "Select..."
        self.env_var.set(current)
        self.env_menu = tk.OptionMenu(
            master, self.env_var, *manager.list_envs(), command=self._switch
        )
        self.env_menu.pack(pady=5)

        self.pkg_list = tk.Listbox(master, width=40)
        self.pkg_list.pack(pady=5)

        btns = [
            ("Add Package", self._add),
            ("Remove Package", self._remove),
            ("Lockfile", self._lock),
            ("Check Vulns", self._vulns),
        ]
        frame = tk.Frame(master)
        frame.pack(pady=5)
        for i, (txt, cmd) in enumerate(btns):
            tk.Button(frame, text=txt, command=cmd).grid(row=0, column=i, padx=5)

        self.status = tk.Label(master, text="")
        self.status.pack(pady=5)
        self._refresh()

    def _exec(self, func, *args, message=None):
        try:
            func(*args)
            if message:
                self.status.config(text=message)
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def _switch(self, choice):
        self._exec(self.manager.switch_env, choice, message=f"Switched to '{choice}'")
        self._refresh()

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
            self._exec(self.manager.install_package, pkg, ver, message=f"Added {pkg}=={ver}")
            self._refresh()

    def _remove(self):
        sel = self.pkg_list.curselection()
        if not sel:
            return
        pkg = self.pkg_list.get(sel[0]).split("==")[0]
        self._exec(self.manager.remove_package, pkg, message=f"Removed {pkg}")
        self._refresh()

    def _lock(self):
        self._exec(self.manager.generate_lockfile, message="Lockfile generated")

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
