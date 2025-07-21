# -*- coding: utf-8 -*-
import tkinter as tk
import threading

class SuggestEntry:
    def __init__(self, master, candidates, on_select_callback=None):
        self.frame = tk.Frame(master, bg="#181a1b")
        self.entry = tk.Entry(self.frame, width=40, bg="#23272a", fg="#f5f6fa", insertbackground="#f5f6fa")
        self.entry.pack(side=tk.TOP, anchor="w", fill=tk.X, padx=(0, 0), pady=(0, 2))
        self.listbox = tk.Listbox(self.frame, width=40, height=6, bg="#23272a", fg="#f5f6fa", selectbackground="#3a3f4b", selectforeground="#ffffff", highlightbackground="#23272a", highlightcolor="#23272a")
        self.listbox.pack(side=tk.TOP, fill=tk.X, padx=(0, 0), pady=(0, 0))
        self.candidates = candidates
        self._item_placeholder = "アイテム名またはIDを入力"
        self.entry.insert(0, self._item_placeholder)
        self.entry.config(fg="#888a8c")
        self._suggest_thread = None
        self._suggest_cancel = threading.Event()
        self.on_select_callback = on_select_callback
        self._bind_events()

    def _bind_events(self):
        self.entry.bind("<FocusIn>", self._on_focus_in)
        self.entry.bind("<FocusOut>", self._on_focus_out)
        self.entry.bind('<KeyRelease>', self.update_suggest_list)
        self.listbox.bind('<<ListboxSelect>>', self._on_suggest_select)
        self.listbox.bind('<ButtonRelease-1>', self._on_suggest_select)

    def _on_focus_in(self, event):
        if self.entry.get() == self._item_placeholder:
            self.entry.delete(0, tk.END)
            self.entry.config(fg="#f5f6fa")

    def _on_focus_out(self, event):
        if not self.entry.get():
            self.entry.insert(0, self._item_placeholder)
            self.entry.config(fg="#888a8c")

    def update_suggest_list(self, event=None):
        if self._suggest_thread and self._suggest_thread.is_alive():
            self._suggest_cancel.set()
            self._suggest_thread.join(timeout=0.1)
        self._suggest_cancel.clear()
        current = self.entry.get()
        words = [w for w in current.lower().split() if w]
        all_values = self.candidates[:]
        def worker():
            if words:
                filtered = [v for v in all_values if all(word in v.lower() for word in words)]
                def sort_key(v):
                    v_lower = v.lower()
                    joined = " ".join(words)
                    if v_lower == joined:
                        return (0, 0, v_lower)
                    if all(v_lower.find(word) == 0 for word in words):
                        return (1, 0, v_lower)
                    if all(word in v_lower for word in words):
                        total_idx = sum(v_lower.find(word) for word in words)
                        return (2, total_idx, v_lower)
                    return (3, 9999, v_lower)
                values = sorted(filtered, key=sort_key)
            else:
                values = all_values
            if self._suggest_cancel.is_set():
                return
            def update_listbox():
                self.listbox.delete(0, tk.END)
                for v in values:
                    self.listbox.insert(tk.END, v)
            self.frame.after(0, update_listbox)
        self._suggest_thread = threading.Thread(target=worker, daemon=True)
        self._suggest_thread.start()

    def _on_suggest_select(self, event):
        if self.listbox.curselection():
            val = self.listbox.get(self.listbox.curselection()[0])
            self.entry.delete(0, tk.END)
            self.entry.insert(0, val)
            if self.on_select_callback:
                self.on_select_callback(val)

    def get(self):
        return self.entry.get()

    def set_candidates(self, candidates):
        self.candidates = candidates
        self.update_suggest_list()

    def pack(self, **kwargs):
        self.frame.pack(**kwargs)

    def bind(self, sequence, func):
        self.entry.bind(sequence, func)

    def delete(self, start, end):
        self.entry.delete(start, end)

    def insert(self, index, value):
        self.entry.insert(index, value)

    def config(self, **kwargs):
        self.entry.config(**kwargs)
