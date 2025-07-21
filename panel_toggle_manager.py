class PanelToggleManager:
    def __init__(self, panel_dict, toggle_button=None, show_text="表示", hide_text="非表示"):
        self.panel_dict = panel_dict  # {name: panel_widget}
        self.toggle_button = toggle_button
        self.show_text = show_text
        self.hide_text = hide_text
        self.state = True  # True: shown, False: hidden

    def toggle_panel(self, *panel_names):
        # 指定パネルをトグル
        for name in panel_names:
            panel = self.panel_dict.get(name)
            if panel:
                if panel.winfo_ismapped():
                    panel.pack_forget()
                else:
                    panel.pack(pady=4, fill="x", expand=True)
        self.state = not self.state
        if self.toggle_button:
            self.toggle_button.config(text=self.show_text if not self.state else self.hide_text)

    def set_button(self, button):
        self.toggle_button = button

    def is_shown(self):
        return self.state
