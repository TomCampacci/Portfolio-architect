# modern_ui_builder.py - Modern UI Components with Tabs
"""
Modern UI builder with tabbed interface for better organization and UX.
"""
import tkinter as tk
from tkinter import ttk
from ui.theme_colors import LightPremiumTheme as T


class ModernUIBuilder:
    """Modern UI components with tabbed interface"""
    
    @staticmethod
    def create_tabbed_interface(parent):
        """
        Create modern tabbed interface
        
        Returns:
            tuple: (notebook, tabs_dict)
        """
        # Create notebook (tabs container)
        style = ttk.Style()
        style.theme_use('default')
        
        # Configure tab style
        style.configure('TNotebook', background=T.MAIN_BG, borderwidth=0)
        style.configure('TNotebook.Tab', 
                       background=T.CARD_BG,
                       foreground=T.TEXT_PRIMARY,
                       padding=[20, 10],
                       font=('Arial', 11, 'bold'))
        style.map('TNotebook.Tab',
                 background=[('selected', T.PRIMARY)],
                 foreground=[('selected', T.TEXT_ON_DARK)])
        
        notebook = ttk.Notebook(parent)
        notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Create tabs
        tabs = {}
        
        # Tab 1: Portfolio Setup
        portfolio_tab = tk.Frame(notebook, bg=T.MAIN_BG)
        notebook.add(portfolio_tab, text=' 📊 Portfolio ')
        tabs['portfolio'] = portfolio_tab
        
        # Tab 2: Benchmarks
        benchmarks_tab = tk.Frame(notebook, bg=T.MAIN_BG)
        notebook.add(benchmarks_tab, text=' 📈 Benchmarks ')
        tabs['benchmarks'] = benchmarks_tab
        
        # Tab 3: Charts Selection
        charts_tab = tk.Frame(notebook, bg=T.MAIN_BG)
        notebook.add(charts_tab, text=' 📉 Charts ')
        tabs['charts'] = charts_tab
        
        # Tab 4: Settings
        settings_tab = tk.Frame(notebook, bg=T.MAIN_BG)
        notebook.add(settings_tab, text=' ⚙️ Settings ')
        tabs['settings'] = settings_tab
        
        # Tab 5: Market Data
        market_tab = tk.Frame(notebook, bg=T.MAIN_BG)
        notebook.add(market_tab, text=' 🌍 Market Data ')
        tabs['market'] = market_tab
        
        return notebook, tabs
    
    @staticmethod
    def create_info_card(parent, title, content, icon="ℹ️"):
        """
        Create an information card with icon
        
        Args:
            parent: Parent widget
            title: Card title
            content: Card content text
            icon: Icon emoji
        """
        card = tk.Frame(parent, bg=T.HIGHLIGHT, relief=tk.FLAT, bd=0)
        card.pack(fill=tk.X, padx=15, pady=10)
        
        # Add subtle border effect
        border_frame = tk.Frame(card, bg=T.BORDER, bd=0)
        border_frame.pack(fill=tk.BOTH, expand=True, padx=1, pady=1)
        
        inner_frame = tk.Frame(border_frame, bg=T.HIGHLIGHT)
        inner_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Header with icon
        header = tk.Frame(inner_frame, bg=T.HIGHLIGHT)
        header.pack(fill=tk.X)
        
        tk.Label(
            header, text=icon, font=("Arial", 16),
            bg=T.HIGHLIGHT, fg=T.PRIMARY
        ).pack(side=tk.LEFT, padx=(0, 10))
        
        tk.Label(
            header, text=title, font=("Arial", 11, "bold"),
            bg=T.HIGHLIGHT, fg=T.TEXT_PRIMARY
        ).pack(side=tk.LEFT)
        
        # Content
        tk.Label(
            inner_frame, text=content, font=("Arial", 9),
            bg=T.HIGHLIGHT, fg=T.TEXT_SECONDARY,
            wraplength=600, justify=tk.LEFT
        ).pack(fill=tk.X, pady=(5, 0))
        
        return card
    
    @staticmethod
    def create_enhanced_ticker_card(parent, num_tickers=10):
        """
        Create enhanced ticker input card with better UX
        
        Args:
            parent: Parent widget
            num_tickers: Number of ticker rows
        
        Returns:
            tuple: (card_frame, ticker_rows, weight_total_label)
        """
        # Main card
        card = tk.Frame(parent, bg=T.CARD_BG, relief=tk.RIDGE, bd=2)
        card.pack(fill=tk.BOTH, expand=True, padx=15, pady=10)
        
        # Header with gradient effect
        header = tk.Frame(card, bg=T.PANEL_HEADER, height=60)
        header.pack(fill=tk.X)
        header.pack_propagate(False)
        
        header_left = tk.Frame(header, bg=T.PANEL_HEADER)
        header_left.pack(side=tk.LEFT, fill=tk.Y, padx=15)
        
        tk.Label(
            header_left, text="📊 Portfolio Tickers", 
            font=("Arial", 14, "bold"),
            bg=T.PANEL_HEADER, fg=T.TEXT_ON_DARK
        ).pack(anchor="w", pady=(8, 2))
        
        tk.Label(
            header_left, text="Enter ticker symbols (e.g., AAPL, NVDA, MSFT)", 
            font=("Arial", 9),
            bg=T.PANEL_HEADER, fg=T.TEXT_ON_DARK
        ).pack(anchor="w")
        
        # Column headers
        col_header = tk.Frame(card, bg=T.ACTIVE_BG, height=35)
        col_header.pack(fill=tk.X)
        col_header.pack_propagate(False)
        
        tk.Label(col_header, text="#", width=3, font=("Arial", 9, "bold"),
                bg=T.ACTIVE_BG, fg=T.TEXT_PRIMARY).pack(side=tk.LEFT, padx=(15, 5))
        tk.Label(col_header, text="Ticker Symbol", width=18, font=("Arial", 9, "bold"),
                bg=T.ACTIVE_BG, fg=T.TEXT_PRIMARY, anchor="w").pack(side=tk.LEFT, padx=5)
        tk.Label(col_header, text="Status", width=4, font=("Arial", 9, "bold"),
                bg=T.ACTIVE_BG, fg=T.TEXT_PRIMARY).pack(side=tk.LEFT, padx=5)
        tk.Label(col_header, text="Weight %", width=8, font=("Arial", 9, "bold"),
                bg=T.ACTIVE_BG, fg=T.TEXT_PRIMARY).pack(side=tk.LEFT, padx=5)
        tk.Label(col_header, text="Amount", width=10, font=("Arial", 9, "bold"),
                bg=T.ACTIVE_BG, fg=T.TEXT_PRIMARY).pack(side=tk.LEFT, padx=5)
        tk.Label(col_header, text="Name", font=("Arial", 9, "bold"),
                bg=T.ACTIVE_BG, fg=T.TEXT_PRIMARY, anchor="w").pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        
        # Scrollable body
        body_container = tk.Frame(card, bg=T.CARD_BG)
        body_container.pack(fill=tk.BOTH, expand=True)
        
        canvas = tk.Canvas(body_container, bg=T.CARD_BG, highlightthickness=0, height=400)
        scrollbar = tk.Scrollbar(body_container, orient="vertical", command=canvas.yview)
        scrollable_body = tk.Frame(canvas, bg=T.CARD_BG)
        
        scrollable_body.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_body, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Ticker rows
        ticker_rows = []
        for i in range(num_tickers):
            row_bg = T.CARD_BG if i % 2 == 0 else T.HOVER_BG
            row = tk.Frame(scrollable_body, bg=row_bg, height=45)
            row.pack(fill=tk.X, pady=1)
            row.pack_propagate(False)
            
            # Number
            tk.Label(row, text=f"{i+1:02}", width=3, font=("Courier", 9, "bold"),
                    fg=T.PRIMARY, bg=row_bg).pack(side=tk.LEFT, padx=(15, 5))
            
            # Ticker entry with placeholder
            placeholder = f"Enter ticker {i+1}"
            entry = tk.Entry(row, width=18, font=("Arial", 10), fg=T.TEXT_MUTED, 
                           bg=T.INPUT_BG, relief=tk.FLAT, bd=1,
                           highlightthickness=1, highlightcolor=T.PRIMARY,
                           highlightbackground=T.BORDER)
            entry.insert(0, placeholder)
            entry.pack(side=tk.LEFT, padx=5, pady=8)
            
            # Status indicator
            status_lbl = tk.Label(row, text="•", font=("Arial", 14, "bold"),
                                 fg=T.TEXT_MUTED, bg=row_bg, width=4)
            status_lbl.pack(side=tk.LEFT, padx=5)
            
            # Weight entry
            weight_ent = tk.Entry(row, width=8, font=("Arial", 10), 
                                 fg=T.TEXT_PRIMARY, bg=T.INPUT_BG_FOCUS,
                                 relief=tk.FLAT, justify="center", bd=1,
                                 highlightthickness=1, highlightcolor=T.SUCCESS,
                                 highlightbackground=T.BORDER)
            weight_ent.insert(0, "10.0")
            weight_ent.pack(side=tk.LEFT, padx=5, pady=8)
            
            tk.Label(row, text="%", font=("Arial", 9), 
                    fg=T.TEXT_SECONDARY, bg=row_bg).pack(side=tk.LEFT, padx=(0, 5))
            
            # Amount entry
            amount_ent = tk.Entry(row, width=10, font=("Arial", 10),
                                 fg=T.TEXT_PRIMARY, bg=T.HIGHLIGHT,
                                 relief=tk.FLAT, justify="center", bd=1,
                                 highlightthickness=1, highlightcolor=T.SUCCESS,
                                 highlightbackground=T.BORDER)
            amount_ent.insert(0, "1,000")
            amount_ent.pack(side=tk.LEFT, padx=5, pady=8)
            
            # Currency label
            currency_lbl = tk.Label(row, text="$", font=("Arial", 9),
                                   fg=T.TEXT_SECONDARY, bg=row_bg)
            currency_lbl.pack(side=tk.LEFT, padx=(0, 5))
            
            # Name label (for validated ticker names)
            name_lbl = tk.Label(row, text="", font=("Arial", 9, "italic"),
                               fg=T.TEXT_SECONDARY, bg=row_bg, anchor="w")
            name_lbl.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
            
            ticker_rows.append({
                "entry": entry,
                "status": status_lbl,
                "placeholder": placeholder,
                "weight_entry": weight_ent,
                "amount_entry": amount_ent,
                "currency_label": currency_lbl,
                "name_label": name_lbl,
                "row_frame": row
            })
        
        # Footer with total and actions
        footer = tk.Frame(card, bg=T.INPUT_BG_FOCUS, bd=0, height=50)
        footer.pack(fill=tk.X)
        footer.pack_propagate(False)
        
        footer_inner = tk.Frame(footer, bg=T.INPUT_BG_FOCUS)
        footer_inner.pack(fill=tk.BOTH, expand=True, padx=15, pady=10)
        
        # Total weight
        total_frame = tk.Frame(footer_inner, bg=T.INPUT_BG_FOCUS)
        total_frame.pack(side=tk.LEFT)
        
        tk.Label(total_frame, text="TOTAL WEIGHT:", font=("Arial", 10, "bold"),
                bg=T.INPUT_BG_FOCUS, fg=T.WARNING).pack(side=tk.LEFT, padx=(0, 10))
        
        weight_total_label = tk.Label(total_frame, text="100.0%", 
                                      font=("Arial", 12, "bold"),
                                      bg=T.INPUT_BG_FOCUS, fg=T.PANEL_HEADER)
        weight_total_label.pack(side=tk.LEFT)
        
        # Action buttons
        actions_frame = tk.Frame(footer_inner, bg=T.INPUT_BG_FOCUS)
        actions_frame.pack(side=tk.RIGHT)
        
        # Will be populated with callbacks later
        
        return card, ticker_rows, weight_total_label
    
    @staticmethod
    def create_enhanced_exchange_dialog(root, query, exchanges_data, is_isin=False):
        """
        Create enhanced exchange selection dialog with preview
        
        Args:
            root: Parent window
            query: Symbol or ISIN
            exchanges_data: List of exchange options
            is_isin: Whether this is an ISIN
        
        Returns:
            tuple: (dialog, selected_var)
        """
        dialog = tk.Toplevel(root)
        dialog.title("Select Exchange")
        dialog.geometry("650x550")
        dialog.transient(root)
        dialog.grab_set()
        dialog.configure(bg=T.MAIN_BG)
        
        # Modern header - Compact
        header = tk.Frame(dialog, bg=T.PANEL_HEADER, height=80)
        header.pack(fill=tk.X)
        header.pack_propagate(False)
        
        header_content = tk.Frame(header, bg=T.PANEL_HEADER)
        header_content.pack(expand=True, fill=tk.BOTH, padx=20, pady=12)
        
        # Icon and title
        icon_label = tk.Label(header_content, text="🌍", font=("Arial", 24),
                             bg=T.PANEL_HEADER)
        icon_label.pack(side=tk.LEFT, padx=(0, 12))
        
        title_frame = tk.Frame(header_content, bg=T.PANEL_HEADER)
        title_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        if is_isin:
            title_text = "ISIN Code Detected"
            subtitle_text = f"Multiple exchanges found for: {query}"
        else:
            title_text = "Multiple Exchanges Available"
            subtitle_text = f"Symbol: {query}"
        
        tk.Label(title_frame, text=title_text, font=("Arial", 14, "bold"),
                bg=T.PANEL_HEADER, fg=T.TEXT_ON_DARK, anchor="w").pack(fill=tk.X)
        
        tk.Label(title_frame, text=subtitle_text, font=("Arial", 10),
                bg=T.PANEL_HEADER, fg=T.TEXT_ON_DARK, anchor="w").pack(fill=tk.X, pady=(5, 0))
        
        # Instrument name if available
        if exchanges_data and len(exchanges_data) > 0:
            instrument_name = exchanges_data[0].get('name', '')
            if instrument_name:
                tk.Label(title_frame, text=instrument_name, font=("Arial", 9, "italic"),
                        bg=T.PANEL_HEADER, fg=T.TEXT_ON_DARK, anchor="w").pack(fill=tk.X, pady=(3, 0))
        
        # Symbol display - Clean and simple
        info_frame = tk.Frame(dialog, bg=T.HIGHLIGHT, bd=0, height=50)
        info_frame.pack(fill=tk.X, padx=20, pady=(15, 0))
        info_frame.pack_propagate(False)
        
        tk.Label(info_frame, 
                text=f"Symbol: {query}",
                font=("Arial", 14, "bold"), bg=T.HIGHLIGHT, fg=T.TEXT_PRIMARY,
                anchor="w").pack(side=tk.LEFT, padx=15, pady=12)
        
        # Scrollable list of exchanges
        list_container = tk.Frame(dialog, bg=T.MAIN_BG)
        list_container.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        canvas = tk.Canvas(list_container, bg=T.MAIN_BG, highlightthickness=0)
        scrollbar = tk.Scrollbar(list_container, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg=T.MAIN_BG)
        
        scrollable_frame.bind("<Configure>",
                             lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Radio button variable
        selected_var = tk.StringVar()
        
        # Exchange name mapping
        exchange_names = {
            "PA": "🇫🇷 Euronext Paris", "FP": "🇫🇷 Euronext Paris",
            "MI": "🇮🇹 Borsa Italiana (Milan)", "IM": "🇮🇹 Borsa Italiana",
            "LN": "🇬🇧 London Stock Exchange", "L": "🇬🇧 London Stock Exchange",
            "AS": "🇳🇱 Euronext Amsterdam", "NA": "🇳🇱 Euronext Amsterdam",
            "BB": "🇧🇪 Euronext Brussels", "BR": "🇧🇪 Euronext Brussels",
            "SM": "🇪🇸 BME Spanish Exchanges", "MC": "🇪🇸 BME Spanish Exchanges",
            "SW": "🇨🇭 SIX Swiss Exchange",
            "GR": "🇩🇪 Deutsche Boerse (Frankfurt)", "GY": "🇩🇪 Deutsche Boerse (XETRA)", "DE": "🇩🇪 Deutsche Boerse",
            "US": "🇺🇸 US Exchanges", "UN": "🇺🇸 NYSE", "UW": "🇺🇸 NASDAQ"
        }
        
        # Sort exchanges by currency for better UX (USD first, then EUR, then others alphabetically)
        currency_priority = {"USD": 0, "EUR": 1, "GBP": 2, "CHF": 3, "JPY": 4}
        
        def sort_key(exchange_data):
            curr = exchange_data.get('currency', 'USD')
            priority = currency_priority.get(curr, 99)
            return (priority, curr, exchange_data.get('exchange', ''))
        
        exchanges_data_sorted = sorted(exchanges_data, key=sort_key)
        
        # Track current currency for section headers
        current_currency = None
        
        # Add exchange options as modern cards
        for i, data in enumerate(exchanges_data_sorted):
            ticker = data.get('ticker') or data.get('symbol', '')
            name = data.get('name', '')
            exch_code = data.get('exchange', '')
            currency = data.get('currency', 'USD')
            info_detail = data.get('market_sector') or data.get('type', '')
            
            if not ticker:
                continue
            
            # Add currency section header when currency changes
            if currency != current_currency:
                current_currency = currency
                
                # Currency section header - Compact
                currency_emojis = {
                    "USD": "💵",
                    "EUR": "💶",
                    "GBP": "💷",
                    "CHF": "🇨🇭",
                    "JPY": "💴",
                    "HKD": "🇭🇰",
                    "AUD": "🇦🇺",
                    "CAD": "🇨🇦"
                }
                
                section_header = tk.Frame(scrollable_frame, bg=T.PANEL_HEADER, height=28)
                section_header.pack(fill=tk.X, pady=(8 if i > 0 else 0, 3))
                section_header.pack_propagate(False)
                
                emoji = currency_emojis.get(currency, "💱")
                tk.Label(
                    section_header, 
                    text=f"{emoji} {currency}",
                    font=("Arial", 9, "bold"),
                    bg=T.PANEL_HEADER, fg=T.TEXT_ON_DARK,
                    anchor="w"
                ).pack(side=tk.LEFT, padx=12, pady=6)
            
            # Create modern card for each exchange - Compact
            option_card = tk.Frame(scrollable_frame, bg=T.CARD_BG, 
                                   relief=tk.FLAT, bd=0, cursor="hand2")
            option_card.pack(fill=tk.X, pady=3)
            
            # Border effect
            border = tk.Frame(option_card, bg=T.BORDER)
            border.pack(fill=tk.BOTH, expand=True, padx=1, pady=1)
            
            inner = tk.Frame(border, bg=T.CARD_BG)
            inner.pack(fill=tk.BOTH, expand=True, padx=10, pady=8)
            
            # Radio button
            rb = tk.Radiobutton(
                inner, variable=selected_var, value=ticker,
                bg=T.CARD_BG, activebackground=T.CARD_BG,
                selectcolor=T.SUCCESS, font=("Arial", 10)
            )
            rb.pack(side=tk.LEFT, padx=(0, 10))
            
            # Exchange info
            info_frame = tk.Frame(inner, bg=T.CARD_BG)
            info_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
            
            # Top row: Exchange name and CURRENCY (compact)
            top_row = tk.Frame(info_frame, bg=T.CARD_BG)
            top_row.pack(fill=tk.X)
            
            # Exchange name with flag
            exch_display = exchange_names.get(exch_code, exch_code)
            tk.Label(top_row, text=exch_display, font=("Arial", 10, "bold"),
                    bg=T.CARD_BG, fg=T.TEXT_PRIMARY, anchor="w").pack(side=tk.LEFT)
            
            # Currency badge - Smaller and more subtle
            if currency:
                currency_badge = tk.Label(
                    top_row, text=f" {currency} ", 
                    font=("Arial", 8, "bold"),
                    bg=T.BORDER,
                    fg=T.TEXT_PRIMARY,
                    relief=tk.FLAT,
                    padx=6, pady=1
                )
                currency_badge.pack(side=tk.LEFT, padx=8)
            
            # Ticker symbol - Compact
            ticker_text = f"{ticker}"
            tk.Label(info_frame, text=ticker_text, font=("Courier", 10, "bold"),
                    bg=T.CARD_BG, fg=T.PRIMARY, anchor="w").pack(fill=tk.X, pady=(3, 0))
            
            # Additional info
            if info_detail:
                tk.Label(info_frame, text=info_detail, font=("Arial", 8),
                        bg=T.CARD_BG, fg=T.TEXT_SECONDARY, anchor="w").pack(fill=tk.X, pady=(2, 0))
            
            # Make whole card clickable
            def select_option(ticker_val=ticker):
                selected_var.set(ticker_val)
            
            for widget in [option_card, border, inner, info_frame]:
                widget.bind("<Button-1>", lambda e, t=ticker: selected_var.set(t))
            
            # Hover effect
            def on_enter(e, card=option_card, brd=border):
                brd.configure(bg=T.PRIMARY)
            
            def on_leave(e, card=option_card, brd=border):
                brd.configure(bg=T.BORDER)
            
            option_card.bind("<Enter>", on_enter)
            option_card.bind("<Leave>", on_leave)
            
            # Select first option by default
            if i == 0:
                selected_var.set(ticker)
        
        # Footer with buttons - Compact
        footer = tk.Frame(dialog, bg=T.CARD_BG, bd=0, height=60)
        footer.pack(fill=tk.X, side=tk.BOTTOM)
        footer.pack_propagate(False)
        
        btn_frame = tk.Frame(footer, bg=T.CARD_BG)
        btn_frame.pack(expand=True, pady=12)
        
        # Cancel button
        cancel_btn = tk.Button(
            btn_frame, text="Cancel", font=("Arial", 10, "bold"),
            bg=T.BTN_SECONDARY_BG, fg=T.TEXT_ON_DARK,
            padx=20, pady=8, relief=tk.FLAT, cursor="hand2",
            command=lambda: [selected_var.set(""), dialog.destroy()]
        )
        cancel_btn.pack(side=tk.LEFT, padx=8)
        
        # Confirm button
        confirm_btn = tk.Button(
            btn_frame, text="Confirm", font=("Arial", 10, "bold"),
            bg=T.SUCCESS, fg=T.TEXT_ON_DARK,
            padx=25, pady=8, relief=tk.FLAT, cursor="hand2",
            command=dialog.destroy
        )
        confirm_btn.pack(side=tk.LEFT, padx=8)
        
        return dialog, selected_var

