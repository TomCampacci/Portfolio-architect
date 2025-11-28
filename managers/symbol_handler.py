# symbol_handler.py - Symbol Validation and Autocompletion Handler
import tkinter as tk
import threading
import re
from utils.utils_data import (
    validate_yahoo_symbol, is_isin, isin_to_ticker,
    search_yahoo_symbols, generate_symbol_heuristics,
    auto_resolve_european_suffix, get_popular_benchmarks
)
from ui.theme_colors import LightPremiumTheme as T


class SymbolValidator:
    """Pure logic for symbol validation and conversion (agnostic)"""
    
    @staticmethod
    def sanitize_symbols(symbols):
        """
        Clean and validate a list of symbols
        
        Args:
            symbols: List of symbol strings
        
        Returns:
            list: Cleaned and validated symbols
        """
        allowed = re.compile(r"^[A-Z0-9^=.+-]{1,20}$")
        blocklist = {"NASDAQ", "INDEX", "STOCKS", "EQUITY", "FUTURES"}
        cleaned = []
        
        for s in symbols:
            if not s:
                continue
            sym = s.strip().upper()
            # Remove stray unicode/non-ascii
            sym = ''.join(ch for ch in sym if ord(ch) < 128)
            if not allowed.match(sym):
                continue
            if sym in blocklist:
                continue
            if sym not in cleaned:
                cleaned.append(sym)
        
        # Final pass: keep only those that still validate
        valid = [sym for sym in cleaned if validate_yahoo_symbol(sym)]
        return valid
    
    @staticmethod
    def validate_symbol(symbol, return_name=False):
        """
        Validate a symbol via Yahoo Finance
        
        Args:
            symbol: Symbol string to validate
            return_name: If True, also return instrument name
        
        Returns:
            bool or tuple: Valid status, optionally with name
        """
        return validate_yahoo_symbol(symbol, return_name=return_name)
    
    @staticmethod
    def convert_isin(isin_code):
        """
        Convert ISIN to ticker
        
        Args:
            isin_code: ISIN code string
        
        Returns:
            dict or None: Conversion result with ticker, name, exchange
        """
        if not is_isin(isin_code):
            return None
        return isin_to_ticker(isin_code)
    
    @staticmethod
    def is_isin_code(code):
        """Check if code is a valid ISIN"""
        return is_isin(code)


