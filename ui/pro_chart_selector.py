# pro_chart_selector.py - Professional Chart Selection Dialog
"""
Modern, professional chart selection interface with categories,
search, and visual previews.
"""

import tkinter as tk
from tkinter import ttk
from ui.theme_colors import LightPremiumTheme as T


class ProChartSelector:
    """Professional chart selector with modern UI"""
    
    # Chart definitions with categories and descriptions
    CHARTS = {
        "Core Analysis": [
            {
                "id": "portfolio",
                "name": "Portfolio Performance",
                "desc": "Cumulative returns vs benchmarks over time",
                "icon": "📊",
                "default": True
            },
            {
                "id": "risk_metrics",
                "name": "Risk Metrics Dashboard",
                "desc": "Comprehensive risk analysis (volatility, drawdowns, VaR)",
                "icon": "⚠️",
                "default": True
            },
            {
                "id": "benchmarks",
                "name": "Benchmark Comparison",
                "desc": "Performance comparison with selected benchmarks",
                "icon": "📈",
                "default": True
            }
        ],
        "Sector Analysis": [
            {
                "id": "sector",
                "name": "Sector Allocation",
                "desc": "Current sector breakdown and diversification",
                "icon": "🏢",
                "default": True
            },
            {
                "id": "sector_projection",
                "name": "Sector Projections",
                "desc": "Monte Carlo projections by sector",
                "icon": "🎯",
                "default": False
            }
        ],
        "Advanced Analysis": [
            {
                "id": "monte_carlo",
                "name": "Monte Carlo Simulation",
                "desc": "Probabilistic portfolio projections",
                "icon": "🎲",
                "default": True
            },
            {
                "id": "regime",
                "name": "Market Regime Analysis",
                "desc": "Portfolio behavior in different market conditions",
                "icon": "🌊",
                "default": True
            }
        ],
        "Additional Charts": [
            {
                "id": "correlation",
                "name": "Correlation Matrix",
                "desc": "Asset correlation heatmap",
                "icon": "🔗",
                "default": False
            },
            {
                "id": "efficient_frontier",
                "name": "Efficient Frontier",
                "desc": "Optimal risk-return combinations",
                "icon": "📐",
                "default": False
            },
            {
                "id": "rolling_metrics",
                "name": "Rolling Statistics",
                "desc": "Time-varying risk metrics",
                "icon": "📉",
                "default": False
            }
        ]
    }
    
    def __init__(self, parent, chart_vars):
        """
        Initialize professional chart selector
        
        Args:
            parent: Parent window
            chart_vars: Dictionary to store chart selection state
        """
        self.parent = parent
        self.chart_vars = chart_vars
        self.search_var = tk.StringVar()
        self.search_var.trace_add("write", self._on_search)
        
        # Initialize chart variables if not exists
        self._initialize_chart_vars()
        
        # Create dialog
        self._create_dialog()
        
    def _initialize_chart_vars(self):
        """Initialize chart variables with defaults"""
        for category, charts in self.CHARTS.items():
            for chart in charts:
                chart_id = chart["id"]
                if chart_id not in self.chart_vars:
                    self.chart_vars[chart_id] = tk.BooleanVar(value=chart["default"])
    
    def _create_dialog(self):
        """Create the chart selector dialog"""
        self.dialog = tk.Toplevel(self.parent)
        self.dialog.title("Chart Selection - Professional")
        self.dialog.geometry("900x700")
        self.dialog.transient(self.parent)
        self.dialog.grab_set()
        self.dialog.resizable(False, False)
        
        # Center dialog
        self.dialog.update_idletasks()
        x = (self.dialog.winfo_screenwidth() // 2) - (self.dialog.winfo_width() // 2)
        y = (self.dialog.winfo_screenheight() // 2) - (self.dialog.winfo_height() // 2)
        self.dialog.geometry(f"+{x}+{y}")
        
        # Create components
        self._create_header()
        self._create_toolbar()
        self._create_content()
        self._create_footer()
        
    def _create_header(self):
        """Create dialog header"""
        header = tk.Frame(self.dialog, bg=T.HEADER, height=80)
        header.pack(fill=tk.X)
        header.pack_propagate(False)
        
        tk.Label(
            header,
            text="📊 Select Analysis Charts",
            font=("Segoe UI", 16, "bold"),
            bg=T.HEADER,
            fg=T.TEXT_ON_DARK
        ).pack(side=tk.LEFT, padx=20, pady=(15, 5))
        
        # Selection counter
        self.selection_label = tk.Label(
            header,
            text="7 charts selected",
            font=("Segoe UI", 10),
            bg=T.HEADER,
            fg=T.TEXT_SECONDARY
        )
        self.selection_label.pack(side=tk.RIGHT, padx=20)
        
        tk.Label(
            header,
            text="Choose which charts to generate for your portfolio analysis",
            font=("Segoe UI", 10),
            bg=T.HEADER,
            fg=T.TEXT_SECONDARY
        ).pack(side=tk.LEFT, padx=(20, 0), pady=(0, 15), anchor="w")
        
    def _create_toolbar(self):
        """Create toolbar with search and quick actions"""
        toolbar = tk.Frame(self.dialog, bg=T.MAIN_BG, height=60)
        toolbar.pack(fill=tk.X, padx=20, pady=(15, 0))
        toolbar.pack_propagate(False)
        
        # Search box
        search_frame = tk.Frame(toolbar, bg=T.MAIN_BG)
        search_frame.pack(side=tk.LEFT, fill=tk.Y)
        
        tk.Label(
            search_frame,
            text="🔍",
            font=("Segoe UI", 14),
            bg=T.MAIN_BG
        ).pack(side=tk.LEFT, padx=(0, 5))
        
        search_entry = tk.Entry(
            search_frame,
            textvariable=self.search_var,
            width=30,
            font=("Segoe UI", 10),
            bg=T.INPUT_BG,
            fg=T.TEXT_PRIMARY,
            relief=tk.FLAT,
            bd=2
        )
        search_entry.pack(side=tk.LEFT)
        search_entry.insert(0, "Search charts...")
        search_entry.bind("<FocusIn>", lambda e: search_entry.delete(0, tk.END) if search_entry.get() == "Search charts..." else None)
        
        # Quick actions
        actions_frame = tk.Frame(toolbar, bg=T.MAIN_BG)
        actions_frame.pack(side=tk.RIGHT)
        
        for text, cmd in [
            ("Select All", self._select_all),
            ("Select None", self._select_none),
            ("Defaults", self._select_defaults)
        ]:
            btn = tk.Button(
                actions_frame,
                text=text,
                font=("Segoe UI", 9),
                bg=T.SECONDARY_BG,
                fg=T.TEXT_PRIMARY,
                relief=tk.FLAT,
                padx=15,
                pady=5,
                cursor="hand2",
                command=cmd
            )
            btn.pack(side=tk.LEFT, padx=5)
    
    def _create_content(self):
        """Create main content area with chart categories"""
        # Create scrollable frame
        content_frame = tk.Frame(self.dialog, bg=T.MAIN_BG)
        content_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=15)
        
        canvas = tk.Canvas(content_frame, bg=T.MAIN_BG, highlightthickness=0)
        scrollbar = ttk.Scrollbar(content_frame, orient="vertical", command=canvas.yview)
        self.scrollable_frame = tk.Frame(canvas, bg=T.MAIN_BG)
        
        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Create categories
        self.chart_widgets = {}
        for category, charts in self.CHARTS.items():
            self._create_category(self.scrollable_frame, category, charts)
    
    def _create_category(self, parent, category_name, charts):
        """Create a chart category section"""
        category_frame = tk.Frame(parent, bg=T.CARD_BG, relief=tk.FLAT, bd=0)
        category_frame.pack(fill=tk.X, pady=(0, 15))
        
        # Category header
        header = tk.Frame(category_frame, bg=T.PANEL_HEADER, height=35)
        header.pack(fill=tk.X)
        header.pack_propagate(False)
        
        tk.Label(
            header,
            text=category_name,
            font=("Segoe UI", 11, "bold"),
            bg=T.PANEL_HEADER,
            fg=T.TEXT_ON_DARK
        ).pack(side=tk.LEFT, padx=15, pady=5)
        
        # Charts in this category
        charts_container = tk.Frame(category_frame, bg=T.CARD_BG)
        charts_container.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        for chart in charts:
            chart_widget = self._create_chart_item(charts_container, chart)
            self.chart_widgets[chart["id"]] = chart_widget
    
    def _create_chart_item(self, parent, chart):
        """Create a single chart item"""
        item_frame = tk.Frame(parent, bg=T.CARD_BG, relief=tk.FLAT, bd=1)
        item_frame.pack(fill=tk.X, pady=5)
        
        # Hover effect
        def on_enter(e):
            item_frame.config(bg=T.HOVER_BG)
            icon_label.config(bg=T.HOVER_BG)
            name_label.config(bg=T.HOVER_BG)
            desc_label.config(bg=T.HOVER_BG)
            
        def on_leave(e):
            item_frame.config(bg=T.CARD_BG)
            icon_label.config(bg=T.CARD_BG)
            name_label.config(bg=T.CARD_BG)
            desc_label.config(bg=T.CARD_BG)
        
        item_frame.bind("<Enter>", on_enter)
        item_frame.bind("<Leave>", on_leave)
        
        # Checkbox
        cb = tk.Checkbutton(
            item_frame,
            variable=self.chart_vars[chart["id"]],
            bg=T.CARD_BG,
            activebackground=T.CARD_BG,
            command=self._update_selection_count
        )
        cb.pack(side=tk.LEFT, padx=10)
        cb.bind("<Enter>", on_enter)
        cb.bind("<Leave>", on_leave)
        
        # Icon
        icon_label = tk.Label(
            item_frame,
            text=chart["icon"],
            font=("Segoe UI", 20),
            bg=T.CARD_BG
        )
        icon_label.pack(side=tk.LEFT, padx=(0, 10))
        icon_label.bind("<Enter>", on_enter)
        icon_label.bind("<Leave>", on_leave)
        
        # Text content
        text_frame = tk.Frame(item_frame, bg=T.CARD_BG)
        text_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, pady=8)
        text_frame.bind("<Enter>", on_enter)
        text_frame.bind("<Leave>", on_leave)
        
        name_label = tk.Label(
            text_frame,
            text=chart["name"],
            font=("Segoe UI", 11, "bold"),
            bg=T.CARD_BG,
            fg=T.TEXT_PRIMARY,
            anchor="w"
        )
        name_label.pack(anchor="w")
        name_label.bind("<Enter>", on_enter)
        name_label.bind("<Leave>", on_leave)
        
        desc_label = tk.Label(
            text_frame,
            text=chart["desc"],
            font=("Segoe UI", 9),
            bg=T.CARD_BG,
            fg=T.TEXT_SECONDARY,
            anchor="w"
        )
        desc_label.pack(anchor="w")
        desc_label.bind("<Enter>", on_enter)
        desc_label.bind("<Leave>", on_leave)
        
        # Make entire frame clickable
        def toggle_chart(e):
            current = self.chart_vars[chart["id"]].get()
            self.chart_vars[chart["id"]].set(not current)
            self._update_selection_count()
        
        for widget in [item_frame, icon_label, text_frame, name_label, desc_label]:
            widget.bind("<Button-1>", toggle_chart)
        
        return item_frame
    
    def _create_footer(self):
        """Create dialog footer with action buttons"""
        footer = tk.Frame(self.dialog, bg=T.MAIN_BG, height=70)
        footer.pack(fill=tk.X, side=tk.BOTTOM)
        footer.pack_propagate(False)
        
        # Separator
        tk.Frame(footer, bg=T.BORDER, height=1).pack(fill=tk.X)
        
        button_frame = tk.Frame(footer, bg=T.MAIN_BG)
        button_frame.pack(expand=True)
        
        # Cancel button
        cancel_btn = tk.Button(
            button_frame,
            text="Cancel",
            font=("Segoe UI", 10),
            bg=T.SECONDARY_BG,
            fg=T.TEXT_PRIMARY,
            relief=tk.FLAT,
            padx=30,
            pady=10,
            cursor="hand2",
            command=self.dialog.destroy
        )
        cancel_btn.pack(side=tk.LEFT, padx=5)
        
        # Apply button
        apply_btn = tk.Button(
            button_frame,
            text="✓ Apply Selection",
            font=("Segoe UI", 11, "bold"),
            bg=T.PRIMARY,
            fg=T.TEXT_ON_DARK,
            relief=tk.FLAT,
            padx=40,
            pady=10,
            cursor="hand2",
            command=self._apply_selection
        )
        apply_btn.pack(side=tk.LEFT, padx=5)
        
    def _update_selection_count(self):
        """Update the selection counter"""
        count = sum(1 for var in self.chart_vars.values() if var.get())
        self.selection_label.config(text=f"{count} chart{'s' if count != 1 else ''} selected")
    
    def _select_all(self):
        """Select all charts"""
        for var in self.chart_vars.values():
            var.set(True)
        self._update_selection_count()
    
    def _select_none(self):
        """Deselect all charts"""
        for var in self.chart_vars.values():
            var.set(False)
        self._update_selection_count()
    
    def _select_defaults(self):
        """Select default charts"""
        for category, charts in self.CHARTS.items():
            for chart in charts:
                self.chart_vars[chart["id"]].set(chart["default"])
        self._update_selection_count()
    
    def _on_search(self, *args):
        """Filter charts based on search query"""
        query = self.search_var.get().lower()
        if query == "search charts...":
            query = ""
        
        for category, charts in self.CHARTS.items():
            for chart in charts:
                widget = self.chart_widgets.get(chart["id"])
                if widget:
                    if not query or query in chart["name"].lower() or query in chart["desc"].lower():
                        widget.pack(fill=tk.X, pady=5)
                    else:
                        widget.pack_forget()
    
    def _apply_selection(self):
        """Apply selection and close dialog"""
        count = sum(1 for var in self.chart_vars.values() if var.get())
        if count == 0:
            tk.messagebox.showwarning(
                "No Charts Selected",
                "Please select at least one chart to generate.",
                parent=self.dialog
            )
            return
        
        self.dialog.destroy()


def test():
    """Test the chart selector"""
    root = tk.Tk()
    root.withdraw()
    
    chart_vars = {}
    selector = ProChartSelector(root, chart_vars)
    root.wait_window(selector.dialog)
    
    print("\nSelected charts:")
    for chart_id, var in chart_vars.items():
        if var.get():
            print(f"  - {chart_id}")
    
    root.destroy()


if __name__ == "__main__":
    test()

