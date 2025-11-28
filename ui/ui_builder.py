# ui_builder.py - UI Component Builder for Portfolio Analysis
import tkinter as tk
from tkinter import ttk
from ui.theme_colors import LightPremiumTheme as T


class UIBuilder:
    """Static methods for building UI components"""
    
    @staticmethod
    def create_forex_rates_panel(parent):
        """
        Create panel to display current forex rates (EUR/USD, GBP/USD)
        
        Args:
            parent: Parent widget
        
        Returns:
            dict: {
                'panel_frame': LabelFrame,
                'eurusd_label': Label,
                'gbpusd_label': Label,
                'timestamp_label': Label,
                'update_callback': function to update rates,
                'refresh_callback': placeholder for refresh function
            }
        """
        panel_frame = tk.LabelFrame(
            parent, text="Exchange Rates", font=("Arial", 11, "bold"),
            bg=T.CARD_BG, relief=tk.RIDGE, bd=2, fg=T.PANEL_HEADER
        )
        panel_frame.pack(fill=tk.X, pady=(0, 12))
        
        # Header with refresh button
        header_frame = tk.Frame(panel_frame, bg=T.CARD_BG)
        header_frame.pack(fill=tk.X, padx=15, pady=(8, 0))
        
        # Refresh button (will be bound later)
        refresh_btn = tk.Button(
            header_frame, text="Refresh", font=("Arial", 8, "bold"),
            bg=T.PRIMARY, fg=T.TEXT_ON_DARK, relief=tk.FLAT, padx=10, pady=4,
            cursor="hand2", borderwidth=0
        )
        refresh_btn.pack(side=tk.RIGHT)
        
        # Inner container
        inner_frame = tk.Frame(panel_frame, bg=T.CARD_BG)
        inner_frame.pack(fill=tk.X, padx=15, pady=12)
        
        # EUR/USD Rate
        eurusd_row = tk.Frame(inner_frame, bg=T.CARD_BG)
        eurusd_row.pack(fill=tk.X, pady=(0, 8))
        
        eurusd_label_left = tk.Label(
            eurusd_row, text="EUR/USD:", font=("Arial", 10),
            bg=T.CARD_BG, fg=T.TEXT_PRIMARY
        )
        eurusd_label_left.pack(side=tk.LEFT)
        
        eurusd_value_label = tk.Label(
            eurusd_row, text="Loading...", font=("Arial", 11, "bold"),
            bg=T.CARD_BG, fg=T.PRIMARY
        )
        eurusd_value_label.pack(side=tk.LEFT, padx=(10, 0))
        
        # GBP/USD Rate
        gbpusd_row = tk.Frame(inner_frame, bg=T.CARD_BG)
        gbpusd_row.pack(fill=tk.X, pady=(0, 8))
        
        gbpusd_label_left = tk.Label(
            gbpusd_row, text="GBP/USD:", font=("Arial", 10),
            bg=T.CARD_BG, fg=T.TEXT_PRIMARY
        )
        gbpusd_label_left.pack(side=tk.LEFT)
        
        gbpusd_value_label = tk.Label(
            gbpusd_row, text="Loading...", font=("Arial", 11, "bold"),
            bg=T.CARD_BG, fg=T.PRIMARY
        )
        gbpusd_value_label.pack(side=tk.LEFT, padx=(10, 0))
        
        # Timestamp
        timestamp_row = tk.Frame(inner_frame, bg=T.CARD_BG)
        timestamp_row.pack(fill=tk.X)
        
        timestamp_label = tk.Label(
            timestamp_row, text="Last update: --", font=("Arial", 8),
            bg=T.CARD_BG, fg=T.TEXT_SECONDARY
        )
        timestamp_label.pack(side=tk.LEFT)
        
        # Update function
        def update_rates(rates_dict):
            """Update the forex rates display"""
            if rates_dict.get('success'):
                eurusd = rates_dict.get('EURUSD')
                gbpusd = rates_dict.get('GBPUSD')
                timestamp = rates_dict.get('timestamp', '')
                
                if eurusd:
                    eurusd_value_label.config(text=f"{eurusd:.4f}", fg=T.SUCCESS)
                else:
                    eurusd_value_label.config(text="N/A", fg=T.ERROR)
                
                if gbpusd:
                    gbpusd_value_label.config(text=f"{gbpusd:.4f}", fg=T.SUCCESS)
                else:
                    gbpusd_value_label.config(text="N/A", fg=T.ERROR)
                
                timestamp_label.config(text=f"Last update: {timestamp}")
            else:
                eurusd_value_label.config(text="Error", fg=T.ERROR)
                gbpusd_value_label.config(text="Error", fg=T.ERROR)
                error_msg = rates_dict.get('error', 'Unknown error')
                timestamp_label.config(text=f"Error: {error_msg}")
        
        return {
            'panel_frame': panel_frame,
            'eurusd_label': eurusd_value_label,
            'gbpusd_label': gbpusd_value_label,
            'timestamp_label': timestamp_label,
            'refresh_btn': refresh_btn,
            'update_callback': update_rates
        }
    
    @staticmethod
    def create_major_indexes_panel(parent):
        """
        Create panel to display current prices for 10 major indexes in 3 columns
        
        Args:
            parent: Parent widget
        
        Returns:
            dict: {
                'panel_frame': LabelFrame,
                'index_labels': list of Labels,
                'timestamp_label': Label,
                'update_callback': function to update prices
            }
        """
        panel_frame = tk.LabelFrame(
            parent, text="Major Indexes", font=("Arial", 11, "bold"),
            bg=T.CARD_BG, relief=tk.RIDGE, bd=2
        )
        panel_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 12))
        
        # Header with refresh button
        header_frame = tk.Frame(panel_frame, bg=T.CARD_BG)
        header_frame.pack(fill=tk.X, padx=15, pady=(8, 0))
        
        # Refresh button (will be bound later)
        indexes_refresh_btn = tk.Button(
            header_frame, text="Refresh", font=("Arial", 8),
            bg=T.PRIMARY, fg=T.TEXT_ON_DARK, relief=tk.FLAT, padx=8, pady=2,
            cursor="hand2", borderwidth=1
        )
        indexes_refresh_btn.pack(side=tk.RIGHT)
        
        # Inner container
        inner_frame = tk.Frame(panel_frame, bg=T.CARD_BG)
        inner_frame.pack(fill=tk.BOTH, expand=True, padx=15, pady=12)
        
        # Create 3 columns container
        columns_container = tk.Frame(inner_frame, bg=T.CARD_BG)
        columns_container.pack(fill=tk.BOTH, expand=True)
        
        # Store label references
        index_labels = {}
        
        # Define indexes organized in 3 columns
        columns_data = [
            ['S&P 500', 'Nasdaq', 'Dow Jones', 'DAX'],
            ['CAC 40', 'FTSE 100', 'Nikkei 225', 'Hang Seng'],
            ['Gold', 'Bitcoin']
        ]
        
        # Create 3 columns
        for col_idx, col_indexes in enumerate(columns_data):
            col_frame = tk.Frame(columns_container, bg=T.CARD_BG)
            col_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10 if col_idx < 2 else 0))
            
            for idx_name in col_indexes:
                row = tk.Frame(col_frame, bg=T.CARD_BG)
                row.pack(fill=tk.X, pady=3)
                
                name_label = tk.Label(
                    row, text=f"{idx_name}:", font=("Arial", 9),
                    bg=T.CARD_BG, fg=T.TEXT_PRIMARY, anchor="w"
                )
                name_label.pack(side=tk.LEFT)
                
                price_label = tk.Label(
                    row, text="Loading...", font=("Arial", 9, "bold"),
                    bg=T.CARD_BG, fg=T.PRIMARY, anchor="e"
                )
                price_label.pack(side=tk.RIGHT, fill=tk.X, expand=True, padx=(5, 0))
                
                index_labels[idx_name] = price_label
        
        # Timestamp at bottom
        timestamp_frame = tk.Frame(panel_frame, bg=T.CARD_BG)
        timestamp_frame.pack(fill=tk.X, padx=15, pady=(5, 10))
        
        timestamp_label = tk.Label(
            timestamp_frame, text="Last update: --", font=("Arial", 8),
            bg=T.CARD_BG, fg=T.TEXT_MUTED
        )
        timestamp_label.pack(side=tk.LEFT)
        
        # Update function
        def update_indexes(indexes_dict):
            """Update the indexes display"""
            if indexes_dict.get('success'):
                indexes_list = indexes_dict.get('indexes', [])
                timestamp = indexes_dict.get('timestamp', '')
                
                for index_data in indexes_list:
                    name = index_data.get('name')
                    price = index_data.get('price')
                    success = index_data.get('success')
                    
                    if name in index_labels:
                        label = index_labels[name]
                        if success and price is not None:
                            # Format price nicely
                            if price >= 1000:
                                formatted_price = f"{price:,.2f}"
                            else:
                                formatted_price = f"{price:.2f}"
                            label.config(text=formatted_price, fg=T.SUCCESS)
                        else:
                            label.config(text="N/A", fg=T.ERROR)
                
                timestamp_label.config(text=f"Last update: {timestamp}")
            else:
                for label in index_labels.values():
                    label.config(text="Error", fg=T.ERROR)
                error_msg = indexes_dict.get('error', 'Unknown error')
                timestamp_label.config(text=f"Error: {error_msg}")
        
        return {
            'panel_frame': panel_frame,
            'index_labels': index_labels,
            'timestamp_label': timestamp_label,
            'refresh_btn': indexes_refresh_btn,
            'update_callback': update_indexes
        }
    
    @staticmethod
    def create_capital_currency_panel(parent, default_capital=10000, default_currency="USD"):
        """
        Create panel for capital amount and currency selection
        
        Args:
            parent: Parent widget
            default_capital: Default capital amount
            default_currency: Default currency ("USD", "EUR", "GBP")
        
        Returns:
            tuple: (panel_frame, capital_var, currency_var, capital_label)
        """
        panel_frame = tk.LabelFrame(
            parent, text="Portfolio Settings", font=("Arial", 11, "bold"),
            bg=T.CARD_BG, relief=tk.RIDGE, bd=2
        )
        panel_frame.pack(fill=tk.X, pady=(0, 12))
        
        # Inner container for better layout
        inner_frame = tk.Frame(panel_frame, bg=T.CARD_BG)
        inner_frame.pack(fill=tk.X, padx=15, pady=12)
        
        # Capital Amount Section
        capital_row = tk.Frame(inner_frame, bg=T.CARD_BG)
        capital_row.pack(fill=tk.X, pady=(0, 10))
        
        capital_label_left = tk.Label(
            capital_row, text="Initial Capital:", font=("Arial", 10),
            bg=T.CARD_BG, fg=T.TEXT_PRIMARY
        )
        capital_label_left.pack(side=tk.LEFT)
        
        # Capital entry with validation
        capital_var = tk.StringVar(value=str(default_capital))
        capital_entry = tk.Entry(
            capital_row, textvariable=capital_var, font=("Arial", 12, "bold"),
            width=15, bg=T.INPUT_BG_FOCUS, fg=T.TEXT_PRIMARY, relief=tk.FLAT, bd=0
        )
        capital_entry.pack(side=tk.LEFT, padx=(10, 0))
        
        # Add padding to entry
        capital_entry.config(highlightthickness=1, highlightbackground=T.BORDER, highlightcolor=T.SUCCESS)
        
        # Display label showing formatted capital
        capital_display = tk.Label(
            capital_row, text="", font=("Arial", 9),
            bg=T.CARD_BG, fg=T.TEXT_SECONDARY
        )
        capital_display.pack(side=tk.LEFT, padx=(10, 0))
        
        # Currency Selection Section
        currency_row = tk.Frame(inner_frame, bg=T.CARD_BG)
        currency_row.pack(fill=tk.X)
        
        currency_label = tk.Label(
            currency_row, text="Currency:", font=("Arial", 10),
            bg=T.CARD_BG, fg=T.TEXT_PRIMARY
        )
        currency_label.pack(side=tk.LEFT)
        
        # Currency selector with flag emojis
        currency_var = tk.StringVar(value=default_currency)
        
        currencies = [
            ("USD - US Dollar", "USD"),
            ("EUR - Euro", "EUR"),
            ("GBP - British Pound", "GBP")
        ]
        
        currency_frame = tk.Frame(currency_row, bg=T.CARD_BG)
        currency_frame.pack(side=tk.LEFT, padx=(10, 0))
        
        for display_text, value in currencies:
            rb = tk.Radiobutton(
                currency_frame, text=display_text, variable=currency_var,
                value=value, font=("Arial", 9), bg=T.CARD_BG,
                activebackground=T.CARD_BG, selectcolor=T.HIGHLIGHT
            )
            rb.pack(side=tk.LEFT, padx=5)
        
        # Update display label when capital changes
        def update_capital_display(*args):
            try:
                amount = float(capital_var.get().replace(",", ""))
                formatted = f"({amount:,.0f})"
                capital_display.config(text=formatted, fg=T.SUCCESS)
            except ValueError:
                capital_display.config(text="(Invalid)", fg=T.ERROR)
        
        capital_var.trace_add("write", update_capital_display)
        update_capital_display()  # Initial update
        
        return panel_frame, capital_var, currency_var, capital_display, update_capital_display
    
    @staticmethod
    def create_main_layout(root):
        """
        Create main scrollable canvas layout
        
        Returns:
            tuple: (main_canvas, main_scrollbar, content_wrapper)
        """
        main_canvas = tk.Canvas(root, bg=T.MAIN_BG, highlightthickness=0)
        main_scrollbar = tk.Scrollbar(root, orient="vertical", command=main_canvas.yview)
        
        main_container = tk.Frame(main_canvas, bg=T.MAIN_BG)
        
        main_canvas.configure(yscrollcommand=main_scrollbar.set)
        main_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        main_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        canvas_frame = main_canvas.create_window((0, 0), window=main_container, anchor="nw")
        
        # Bind canvas resize (with debounce to reduce flickering)
        configure_after_id = [None]
        def on_canvas_configure(event):
            # Cancel previous configure if still pending
            if configure_after_id[0]:
                main_canvas.after_cancel(configure_after_id[0])
            # Schedule configure with small delay
            configure_after_id[0] = main_canvas.after(10, lambda: main_canvas.configure(scrollregion=main_canvas.bbox("all")))
        main_container.bind("<Configure>", on_canvas_configure)
        
        # Bind mousewheel (optimized for smoother scrolling)
        def on_mousewheel(event):
            main_canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
        main_canvas.bind_all("<MouseWheel>", on_mousewheel)
        
        # Adjust canvas window width (with debounce to reduce flickering)
        resize_after_id = [None]  # Use list to allow modification in nested function
        def on_canvas_resize(event):
            # Cancel previous resize if still pending
            if resize_after_id[0]:
                main_canvas.after_cancel(resize_after_id[0])
            # Schedule resize with small delay to avoid multiple redraws
            resize_after_id[0] = main_canvas.after(10, lambda: main_canvas.itemconfig(canvas_frame, width=event.width))
        main_canvas.bind("<Configure>", on_canvas_resize)
        
        # Add padding
        content_wrapper = tk.Frame(main_container, bg=T.MAIN_BG)
        content_wrapper.pack(fill=tk.BOTH, expand=True, padx=16, pady=16)
        
        return main_canvas, main_scrollbar, content_wrapper
    
    @staticmethod
    def create_title(parent):
        """Create title label"""
        title = tk.Label(
            parent,
            text="Portfolio Analysis - Chart Selector",
            font=("Arial", 18, "bold"), bg=T.MAIN_BG, fg=T.TEXT_PRIMARY
        )
        title.pack(pady=(0, 16))
        return title
    
    @staticmethod
    def create_left_panel(parent, weights_raw, bench_def):
        """
        Create left panel with portfolio composition and benchmarks
        
        Args:
            parent: Parent widget
            weights_raw: Dictionary of portfolio weights
            bench_def: List of benchmark tuples (label, ticker)
        
        Returns:
            tuple: (left_panel, portfolio_text, benchmark_text)
        """
        left_panel = tk.Frame(parent, bg=T.MAIN_BG, width=300)
        left_panel.pack(side=tk.LEFT, fill=tk.BOTH, padx=(0, 10))
        
        # Portfolio Composition
        portfolio_frame = tk.LabelFrame(
            left_panel, text="Portfolio Composition", font=("Arial", 11, "bold"),
            bg=T.CARD_BG, relief=tk.RIDGE, bd=2
        )
        portfolio_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        portfolio_scroll = tk.Scrollbar(portfolio_frame)
        portfolio_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        portfolio_text = tk.Text(
            portfolio_frame, height=12, width=30, font=("Courier", 9), bg=T.CARD_BG,
            yscrollcommand=portfolio_scroll.set, relief=tk.FLAT
        )
        portfolio_scroll.config(command=portfolio_text.yview)
        portfolio_text.insert("1.0", "Ticker    Weight\n")
        portfolio_text.insert("end", "-" * 25 + "\n")
        for ticker, weight in weights_raw.items():
            portfolio_text.insert("end", f"{ticker:<10}{weight*100:>6.1f}%\n")
        portfolio_text.insert("end", "-" * 25 + "\n")
        portfolio_text.insert("end", f"{'TOTAL':<10}{sum(weights_raw.values())*100:>6.1f}%\n")
        portfolio_text.config(state=tk.DISABLED)
        portfolio_text.pack(padx=5, pady=5)
        
        # Benchmarks list
        benchmark_frame = tk.LabelFrame(
            left_panel, text="Benchmarks", font=("Arial", 11, "bold"), bg=T.CARD_BG,
            relief=tk.RIDGE, bd=2
        )
        benchmark_frame.pack(fill=tk.BOTH, expand=True)
        benchmark_text = tk.Text(benchmark_frame, height=8, width=30, font=("Courier", 9), bg=T.CARD_BG, relief=tk.FLAT)
        benchmark_text.insert("1.0", "Index          Ticker\n")
        benchmark_text.insert("end", "-" * 25 + "\n")
        for label, ticker in bench_def:
            benchmark_text.insert("end", f"{label:<15}{ticker}\n")
        benchmark_text.config(state=tk.DISABLED)
        benchmark_text.pack(padx=5, pady=5)
        
        return left_panel, portfolio_text, benchmark_text
    
    @staticmethod
    def create_ticker_card(parent, callbacks):
        """
        Create ticker input card with weight management
        
        Args:
            parent: Parent widget
            callbacks: Dictionary of callback functions
                - on_focus_in: callback(entry, placeholder)
                - queue_validate: callback(kind, idx)
                - on_type: callback(kind, idx)
                - focus_dropdown: callback(kind, idx)
                - hide_dropdown: callback(kind, idx)
                - update_weight_total: callback()
                - normalize_weights: callback()
        
        Returns:
            tuple: (card_frame, ticker_rows, weight_total_label, weight_normalize_btn)
        """
        tickers_card = tk.Frame(parent, bg=T.CARD_BG, relief=tk.RIDGE, bd=2)
        tickers_card.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 5))
        
        tickers_header = tk.Frame(tickers_card, bg=T.PANEL_HEADER)
        tickers_header.pack(fill=tk.X)
        tk.Label(
            tickers_header, text="Tickers (max 10)", font=("Arial", 11, "bold"),
            bg=T.PANEL_HEADER, fg=T.TEXT_ON_DARK, padx=10, pady=6
        ).pack(side=tk.LEFT)
        
        tickers_body = tk.Frame(tickers_card, bg=T.CARD_BG)
        tickers_body.pack(fill=tk.BOTH, expand=True, padx=10, pady=(10, 5))
        
        ticker_rows = []
        
        for i in range(10):
            row = tk.Frame(tickers_body, bg=T.CARD_BG)
            row.pack(fill=tk.X, pady=3)
            num = tk.Label(row, text=f"{i+1:02}", width=3, font=("Courier", 9, "bold"), fg=T.WARNING, bg=T.INPUT_BG_FOCUS)
            num.pack(side=tk.LEFT, padx=(0, 6))
            placeholder = f"Ticker {i+1}"
            ent = tk.Entry(row, width=18, font=("Arial", 10), fg=T.TEXT_MUTED, bg=T.INPUT_BG, relief=tk.FLAT)
            ent.insert(0, placeholder)
            ent.pack(side=tk.LEFT, fill=tk.X, expand=True)
            
            # Weight entry field (%)
            weight_ent = tk.Entry(row, width=6, font=("Arial", 9), fg=T.TEXT_PRIMARY, bg=T.INPUT_BG_FOCUS, relief=tk.FLAT, justify="center")
            weight_ent.insert(0, "10.0")
            weight_ent.pack(side=tk.LEFT, padx=(4, 2))
            tk.Label(row, text="%", font=("Arial", 9), fg=T.TEXT_SECONDARY, bg=T.CARD_BG).pack(side=tk.LEFT, padx=(0, 4))
            
            # Amount entry field (currency)
            amount_ent = tk.Entry(row, width=8, font=("Arial", 9), fg=T.TEXT_PRIMARY, bg=T.HIGHLIGHT, relief=tk.FLAT, justify="center")
            amount_ent.insert(0, "1,000")
            amount_ent.pack(side=tk.LEFT, padx=(4, 0))
            
            # Currency label (will be updated dynamically)
            currency_lbl = tk.Label(row, text="$", font=("Arial", 9), fg=T.TEXT_SECONDARY, bg=T.CARD_BG)
            currency_lbl.pack(side=tk.LEFT, padx=(2, 4))
            
            status_lbl = tk.Label(row, text="•", font=("Arial", 12, "bold"), fg=T.TEXT_MUTED, bg=T.CARD_BG)
            status_lbl.pack(side=tk.RIGHT, padx=(6, 0))
            
            # Bind callbacks (autocomplete disabled - only validation on FocusOut/Return)
            ent.bind("<FocusIn>", lambda e, entry=ent, ph=placeholder: callbacks['on_focus_in'](entry, ph))
            ent.bind("<FocusOut>", lambda e, idx=i: callbacks['queue_validate']("ticker", idx))
            ent.bind("<Return>", lambda e, idx=i: callbacks['queue_validate']("ticker", idx))
            
            # Update total and sync fields on weight change
            weight_ent.bind("<KeyRelease>", lambda e, idx=i: callbacks['on_weight_change'](idx))
            weight_ent.bind("<FocusOut>", lambda e, idx=i: callbacks['on_weight_change'](idx))
            
            # Sync weight when amount changes
            amount_ent.bind("<KeyRelease>", lambda e, idx=i: callbacks['on_amount_change'](idx))
            amount_ent.bind("<FocusOut>", lambda e, idx=i: callbacks['on_amount_change'](idx))
            
            # Add label for instrument name display
            name_lbl = tk.Label(row, text="", font=("Arial", 8, "italic"), fg=T.TEXT_SECONDARY, bg=T.CARD_BG, anchor="w")
            name_lbl.pack(side=tk.LEFT, padx=(6, 0))
            
            ticker_rows.append({
                "entry": ent, "status": status_lbl, "placeholder": placeholder,
                "weight_entry": weight_ent, "amount_entry": amount_ent, 
                "currency_label": currency_lbl, "name_label": name_lbl,
                "sugg_top": None, "sugg_list": None, "after_id": None,
                "isin_info": None
            })
        
        # Total weight display
        total_frame = tk.Frame(tickers_card, bg=T.INPUT_BG_FOCUS, relief=tk.FLAT, bd=1)
        total_frame.pack(fill=tk.X, padx=10, pady=(5, 10))
        tk.Label(total_frame, text="TOTAL:", font=("Arial", 9, "bold"), bg=T.INPUT_BG_FOCUS, fg=T.WARNING).pack(side=tk.LEFT, padx=(5, 10))
        weight_total_label = tk.Label(total_frame, text="100.0%", font=("Arial", 10, "bold"), bg=T.INPUT_BG_FOCUS, fg=T.PANEL_HEADER)
        weight_total_label.pack(side=tk.LEFT)
        
        # Dropdown button for weight management
        weight_btn_frame = tk.Frame(total_frame, bg=T.INPUT_BG_FOCUS)
        weight_btn_frame.pack(side=tk.RIGHT, padx=5)
        
        weight_normalize_btn = tk.Menubutton(
            weight_btn_frame, text="Equilibrer ▼", font=("Arial", 8, "bold"), 
            bg=T.SUCCESS, fg=T.TEXT_ON_DARK, relief=tk.RAISED, padx=10, pady=4, 
            cursor="hand2", direction="below", borderwidth=2
        )
        weight_normalize_btn.pack()
        
        # Create dropdown menu
        weight_menu = tk.Menu(weight_normalize_btn, tearoff=0, font=("Arial", 9))
        weight_menu.add_command(label="Equilibrer (normaliser a 100%)", command=callbacks['normalize_weights'])
        weight_menu.add_separator()
        weight_menu.add_command(label="Poids egaux", command=callbacks.get('equal_weights', callbacks['normalize_weights']))
        weight_menu.add_command(label="Effacer les poids", command=callbacks.get('clear_weights', callbacks['normalize_weights']))
        weight_menu.add_command(label="Effacer tout le portefeuille", command=callbacks.get('clear_portfolio', callbacks['normalize_weights']))
        
        weight_normalize_btn['menu'] = weight_menu
        
        return tickers_card, ticker_rows, weight_total_label, weight_normalize_btn
    
    @staticmethod
    def create_benchmark_card(parent, callbacks):
        """
        Create benchmark input card with pre-filled major market indexes
        
        Args:
            parent: Parent widget
            callbacks: Dictionary of callback functions
        
        Returns:
            tuple: (card_frame, benchmark_rows)
        """
        bench_card = tk.Frame(parent, bg=T.CARD_BG, relief=tk.RIDGE, bd=2)
        bench_card.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(5, 0))
        
        bench_header = tk.Frame(bench_card, bg=T.SUCCESS)
        bench_header.pack(fill=tk.X)
        tk.Label(
            bench_header, text="Benchmarks (max 6)", font=("Arial", 11, "bold"),
            bg=T.SUCCESS, fg=T.TEXT_ON_DARK, padx=10, pady=6
        ).pack(side=tk.LEFT)
        
        bench_body = tk.Frame(bench_card, bg=T.CARD_BG)
        bench_body.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        benchmark_rows = []
        
        for i in range(6):
            row = tk.Frame(bench_body, bg=T.CARD_BG)
            row.pack(fill=tk.X, pady=3)
            num = tk.Label(row, text=f"{i+1:02}", width=3, font=("Courier", 9, "bold"), fg=T.PANEL_HEADER, bg=T.HIGHLIGHT)
            num.pack(side=tk.LEFT, padx=(0, 6))
            placeholder = f"Benchmark {i+1}"
            ent = tk.Entry(row, width=20, font=("Arial", 10), fg=T.TEXT_MUTED, bg=T.INPUT_BG, relief=tk.FLAT)
            ent.insert(0, placeholder)
            ent.pack(side=tk.LEFT, fill=tk.X, expand=True)
            
            # Browse button for popular indexes
            browse_btn = tk.Button(
                row, text="...", font=("Arial", 9, "bold"),
                bg=T.HIGHLIGHT, fg=T.PANEL_HEADER, relief=tk.FLAT,
                width=2, cursor="hand2", padx=2, pady=0,
                command=lambda idx=i: callbacks.get('browse_benchmarks', lambda x: None)(idx)
            )
            browse_btn.pack(side=tk.LEFT, padx=(4, 4))
            
            status_lbl = tk.Label(row, text="•", font=("Arial", 12, "bold"), fg=T.TEXT_MUTED, bg=T.CARD_BG)
            status_lbl.pack(side=tk.RIGHT, padx=(6, 0))
            
            # Bind callbacks (autocomplete disabled - only validation on FocusOut/Return)
            ent.bind("<FocusIn>", lambda e, entry=ent, ph=placeholder: callbacks['on_focus_in'](entry, ph))
            ent.bind("<FocusOut>", lambda e, idx=i: callbacks['queue_validate']("bench", idx))
            ent.bind("<Return>", lambda e, idx=i: callbacks['queue_validate']("bench", idx))
            
            # Add label for instrument name display
            name_lbl = tk.Label(row, text="", font=("Arial", 8, "italic"), fg=T.TEXT_SECONDARY, bg=T.CARD_BG, anchor="w")
            name_lbl.pack(side=tk.LEFT, padx=(6, 0))
            
            benchmark_rows.append({
                "entry": ent, "status": status_lbl, "placeholder": placeholder,
                "name_label": name_lbl, "browse_btn": browse_btn,
                "sugg_top": None, "sugg_list": None, "after_id": None,
                "isin_info": None
            })
        
        return bench_card, benchmark_rows
    
    @staticmethod
    def create_info_panel(parent):
        """Create information/help panel"""
        info_frame = tk.LabelFrame(
            parent, text="How to enter tickers & benchmarks",
            font=("Arial", 11, "bold"), bg=T.CARD_BG, relief=tk.RIDGE, bd=2
        )
        info_frame.pack(fill=tk.X, pady=(0, 10))
        
        info_text_main = (
            "- Yahoo Finance tickers (preferred) - A green checkmark confirms validity.\n"
            "- ISIN codes - Auto-converted to tickers (ex: FR0000120271 → TTE.PA for TotalEnergies).\n"
            "- European ETFs - Auto-suffix resolution (ex: ANXU → ANXU.PA automatically).\n"
            "- Smart Benchmarks - Click any benchmark field to see 14 popular global indexes (S&P 500, Nasdaq, DAX, CAC 40, Nikkei, etc.)\n"
            "Add exchange suffix for non-US: .PA (Paris), .MI (Milan), .L (London), .AS (Amsterdam), .BR (Brussels), .MC (Madrid), .SW (Zurich), .DE (XETRA).\n"
            "ETF examples: CW8.PA, VUSA.L, CSPX.L, IWDA.AS, GLDA.DE."
        )
        tk.Label(info_frame, text=info_text_main, font=("Arial", 9), bg=T.CARD_BG, fg="#555", justify="left", anchor="w",
                 wraplength=820, padx=10, pady=8).pack(fill=tk.X, pady=(0, 4))
        
        # Warning about Amundi ETFs
        warning_frame = tk.Frame(info_frame, bg=T.INPUT_BG_FOCUS, relief=tk.FLAT, bd=1)
        warning_frame.pack(fill=tk.X, padx=10, pady=8)
        tk.Label(
            warning_frame,
            text="WARNING: Yahoo Finance has limited coverage for Amundi ETFs. Some may not be available or have incomplete data. Prefer ETFs from Vanguard, iShares, or SPDR for better availability.",
            font=("Arial", 8), bg=T.INPUT_BG_FOCUS, fg=T.WARNING, justify="left", anchor="w",
            wraplength=800, padx=8, pady=6
        ).pack(fill=tk.X)
        
        return info_frame
    
    @staticmethod
    def create_chart_selector(parent, chart_groups, chart_names):
        """
        Create chart selector with checkboxes
        
        Args:
            parent: Parent widget
            chart_groups: Dictionary of chart groups
            chart_names: Dictionary of chart names
        
        Returns:
            tuple: (selection_frame, chart_vars dict)
        """
        selection_frame = tk.Frame(parent, bg=T.CARD_BG, relief=tk.RIDGE, bd=2)
        selection_frame.pack(fill=tk.BOTH, expand=True)
        
        canvas = tk.Canvas(selection_frame, bg=T.CARD_BG, highlightthickness=0)
        scrollbar = ttk.Scrollbar(selection_frame, orient="vertical", command=canvas.yview)
        scrollable = tk.Frame(canvas, bg=T.CARD_BG)
        scrollable.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=scrollable, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        def _on_mousewheel(event):
            canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
        canvas.bind_all("<MouseWheel>", _on_mousewheel)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        chart_vars = {}
        
        for group_name, chart_numbers in chart_groups.items():
            group_frame = tk.Frame(scrollable, bg=T.BORDER, relief=tk.RAISED, bd=1)
            group_frame.pack(fill=tk.X, padx=10, pady=(10, 5))
            group_label = tk.Label(group_frame, text=group_name, font=("Arial", 11, "bold"), bg=T.BORDER, fg=T.TEXT_PRIMARY)
            group_label.pack(anchor="w", padx=10, pady=5)
            
            for chart_num in chart_numbers:
                var = tk.BooleanVar(value=True)
                chart_vars[chart_num] = var
                cb = tk.Checkbutton(
                    scrollable, text=f"Chart {chart_num}: {chart_names[chart_num]}",
                    variable=var, font=("Arial", 10), bg=T.CARD_BG, anchor="w",
                    activebackground=T.CARD_BG, selectcolor=T.SUCCESS
                )
                cb.pack(fill=tk.X, padx=30, pady=2)
        
        return selection_frame, chart_vars
    
    @staticmethod
    def create_status_panel(parent):
        """Create status label panel"""
        control_panel = tk.Frame(parent, bg=T.MAIN_BG)
        control_panel.pack(fill=tk.X, pady=(10, 4))
        status_label = tk.Label(
            control_panel,
            text="Ready - Select charts and click RUN ANALYSIS",
            font=("Arial", 9), bg=T.MAIN_BG, fg=T.TEXT_SECONDARY
        )
        status_label.pack(pady=(0, 6))
        return control_panel, status_label
    
    @staticmethod
    def create_bottom_toolbar(parent, callbacks):
        """
        Create bottom toolbar with action buttons
        
        Args:
            parent: Parent widget
            callbacks: Dictionary with select_all, deselect_all, run_analysis
        
        Returns:
            tk.Frame: Toolbar frame
        """
        bottom_toolbar = tk.Frame(parent, bg=T.BORDER, bd=2, relief=tk.RIDGE)
        bottom_toolbar.pack(side=tk.BOTTOM, fill=tk.X, pady=(20, 0))
        
        bwrap = tk.Frame(bottom_toolbar, bg=T.BORDER)
        bwrap.pack(pady=10)
        
        tk.Button(
            bwrap, text="✓ Select All", command=callbacks['select_all'],
            font=("Arial", 12, "bold"), bg=T.PRIMARY, fg=T.TEXT_ON_DARK,
            padx=32, pady=14, relief=tk.RAISED, bd=4, cursor="hand2",
            activebackground=T.PRIMARY
        ).grid(row=0, column=0, padx=10)
        
        tk.Button(
            bwrap, text="✗ Deselect All", command=callbacks['deselect_all'],
            font=("Arial", 12, "bold"), bg=T.WARNING, fg=T.TEXT_ON_DARK,
            padx=32, pady=14, relief=tk.RAISED, bd=4, cursor="hand2",
            activebackground=T.WARNING
        ).grid(row=0, column=1, padx=10)
        
        tk.Button(
            bwrap, text="▶ RUN ANALYSIS", command=callbacks['run_analysis'],
            font=("Arial", 14, "bold"), bg=T.SUCCESS, fg=T.TEXT_ON_DARK,
            padx=40, pady=16, relief=tk.RAISED, bd=4, cursor="hand2",
            activebackground=T.PANEL_HEADER
        ).grid(row=0, column=2, padx=10)
        
        return bottom_toolbar