class SymbolUIHandler:
    """UI-specific symbol handling (Tkinter-dependent)"""
    
    def __init__(self, root, ticker_rows, benchmark_rows, local_ticker_hints, local_bench_hints, on_validation_complete=None):
        """
        Initialize symbol UI handler
        
        Args:
            root: Tkinter root window
            ticker_rows: List of ticker row dictionaries
            benchmark_rows: List of benchmark row dictionaries
            local_ticker_hints: List of local ticker hints for fallback
            local_bench_hints: List of local benchmark hints for fallback
            on_validation_complete: Optional callback(kind) called after validation
        """
        self.root = root
        self.ticker_rows = ticker_rows
        self.benchmark_rows = benchmark_rows
        self.local_ticker_hints = local_ticker_hints
        self.local_bench_hints = local_bench_hints
        self.dropdown_item_height = 18
        self.on_validation_complete = on_validation_complete
        
        # Global dropdown references (currently unused but kept for future)
        self.global_ticker_top = None
        self.global_ticker_list = None
        self.global_bench_top = None
        self.global_bench_list = None
        
        # ISIN exchange selection dialog state
        self.isin_selection_dialog = None
        self.isin_selected_exchange = None
    
    def on_focus_in(self, entry, placeholder, kind=None, idx=None):
        """
        Handle focus in event for entry widgets
        
        Args:
            entry: Entry widget
            placeholder: Placeholder text
            kind: "ticker" or "bench" (optional)
            idx: Row index (optional)
        """
        try:
            if entry.get() == placeholder and entry.cget("fg") == "T.TEXT_MUTED":
                entry.delete(0, tk.END)
                entry.config(fg=T.TEXT_PRIMARY)
        except Exception:
            pass
    
    def show_benchmark_selection(self, kind, idx):
        """
        Show a dialog with popular benchmark indexes
        
        Args:
            kind: "bench"
            idx: Row index
        """
        if self.isin_selection_dialog:
            try:
                self.isin_selection_dialog.destroy()
            except:
                pass
        
        # Create modal dialog
        dialog = tk.Toplevel(self.root)
        dialog.title("Select Benchmark Index")
        dialog.geometry("700x500")
        dialog.transient(self.root)
        dialog.grab_set()
        
        self.isin_selection_dialog = dialog
        self.isin_selected_exchange = None
        
        # Header
        header_frame = tk.Frame(dialog, bg=T.SUCCESS, height=60)
        header_frame.pack(fill=tk.X)
        header_frame.pack_propagate(False)
        
        tk.Label(
            header_frame, text="Select a Benchmark Index",
            font=("Arial", 14, "bold"), bg=T.SUCCESS, fg=T.TEXT_ON_DARK
        ).pack(pady=18)
        
        # Body
        body_frame = tk.Frame(dialog, bg=T.CARD_BG)
        body_frame.pack(fill=tk.X, padx=20, pady=20)
        
        # Create scrollable list with fixed height
        list_frame = tk.Frame(body_frame, bg=T.CARD_BG, height=300)
        list_frame.pack(fill=tk.X)
        list_frame.pack_propagate(False)
        
        canvas = tk.Canvas(list_frame, bg=T.CARD_BG, highlightthickness=0)
        scrollbar = tk.Scrollbar(list_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg=T.CARD_BG)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Radio button variable
        selected_var = tk.StringVar()
        
        # Popular benchmarks organized by region
        from utils.utils_data import get_popular_benchmarks
        popular_benchmarks = get_popular_benchmarks()
        
        # Organize by region
        regions = {
            "United States": [],
            "Europe": [],
            "Asia Pacific": [],
            "Commodities": []
        }
        
        for bench in popular_benchmarks:
            symbol = bench["symbol"]
            name = bench["name"]
            
            if "S&P" in name or "Nasdaq" in name or "Dow Jones" in name:
                regions["United States"].append(bench)
            elif "DAX" in name or "CAC" in name or "FTSE" in name or "Stoxx" in name or "IBEX" in name or "MIB" in name:
                regions["Europe"].append(bench)
            elif "Nikkei" in name or "Hang Seng" in name:
                regions["Asia Pacific"].append(bench)
            elif "Gold" in name or "Oil" in name:
                regions["Commodities"].append(bench)
        
        # Add options by region
        first = True
        for region_name, benchmarks in regions.items():
            if not benchmarks:
                continue
            
            # Region header
            region_header = tk.Frame(scrollable_frame, bg=T.HIGHLIGHT, height=35)
            region_header.pack(fill=tk.X, pady=(10 if not first else 0, 5))
            region_header.pack_propagate(False)
            
            tk.Label(
                region_header, text=region_name,
                font=("Arial", 10, "bold"), bg=T.HIGHLIGHT, fg=T.PANEL_HEADER
            ).pack(side=tk.LEFT, padx=15, pady=8)
            
            # Add benchmarks
            for i, bench in enumerate(benchmarks):
                symbol = bench["symbol"]
                name = bench["name"]
                
                # Create radio button option
                option_frame = tk.Frame(scrollable_frame, bg=T.INPUT_BG_FOCUS, relief=tk.RAISED, bd=1)
                option_frame.pack(fill=tk.X, pady=3, padx=10)
                
                rb = tk.Radiobutton(
                    option_frame,
                    variable=selected_var,
                    value=symbol,
                    bg=T.INPUT_BG_FOCUS,
                    activebackground=T.HIGHLIGHT,
                    command=lambda s=symbol: None
                )
                rb.pack(side=tk.LEFT, padx=10, pady=8)
                
                info_frame = tk.Frame(option_frame, bg=T.INPUT_BG_FOCUS)
                info_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)
                
                tk.Label(
                    info_frame, text=symbol,
                    font=("Arial", 10, "bold"), bg=T.INPUT_BG_FOCUS, anchor="w"
                ).pack(anchor="w")
                
                tk.Label(
                    info_frame, text=name,
                    font=("Arial", 9), bg=T.INPUT_BG_FOCUS, fg=T.TEXT_SECONDARY, anchor="w"
                ).pack(anchor="w")
                
                # Select first option by default
                if first and i == 0:
                    selected_var.set(symbol)
                    first = False
        
        # Buttons
        button_frame = tk.Frame(dialog, bg=T.CARD_BG)
        button_frame.pack(fill=tk.X, padx=20, pady=(0, 20))
        
        def on_confirm():
            self.isin_selected_exchange = selected_var.get()
            dialog.destroy()
            # Fill the entry with selected benchmark
            if self.isin_selected_exchange:
                rows = self.benchmark_rows
                row = rows[idx]
                entry = row["entry"]
                entry.delete(0, tk.END)
                entry.insert(0, self.isin_selected_exchange)
                entry.config(fg=T.TEXT_PRIMARY)
                
                # Directly validate the benchmark without re-checking multi-exchanges
                def worker():
                    # Validate the selected ticker
                    result = SymbolValidator.validate_symbol(self.isin_selected_exchange, return_name=True)
                    if isinstance(result, tuple):
                        ok, instrument_name = result
                    else:
                        ok = result
                        instrument_name = ""
                    
                    def finalize():
                        if ok:
                            self.apply_validation(kind, idx, True)
                            
                            # Display instrument name
                            name_label = row.get("name_label")
                            if name_label and instrument_name:
                                display_name = instrument_name[:30] + "..." if len(instrument_name) > 30 else instrument_name
                                name_label.config(text=display_name, fg=T.TEXT_SECONDARY)
                            
                            entry.config(bg=T.CARD_BG)
                        else:
                            self.apply_validation(kind, idx, False)
                            entry.config(bg=T.CARD_BG)
                    
                    self.root.after(0, finalize)
                
                thread = threading.Thread(target=worker, daemon=True)
                thread.start()
        
        def on_cancel():
            dialog.destroy()
        
        tk.Button(
            button_frame, text="Cancel", command=on_cancel,
            font=("Arial", 10), bg=T.BORDER, fg=T.TEXT_PRIMARY,
            padx=20, pady=8, relief=tk.FLAT, cursor="hand2"
        ).pack(side=tk.LEFT, padx=(0, 10))
        
        tk.Button(
            button_frame, text="Confirm", command=on_confirm,
            font=("Arial", 10, "bold"), bg=T.SUCCESS, fg=T.TEXT_ON_DARK,
            padx=20, pady=8, relief=tk.FLAT, cursor="hand2"
        ).pack(side=tk.RIGHT)
        
        # Center dialog
        dialog.update_idletasks()
        x = (dialog.winfo_screenwidth() // 2) - (dialog.winfo_width() // 2)
        y = (dialog.winfo_screenheight() // 2) - (dialog.winfo_height() // 2)
        dialog.geometry(f"+{x}+{y}")
    
    def show_exchange_selection(self, query, exchanges_data, kind, idx, is_isin=False):
        """
        Show a dialog to let user choose which exchange to use for a symbol
        
        Args:
            query: The symbol or ISIN entered
            exchanges_data: List of dicts with exchange options
            kind: "ticker" or "bench"
            idx: Row index
            is_isin: Whether this is an ISIN code
        """
        if self.isin_selection_dialog:
            try:
                self.isin_selection_dialog.destroy()
            except:
                pass
        
        # Use modern enhanced dialog
        from ui.modern_ui_builder import ModernUIBuilder
        
        dialog, selected_var = ModernUIBuilder.create_enhanced_exchange_dialog(
            self.root, query, exchanges_data, is_isin
        )
        
        self.isin_selection_dialog = dialog
        self.isin_selected_exchange = None
        
        # Wait for dialog to close
        self.root.wait_window(dialog)
        
        # Get selected ticker and name
        selected_ticker = selected_var.get()
        
        if selected_ticker:
            self.isin_selected_exchange = selected_ticker
            
            # Find the exchange data for the selected ticker to get the name
            instrument_name = ""
            for data in exchanges_data:
                ticker_val = data.get('ticker') or data.get('symbol', '')
                if ticker_val == selected_ticker:
                    instrument_name = data.get('name', '')
                    break
            
            # Update the entry with selected ticker
            rows = self.ticker_rows if kind == "ticker" else self.benchmark_rows
            if 0 <= idx < len(rows):
                entry = rows[idx]["entry"]
                entry.delete(0, tk.END)
                entry.insert(0, selected_ticker)
                entry.config(fg=T.TEXT_PRIMARY, bg=T.CARD_BG)
                
                # Mark this row as "just selected from exchange dialog" to prevent reopening
                rows[idx]["_skip_exchange_check"] = True
                
                # Validate and show name
                def worker():
                    # Validate the selected ticker
                    result = SymbolValidator.validate_symbol(selected_ticker, return_name=True)
                    if isinstance(result, tuple):
                        ok, validated_name = result
                        final_name = validated_name if validated_name else instrument_name
                    else:
                        ok = result
                        final_name = instrument_name
                    
                    def finalize():
                        if ok:
                            self.apply_validation(kind, idx, True)
                            
                            # Display instrument name prominently
                            name_label = rows[idx].get("name_label")
                            if name_label and final_name:
                                # Display full name without truncation for better visibility
                                display_name = final_name[:50] + "..." if len(final_name) > 50 else final_name
                                name_label.config(text=display_name, fg=T.SUCCESS, font=("Segoe UI", 9, "bold"))
                        else:
                            self.apply_validation(kind, idx, False)
                        
                        # Clear the skip flag after validation is complete
                        if "_skip_exchange_check" in rows[idx]:
                            del rows[idx]["_skip_exchange_check"]
                    
                    self.root.after(0, finalize)
                
                thread = threading.Thread(target=worker, daemon=True)
                thread.start()
        
        return
    
    def get_symbol(self, entry, placeholder):
        """
        Extract and normalize symbol from entry widget
        
        Args:
            entry: Entry widget
            placeholder: Placeholder text
        
        Returns:
            str: Normalized symbol or empty string
        """
        try:
            val = entry.get()
            # Normalize: strip spaces and non-ascii, keep only allowed chars
            val = val.strip().upper()
            # Remove common UI adorners like EM DASH, hyphens around
            val = val.replace("—", "").replace("–", "").strip()
            allowed = re.compile(r"[^A-Z0-9^=.+-]")
            val = allowed.sub("", val)
            if not val or val == placeholder.upper():
                return ""
            return val
        except Exception:
            return ""
    
    def queue_validate(self, kind, idx):
        """
        Queue symbol validation in a background thread
        
        Args:
            kind: "ticker" or "bench"
            idx: Row index
        """
        rows = self.ticker_rows if kind == "ticker" else self.benchmark_rows
        if idx < 0 or idx >= len(rows):
            return
        row = rows[idx]
        entry = row["entry"]
        placeholder = row["placeholder"]
        name_label = row.get("name_label")
        symbol = self.get_symbol(entry, placeholder)
        
        if not symbol:
            self.apply_validation(kind, idx, None)
            if name_label:
                name_label.config(text="")
            return
        
        row["status"].config(text="…", fg=T.STATUS_PENDING)
        entry.config(bg=T.INPUT_BG_FOCUS)
        
        def worker():
            # Check if it's an ISIN first
            converted_ticker = symbol
            instrument_name = ""
            is_isin_code = False
            eu_resolved = False
            
            if SymbolValidator.is_isin_code(symbol):
                is_isin_code = True
                def update_status():
                    row["status"].config(text="🔍", fg=T.WARNING)
                    if name_label:
                        name_label.config(text=f"ISIN detected: {symbol}", fg=T.WARNING, font=("Segoe UI", 9, "italic"))
                self.root.after(0, update_status)
                
                # Get all available exchanges for this ISIN
                from utils.utils_data import isin_to_ticker_openfigi
                all_exchanges = isin_to_ticker_openfigi(symbol, return_all_exchanges=True)
                
                if all_exchanges and len(all_exchanges) > 1:
                    # Multiple exchanges available - show selection dialog with instrument name
                    def show_dialog():
                        # Update status to show we found it
                        if name_label and all_exchanges[0].get('name'):
                            instr_name = all_exchanges[0].get('name', '')
                            name_label.config(text=f"✓ {instr_name} - Select exchange", fg=T.SUCCESS, font=("Segoe UI", 9, "bold"))
                        self.show_exchange_selection(symbol, all_exchanges, kind, idx, is_isin=True)
                    self.root.after(0, show_dialog)
                    return
                elif all_exchanges and len(all_exchanges) == 1:
                    # Only one exchange - use it directly and auto-convert
                    conversion = all_exchanges[0]
                    converted_ticker = conversion["ticker"]
                    instrument_name = conversion["name"]
                    row["isin_info"] = conversion
                    
                    # Auto-convert the ISIN to ticker in the entry field
                    def auto_convert():
                        entry.delete(0, tk.END)
                        entry.insert(0, converted_ticker)
                        entry.config(fg=T.SUCCESS)
                        if name_label and instrument_name:
                            name_label.config(text=f"✓ ISIN → {instrument_name}", fg=T.SUCCESS, font=("Segoe UI", 9, "bold"))
                    self.root.after(0, auto_convert)
                else:
                    # ISIN not found
                    def show_error():
                        self.apply_validation(kind, idx, False)
                        if name_label:
                            name_label.config(text=f"❌ ISIN not found: {symbol}", fg=T.ERROR, font=("Segoe UI", 9))
                    self.root.after(0, show_error)
                    return
            
            # Before validating, check if this symbol has multiple exchanges available
            # Skip if symbol is already fully qualified:
            # - Has exchange suffix (contains dot, e.g., VWCE.DE, LVMH.PA)
            # - Is an index (starts with ^, e.g., ^GSPC, ^NDX)
            # - Is a future (contains =, e.g., GC=F, CL=F)
            # - Is a crypto (ends with -USD, -EUR, etc.)
            is_already_qualified = (
                is_isin_code or
                '.' in converted_ticker or
                converted_ticker.startswith('^') or
                '=' in converted_ticker or
                converted_ticker.endswith(('-USD', '-EUR', '-GBP', '-BTC'))
            )
            
            # Check if we should skip the exchange check (just selected from dialog)
            row = self.ticker_rows[idx] if kind == "ticker" else self.benchmark_rows[idx]
            skip_check = row.get("_skip_exchange_check", False)
            
            if not is_already_qualified and not skip_check:
                from utils.utils_data import search_symbol_all_exchanges
                
                # Search for all exchanges (filtered for major exchanges only)
                multiple_exchanges = search_symbol_all_exchanges(converted_ticker, max_results=10)
                
                if multiple_exchanges and len(multiple_exchanges) > 1:
                    # Multiple exchanges found - show selection dialog
                    def show_dialog():
                        self.show_exchange_selection(converted_ticker, multiple_exchanges, kind, idx, is_isin=False)
                    self.root.after(0, show_dialog)
                    return
            
            # Validate the ticker (original or converted from ISIN)
            # Request name if we don't have it from ISIN conversion
            if not instrument_name:
                result = SymbolValidator.validate_symbol(converted_ticker, return_name=True)
                if isinstance(result, tuple):
                    ok, instrument_name = result
                else:
                    ok = result
            else:
                ok = SymbolValidator.validate_symbol(converted_ticker)
            
            # If validation failed and symbol looks like a European ticker (short, no suffix),
            # try auto-resolving with EU suffixes
            if not ok and not is_isin_code and '.' not in converted_ticker and len(converted_ticker) <= 6:
                def update_resolving():
                    row["status"].config(text="...", fg=T.WARNING)
                self.root.after(0, update_resolving)
                
                # Try EU suffix resolution
                resolved_result = auto_resolve_european_suffix(converted_ticker, return_name=True)
                if resolved_result and resolved_result[0]:
                    resolved_ticker, resolved_name = resolved_result
                    converted_ticker = resolved_ticker
                    instrument_name = resolved_name or ""
                    ok = True
                    eu_resolved = True
            
            def finalize():
                if ok:
                    try:
                        current = entry.get().strip().upper()
                        # Update entry with converted ticker
                        if is_isin_code and converted_ticker != current:
                            # ISIN conversion
                            entry.delete(0, tk.END)
                            entry.insert(0, converted_ticker)
                            entry.config(fg=T.TEXT_PRIMARY)
                        elif eu_resolved and converted_ticker != current:
                            # EU suffix auto-resolved
                            entry.delete(0, tk.END)
                            entry.insert(0, converted_ticker)
                            entry.config(fg=T.TEXT_PRIMARY)
                        elif not is_isin_code and not eu_resolved and current != symbol:
                            # Regular symbol, normalize
                            entry.delete(0, tk.END)
                            entry.insert(0, symbol)
                            entry.config(fg=T.TEXT_PRIMARY)
                        
                        # Display instrument name prominently (no emojis, just the name)
                        if name_label and instrument_name:
                            # Allow longer names for better visibility - up to 60 chars
                            short_name = instrument_name[:60] + "..." if len(instrument_name) > 60 else instrument_name
                            # Use more visible color and bold font
                            name_label.config(text=short_name, fg=T.TEXT_PRIMARY, font=("Segoe UI", 9, "bold"))
                    except Exception as e:
                        print(f"Error updating UI: {e}")
                elif name_label:
                    name_label.config(text="", fg=T.TEXT_SECONDARY, font=("Segoe UI", 9))
                
                self.apply_validation(kind, idx, ok)
            self.root.after(0, finalize)
        
        threading.Thread(target=worker, daemon=True).start()
    
    def apply_validation(self, kind, idx, ok):
        """
        Apply validation result to UI
        
        Args:
            kind: "ticker" or "bench"
            idx: Row index
            ok: Validation result (True/False/None)
        """
        rows = self.ticker_rows if kind == "ticker" else self.benchmark_rows
        if idx < 0 or idx >= len(rows):
            return
        row = rows[idx]
        entry = row["entry"]
        status = row["status"]
        
        if ok is True:
            status.config(text="✓", fg=T.PANEL_HEADER)
            entry.config(bg=T.HIGHLIGHT)
        elif ok is False:
            status.config(text="✗", fg=T.ERROR)
            entry.config(bg=T.INPUT_BG_FOCUS)
        else:
            status.config(text="•", fg=T.TEXT_MUTED)
            base = T.INPUT_BG if kind == "ticker" else T.INPUT_BG
            entry.config(bg=base)
        
        # Call validation complete callback if provided
        if self.on_validation_complete:
            try:
                self.on_validation_complete(kind)
            except Exception as e:
                print(f"Error in validation callback: {e}")
    
    def on_type(self, kind, idx):
        """
        Handle typing in entry widget - DISABLED (direct exchange selection on validation)
        
        Args:
            kind: "ticker" or "bench"
            idx: Row index
        """
        # Autocomplete dropdown disabled - we show exchange selection directly on validation
        pass
    
    def ensure_dropdown(self, kind, idx):
        """
        Ensure dropdown exists for the given row
        
        Args:
            kind: "ticker" or "bench"
            idx: Row index
        
        Returns:
            tuple: (Toplevel window, Listbox widget)
        """
        rows = self.ticker_rows if kind == "ticker" else self.benchmark_rows
        row = rows[idx]
        
        if row.get("sugg_top") and row.get("sugg_list"):
            return row["sugg_top"], row["sugg_list"]
        
        top = tk.Toplevel(self.root)
        top.overrideredirect(True)
        top.attributes("-topmost", True)
        lb = tk.Listbox(top, height=6, activestyle="dotbox", bg=T.CARD_BG, fg=T.TEXT_PRIMARY, bd=1, relief=tk.SOLID)
        lb.pack(fill=tk.BOTH, expand=True)
        lb.bind("<<ListboxSelect>>", lambda e, k=kind, i=idx: self.pick_suggestion(k, i))
        lb.bind("<Return>", lambda e, k=kind, i=idx: self.pick_suggestion(k, i))
        lb.bind("<Escape>", lambda e, k=kind, i=idx: self.hide_dropdown(k, i))
        row["sugg_top"] = top
        row["sugg_list"] = lb
        return top, lb
    
    def place_dropdown(self, kind, idx):
        """
        Position dropdown below entry widget
        
        Args:
            kind: "ticker" or "bench"
            idx: Row index
        """
        rows = self.ticker_rows if kind == "ticker" else self.benchmark_rows
        row = rows[idx]
        entry = row["entry"]
        top = row["sugg_top"]
        
        if not top:
            return
        
        x = entry.winfo_rootx()
        y_below = entry.winfo_rooty() + entry.winfo_height()
        w = entry.winfo_width()
        screen_h = self.root.winfo_screenheight()
        lb = row["sugg_list"]
        items = max(1, min(8, lb.size() or 6))
        item_h = self.dropdown_item_height
        height_px = int(min(items * item_h, max(120, item_h * 4)))
        
        if y_below + height_px + 10 > screen_h:
            y = entry.winfo_rooty() - height_px
        else:
            y = y_below
        
        top.geometry(f"{w}x{height_px}+{x}+{y}")
        top.lift()
    
    def show_dropdown(self, kind, idx, labels):
        """
        Show dropdown with suggestions
        
        Args:
            kind: "ticker" or "bench"
            idx: Row index
            labels: List of suggestion labels
        """
        top, lb = self.ensure_dropdown(kind, idx)
        lb.delete(0, tk.END)
        for s in labels:
            lb.insert(tk.END, s)
        if lb.size() > 0:
            lb.selection_clear(0, tk.END)
            lb.selection_set(0)
        
        # Make sure the dropdown is visible (fix for disappearing dropdown bug)
        try:
            top.deiconify()  # Show window if it was hidden
            top.lift()       # Bring to front
        except Exception:
            pass
        
        self.place_dropdown(kind, idx)
    
    def hide_dropdown(self, kind, idx):
        """
        Hide dropdown for the given row
        
        Args:
            kind: "ticker" or "bench"
            idx: Row index
        """
        rows = self.ticker_rows if kind == "ticker" else self.benchmark_rows
        row = rows[idx]
        if row.get("sugg_top"):
            try:
                row["sugg_top"].withdraw()
            except Exception:
                pass
    
    def focus_dropdown(self, kind, idx):
        """
        Give focus to dropdown
        
        Args:
            kind: "ticker" or "bench"
            idx: Row index
        """
        rows = self.ticker_rows if kind == "ticker" else self.benchmark_rows
        row = rows[idx]
        lb = row.get("sugg_list")
        if lb:
            try:
                row["sugg_top"].deiconify()
                lb.focus_set()
                if lb.size() > 0:
                    lb.selection_set(0)
            except Exception:
                pass
    
    def pick_suggestion(self, kind, idx):
        """
        Pick selected suggestion from dropdown
        
        Args:
            kind: "ticker" or "bench"
            idx: Row index
        """
        rows = self.ticker_rows if kind == "ticker" else self.benchmark_rows
        row = rows[idx]
        entry = row["entry"]
        placeholder = row["placeholder"]
        lb = row.get("sugg_list")
        
        if not lb:
            return
        
        try:
            sel = lb.get(lb.curselection())
        except Exception:
            self.hide_dropdown(kind, idx)
            return
        
        symbol = sel.split(" — ")[0].strip()
        entry.delete(0, tk.END)
        entry.insert(0, symbol)
        entry.config(fg=T.TEXT_PRIMARY)
        self.hide_dropdown(kind, idx)
        self.queue_validate(kind, idx)
    
    def collect_valid_symbols(self, kind):
        """
        Collect valid symbols from rows
        
        Args:
            kind: "ticker" or "bench"
        
        Returns:
            list: For tickers: [(symbol, weight), ...], for benches: [symbol, ...]
        """
        rows = self.ticker_rows if kind == "ticker" else self.benchmark_rows
        out = []
        
        for row in rows:
            entry = row.get("entry")
            placeholder = row.get("placeholder")
            status_lbl = row.get("status")
            symbol = self.get_symbol(entry, placeholder)
            status = status_lbl.cget("text") if status_lbl else ""
            
            if symbol and status == "✓":
                if kind == "ticker":
                    # Also collect weight
                    weight_entry = row.get("weight_entry")
                    try:
                        weight = float(weight_entry.get().strip()) if weight_entry else 10.0
                    except ValueError:
                        weight = 10.0
                    out.append((symbol, weight))
                else:
                    out.append(symbol)
        
        # Deduplicate
        if kind == "ticker":
            seen = set()
            unique = []
            for s, w in out:
                if s not in seen:
                    unique.append((s, w))
                    seen.add(s)
            return unique
        else:
            seen = set()
            unique = []
            for s in out:
                if s not in seen:
                    unique.append(s)
                    seen.add(s)
            return unique

