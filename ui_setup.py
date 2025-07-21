import tkinter as tk
from constants import COLUMNS, COLUMN_LABELS, COLUMN_WIDTHS, COLUMN_ANCHORS
from theme_utils import set_dark_theme
from utils import load_items_json

def setup_ui(app):
    app.title("マーケット情報 - NotificationMarket")
    app.geometry("1100x600")
    app.configure(bg="#181a1b")
    from file_manager import SettingsManager, SearchConditionManager
    app.settings_manager = SettingsManager()
    app.settings = app.settings_manager.settings
    app.search_cond_manager = SearchConditionManager()
    app.search_conditions = app.search_cond_manager.conditions
    app.excluded_itemids = set()
    from order_condition_manager import OrderConditionManager
    app.condition_manager = OrderConditionManager(app.search_conditions, app.excluded_itemids)
    app.last_update_var = tk.StringVar()
    app.max_display_var = tk.IntVar(value=app.settings.get('max_display', 50))
    set_dark_theme(app)
    columns = COLUMNS
    app.lbl_last_update = tk.Label(app, textvariable=app.last_update_var, anchor="w", bg="#181a1b", fg="#f5f6fa")
    app.lbl_last_update.pack(anchor="nw", padx=8, pady=(8,0))

    app.frm_maxdisp = tk.Frame(app, bg="#181a1b")
    app.frm_maxdisp.pack(fill=tk.X, padx=8, pady=(0, 0))
    tk.Label(app.frm_maxdisp, text="最大件数", bg="#181a1b", fg="#f5f6fa").pack(side=tk.LEFT, padx=(0, 2))
    ent_maxdisp = tk.Entry(app.frm_maxdisp, textvariable=app.max_display_var, width=5, bg="#23272a", fg="#f5f6fa", insertbackground="#f5f6fa")
    ent_maxdisp.pack(side=tk.LEFT, padx=(0, 8))
    ent_maxdisp.bind("<FocusOut>", app.on_max_display_changed)
    ent_maxdisp.bind("<Return>", app.on_max_display_changed)

    app.tree = tk.ttk.Treeview(app, columns=columns, show="headings", style="Treeview")
    for col in columns:
        app.tree.heading(col, text=COLUMN_LABELS.get(col, col))
        anchor = COLUMN_ANCHORS.get(col, None)
        if anchor:
            app.tree.column(col, width=COLUMN_WIDTHS.get(col, 100), anchor=anchor)
        else:
            app.tree.column(col, width=COLUMN_WIDTHS.get(col, 100))
    app.tree.pack(fill=tk.BOTH, expand=True, padx=4, pady=0)

    items = load_items_json()
    app.item_candidates = [
        f"{item['name']} (Tier{item.get('tier', item.get('itemTier', '?'))}/{item.get('rarity', item.get('itemRarityStr', '?'))}) ({item['id']})"
        for item in items
    ]
    import re
    def extract_itemid(candidate):
        m = re.search(r'\((\d+)\)$', candidate)
        from treeview_manager import TreeViewManager
        app.treeview_manager = TreeViewManager(app.tree, app.last_update_var)
        return m.group(1) if m else ''
    app.itemid_map = {c: extract_itemid(c) for c in app.item_candidates}

    app.frm_top = tk.Frame(app, bg="#181a1b")
    app.frm_top.pack(pady=0, fill=tk.X, expand=True)

    app.frm_add_conditions = tk.Frame(app.frm_top, bg="#181a1b")
    app.frm_add_conditions.pack(side=tk.LEFT, padx=(0, 8), fill=tk.X)

    app.frm_inputs = tk.Frame(app.frm_add_conditions, bg="#181a1b")
    app.frm_inputs.pack(side=tk.TOP, fill=tk.X)

    from suggest_entry import SuggestEntry
    def on_suggest_selected(val):
        app.selected_itemid = app.itemid_map.get(val, "")
    app.suggest_entry = SuggestEntry(app.frm_inputs, app.item_candidates, on_select_callback=on_suggest_selected)
    app.suggest_entry.pack(side=tk.LEFT, fill=tk.Y)
    app.ent_item = app.suggest_entry.entry
    app.listbox_suggest = app.suggest_entry.listbox

    from price_quantity_form import PriceQuantityForm
    app.priceqty_form = PriceQuantityForm(app.frm_inputs)
    app.priceqty_form.pack(side=tk.LEFT, fill=tk.Y)
    app.ent_minprice = app.priceqty_form.ent_minprice
    app.ent_maxprice = app.priceqty_form.ent_maxprice
    app.ent_minqty = app.priceqty_form.ent_minqty
    app.ent_maxqty = app.priceqty_form.ent_maxqty

    app.frm_add_btn = tk.Frame(app.frm_add_conditions, bg="#181a1b")
    app.frm_add_btn.pack(side=tk.TOP, fill=tk.X, pady=(8, 0))
    btn_add = tk.Button(app.frm_add_btn, text="追加・変更", width=20, command=app.add_condition, bg="#23272a", fg="#f5f6fa", activebackground="#2c2f33", activeforeground="#ffffff")
    btn_add.pack(side=tk.TOP, fill=tk.X, padx=(0, 0), pady=(0, 0))

    app.frm_conditions_btn = tk.Frame(app.frm_top, bg="#181a1b")
    app.frm_conditions_btn.pack(side=tk.TOP, fill=tk.X, padx=(0, 8), pady=(4, 0))
    btn_del = tk.Button(app.frm_conditions_btn, text="削除", command=app.del_condition, bg="#23272a", fg="#f5f6fa", activebackground="#2c2f33", activeforeground="#ffffff")
    btn_del.pack(side=tk.LEFT, padx=(0, 4))
    btn_exclude = tk.Button(app.frm_conditions_btn, text="除外", command=app.exclude_condition, bg="#23272a", fg="#f5f6fa", activebackground="#2c2f33", activeforeground="#ffffff")
    btn_exclude.pack(side=tk.LEFT, padx=(0, 4))
    btn_clear = tk.Button(app.frm_conditions_btn, text="選択解除", command=app.clear_condition_form, bg="#23272a", fg="#f5f6fa", activebackground="#2c2f33", activeforeground="#ffffff")
    btn_clear.pack(side=tk.LEFT, padx=(0, 4))
    btn_reload = tk.Button(app.frm_conditions_btn, text="リロード", command=app.reload_conditions, bg="#23272a", fg="#f5f6fa", activebackground="#2c2f33", activeforeground="#ffffff")
    btn_reload.pack(side=tk.LEFT, padx=(0, 4))
    app.frm_condition = tk.Frame(app.frm_top, bg="#181a1b")
    app.frm_condition.pack(side=tk.TOP, fill=tk.X, padx=(0, 8), pady=(0, 4))

    app.lst_conditions = tk.Listbox(app.frm_condition, width=57, height=6, bg="#23272a", fg="#f5f6fa", selectbackground="#0074D9", selectforeground="#f5f6fa", highlightbackground="#23272a", highlightcolor="#23272a", activestyle='none')
    app.lst_conditions.pack(side=tk.TOP, fill=tk.X, padx=0, pady=4)
    app.lst_conditions.bind("<<ListboxSelect>>", app.on_condition_selected)
    app.lst_conditions.bind("<Double-Button-1>", app.on_condition_double_click)

    from panel_toggle_manager import PanelToggleManager
    app.panel_toggle_mgr = PanelToggleManager({
        "frm_top": app.frm_top,
        "frm_condition": app.frm_condition
    })
    app.btn_toggle_condition = tk.Button(app, text="条件パネル非表示", bg="#23272a", fg="#f5f6fa", activebackground="#2c2f33", activeforeground="#ffffff")
    app.btn_toggle_condition.pack(side=tk.BOTTOM, fill=tk.X, pady=(4, 0))
    app.panel_toggle_mgr.set_button(app.btn_toggle_condition)
    app.btn_toggle_condition.config(command=lambda: app.panel_toggle_mgr.toggle_panel("frm_top", "frm_condition"))

    app.after(0, app.update_market)
    app.update_condition_listbox()
