import tkinter as tk
from tkinter import ttk
from modules.mexc_api import fetch_current_price

class MainApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Autobot")

        # We'll store any user data in a dictionary if needed
        self.answers = {
            "coin": None,
            "position_type": None,
            "entry_price": None,
            "exit_price": None,
            "leverage": None,
            "capital": None,
        }

        # We'll keep track of frames in a dict
        self.frames = {}

        # Create each frame
        self.frames["MenuFrame"]         = MenuFrame(parent=self, controller=self)
        self.frames["CurrentPriceFrame"] = CurrentPriceFrame(parent=self, controller=self)
        self.frames["Calc_Step_Coin"]    = CalcStepCoin(parent=self, controller=self)
        self.frames["Calc_Step_Position"]= CalcStepPosition(parent=self, controller=self)
        self.frames["Calc_Step_Entry"]   = CalcStepEntry(parent=self, controller=self)
        self.frames["Calc_Step_Exit"]    = CalcStepExit(parent=self, controller=self)
        self.frames["Calc_Step_Leverage"]= CalcStepLeverage(parent=self, controller=self)
        self.frames["Calc_Step_Capital"] = CalcStepCapital(parent=self, controller=self)
        self.frames["Calc_Step_Summary"] = CalcStepSummary(parent=self, controller=self)
        self.frames["ScalperFrame"]      = ScalperFrame(parent=self, controller=self)

        # Layout each frame (overlapping)
        for frame in self.frames.values():
            frame.grid(row=0, column=0, sticky="NSEW")

        # Show the menu initially
        self.show_frame("MenuFrame")

    def show_frame(self, frame_name):
        """
        Bring the specified frame to the front.
        """
        frame = self.frames[frame_name]
        frame.tkraise()

    def reset_calc_flow(self):
        """
        Clear answers for the calculation wizard.
        """
        for key in self.answers:
            self.answers[key] = None
        # Reset each calc step's fields
        for step_name in [
            "Calc_Step_Coin","Calc_Step_Position","Calc_Step_Entry","Calc_Step_Exit",
            "Calc_Step_Leverage","Calc_Step_Capital","Calc_Step_Summary"
        ]:
            self.frames[step_name].reset_fields()

# --------------------- MENU FRAME -------------------------

class MenuFrame(ttk.Frame):
    """
    Main menu with 3 buttons: 
      - Current Price
      - Calculation Wizard
      - Scalper
      and an Exit button
    """
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        ttk.Label(self, text="Main Menu", font=("TkDefaultFont", 16)).grid(row=0, column=0, columnspan=2, pady=20)

        current_btn = ttk.Button(self, text="Current Price Flow",
                                 command=lambda: controller.show_frame("CurrentPriceFrame"))
        current_btn.grid(row=1, column=0, padx=10, pady=5)

        calc_btn = ttk.Button(self, text="Calculation Wizard",
                              command=lambda: self.start_calculation_flow())
        calc_btn.grid(row=2, column=0, padx=10, pady=5)

        scalper_btn = ttk.Button(self, text="Scalper Flow",
                                 command=lambda: controller.show_frame("ScalperFrame"))
        scalper_btn.grid(row=3, column=0, padx=10, pady=5)

        exit_btn = ttk.Button(self, text="Exit",
                              command=self.on_exit)
        exit_btn.grid(row=4, column=0, padx=10, pady=5)

    def start_calculation_flow(self):
        """
        Resets the calc flow answers, then show the first step (coin).
        """
        self.controller.reset_calc_flow()
        self.controller.show_frame("Calc_Step_Coin")

    def on_exit(self):
        self.controller.destroy()

# --------------------- CURRENT PRICE ----------------------

class CurrentPriceFrame(ttk.Frame):
    """
    Shows BTC price, asks for a coin, repeatedly updates coin price until user returns
    """
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        self.coin_var = tk.StringVar()
        self.status_var = tk.StringVar()

        ttk.Label(self, text="Current Price Flow", font=("TkDefaultFont", 14)).grid(row=0, column=0, columnspan=2, pady=10)

        # Show BTC Price immediately
        self.btc_label_var = tk.StringVar(value="BTC Price: ???")
        ttk.Label(self, textvariable=self.btc_label_var).grid(row=1, column=0, columnspan=2, sticky="W", padx=5, pady=5)

        # Coin entry
        ttk.Label(self, text="Coin Ticker (e.g. SOL):").grid(row=2, column=0, sticky="W", padx=5)
        ttk.Entry(self, textvariable=self.coin_var).grid(row=2, column=1, padx=5)

        # Buttons
        update_btn = ttk.Button(self, text="Fetch & Monitor", command=self.on_fetch)
        update_btn.grid(row=3, column=0, pady=5)

        menu_btn = ttk.Button(self, text="Back to Menu", command=lambda: controller.show_frame("MenuFrame"))
        menu_btn.grid(row=3, column=1, pady=5)

        ttk.Label(self, textvariable=self.status_var, wraplength=300).grid(row=4, column=0, columnspan=2, sticky="W")

    def on_fetch(self):
        # 1) Fetch BTC
        btc = fetch_current_price("BTC/USDT")
        if btc is not None:
            self.btc_label_var.set(f"BTC Price: {btc:.3f} USDT")
        else:
            self.btc_label_var.set("BTC Price: ??? (failed)")

        # 2) user coin
        coin = self.coin_var.get().strip().upper()
        if not coin:
            self.status_var.set("Please enter a coin ticker.")
            return

        pair = f"{coin}/USDT"
        price = fetch_current_price(pair)
        if price is None:
            self.status_var.set(f"Failed to fetch {pair} price.")
            return

        # 3) Monitor in a loop if you want
        # For simplicity, just show price once. If you want repeated updates, you'd do after(...).
        msg = f"{pair} = {price:.3f} USDT"
        self.status_var.set(msg)

# --------------------- CALCULATION WIZARD ------------------

class CalcStepCoin(ttk.Frame):
    """
    Step 1: choose coin for calculation
    """
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.answers = controller.answers

        ttk.Label(self, text="Calculation Wizard - Step (Coin)", font=("TkDefaultFont", 14)).grid(row=0, column=0, columnspan=2, pady=10)

        self.coin_var = tk.StringVar()
        ttk.Label(self, text="Coin Ticker:").grid(row=1, column=0, sticky="W", padx=5, pady=5)
        ttk.Entry(self, textvariable=self.coin_var).grid(row=1, column=1, padx=5, pady=5)

        nav_frame = ttk.Frame(self)
        nav_frame.grid(row=2, column=0, columnspan=2, pady=10)

        back_btn = ttk.Button(nav_frame, text="Menu", command=lambda: controller.show_frame("MenuFrame"))
        back_btn.grid(row=0, column=0, padx=5)

        next_btn = ttk.Button(nav_frame, text="Next", command=self.on_next)
        next_btn.grid(row=0, column=1, padx=5)

    def on_next(self):
        coin_str = self.coin_var.get().strip().upper()
        if not coin_str:
            print("Please enter a coin.")
            return
        self.answers["coin"] = coin_str
        self.controller.show_frame("Calc_Step_Position")

    def reset_fields(self):
        self.coin_var.set("")

class CalcStepPosition(ttk.Frame):
    """Step 2: LONG/SHORT"""
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.answers = controller.answers

        ttk.Label(self, text="Calculation Wizard - Step (Position)", font=("TkDefaultFont", 14)).grid(row=0, column=0, columnspan=2, pady=10)

        self.pos_var = tk.StringVar()
        ttk.Label(self, text="Position (LONG/SHORT):").grid(row=1, column=0, sticky="W", padx=5, pady=5)
        ttk.Entry(self, textvariable=self.pos_var).grid(row=1, column=1, padx=5, pady=5)

        nav_frame = ttk.Frame(self)
        nav_frame.grid(row=2, column=0, columnspan=2, pady=10)

        back_btn = ttk.Button(nav_frame, text="Back", command=lambda: controller.show_frame("Calc_Step_Coin"))
        back_btn.grid(row=0, column=0, padx=5)

        next_btn = ttk.Button(nav_frame, text="Next", command=self.on_next)
        next_btn.grid(row=0, column=1, padx=5)

    def on_next(self):
        pos = self.pos_var.get().strip().upper()
        if pos not in ["LONG", "SHORT"]:
            print("Invalid position. Must be LONG or SHORT.")
            return
        self.answers["position_type"] = pos
        self.controller.show_frame("Calc_Step_Entry")

    def reset_fields(self):
        self.pos_var.set("")

class CalcStepEntry(ttk.Frame):
    """Step 3: Entry Price"""
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.answers = controller.answers

        ttk.Label(self, text="Calculation Wizard - Step (Entry Price)", font=("TkDefaultFont", 14)).grid(row=0, column=0, columnspan=2, pady=10)

        self.entry_var = tk.StringVar()
        ttk.Label(self, text="Entry Price:").grid(row=1, column=0, sticky="W", padx=5, pady=5)
        ttk.Entry(self, textvariable=self.entry_var).grid(row=1, column=1, padx=5, pady=5)

        nav_frame = ttk.Frame(self)
        nav_frame.grid(row=2, column=0, columnspan=2, pady=10)

        back_btn = ttk.Button(nav_frame, text="Back", command=lambda: controller.show_frame("Calc_Step_Position"))
        back_btn.grid(row=0, column=0, padx=5)

        next_btn = ttk.Button(nav_frame, text="Next", command=self.on_next)
        next_btn.grid(row=0, column=1, padx=5)

    def on_next(self):
        val = self.entry_var.get().strip()
        try:
            entry_price = float(val)
        except ValueError:
            print("Invalid entry price.")
            return
        self.answers["entry_price"] = entry_price
        self.controller.show_frame("Calc_Step_Exit")

    def reset_fields(self):
        self.entry_var.set("")

class CalcStepExit(ttk.Frame):
    """Step 4: Exit Price"""
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.answers = controller.answers

        ttk.Label(self, text="Calculation Wizard - Step (Exit Price)", font=("TkDefaultFont", 14)).grid(row=0, column=0, columnspan=2, pady=10)

        self.exit_var = tk.StringVar()
        ttk.Label(self, text="Exit Price:").grid(row=1, column=0, sticky="W", padx=5, pady=5)
        ttk.Entry(self, textvariable=self.exit_var).grid(row=1, column=1, padx=5, pady=5)

        nav_frame = ttk.Frame(self)
        nav_frame.grid(row=2, column=0, columnspan=2, pady=10)

        back_btn = ttk.Button(nav_frame, text="Back", command=lambda: controller.show_frame("Calc_Step_Entry"))
        back_btn.grid(row=0, column=0, padx=5)

        next_btn = ttk.Button(nav_frame, text="Next", command=self.on_next)
        next_btn.grid(row=0, column=1, padx=5)

    def on_next(self):
        val = self.exit_var.get().strip()
        try:
            exit_price = float(val)
        except ValueError:
            print("Invalid exit price.")
            return
        self.answers["exit_price"] = exit_price
        self.controller.show_frame("Calc_Step_Leverage")

    def reset_fields(self):
        self.exit_var.set("")

class CalcStepLeverage(ttk.Frame):
    """Step 5: Leverage"""
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.answers = controller.answers

        ttk.Label(self, text="Calculation Wizard - Step (Leverage)", font=("TkDefaultFont", 14)).grid(row=0, column=0, columnspan=2, pady=10)

        self.lev_var = tk.StringVar()
        ttk.Label(self, text="Leverage:").grid(row=1, column=0, sticky="W", padx=5, pady=5)
        ttk.Entry(self, textvariable=self.lev_var).grid(row=1, column=1, padx=5, pady=5)

        nav_frame = ttk.Frame(self)
        nav_frame.grid(row=2, column=0, columnspan=2, pady=10)

        back_btn = ttk.Button(nav_frame, text="Back", command=lambda: controller.show_frame("Calc_Step_Exit"))
        back_btn.grid(row=0, column=0, padx=5)

        next_btn = ttk.Button(nav_frame, text="Next", command=self.on_next)
        next_btn.grid(row=0, column=1, padx=5)

    def on_next(self):
        val = self.lev_var.get().strip()
        try:
            leverage = float(val)
        except ValueError:
            print("Invalid leverage.")
            return
        self.answers["leverage"] = leverage
        self.controller.show_frame("Calc_Step_Capital")

    def reset_fields(self):
        self.lev_var.set("")

class CalcStepCapital(ttk.Frame):
    """Step 6: Capital"""
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.answers = controller.answers

        ttk.Label(self, text="Calculation Wizard - Step (Capital)", font=("TkDefaultFont", 14)).grid(row=0, column=0, columnspan=2, pady=10)

        self.cap_var = tk.StringVar()
        ttk.Label(self, text="Capital (USDT):").grid(row=1, column=0, sticky="W", padx=5, pady=5)
        ttk.Entry(self, textvariable=self.cap_var).grid(row=1, column=1, padx=5, pady=5)

        nav_frame = ttk.Frame(self)
        nav_frame.grid(row=2, column=0, columnspan=2, pady=10)

        back_btn = ttk.Button(nav_frame, text="Back", command=lambda: self.controller.show_frame("Calc_Step_Leverage"))
        back_btn.grid(row=0, column=0, padx=5)

        next_btn = ttk.Button(nav_frame, text="Next", command=self.on_next)
        next_btn.grid(row=0, column=1, padx=5)

    def on_next(self):
        val = self.cap_var.get().strip()
        try:
            capital = float(val)
        except ValueError:
            print("Invalid capital.")
            return
        self.answers["capital"] = capital
        self.controller.show_frame("Calc_Step_Summary")

    def reset_fields(self):
        self.cap_var.set("")

class CalcStepSummary(ttk.Frame):
    """Step 7: Summarize and show potential profit / liquidation."""
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.answers = controller.answers

        ttk.Label(self, text="Calculation Wizard - Summary", font=("TkDefaultFont", 14)).grid(row=0, column=0, columnspan=2, pady=10)

        self.result_label_var = tk.StringVar()
        ttk.Label(self, textvariable=self.result_label_var, justify="left").grid(row=1, column=0, columnspan=2, sticky="W", padx=5, pady=5)

        nav_frame = ttk.Frame(self)
        nav_frame.grid(row=2, column=0, columnspan=2, pady=10)

        back_btn = ttk.Button(nav_frame, text="Back", command=lambda: self.controller.show_frame("Calc_Step_Capital"))
        back_btn.grid(row=0, column=0, padx=5)

        calc_btn = ttk.Button(nav_frame, text="Calculate", command=self.on_calculate)
        calc_btn.grid(row=0, column=1, padx=5)

        menu_btn = ttk.Button(nav_frame, text="Menu", command=lambda: self.controller.show_frame("MenuFrame"))
        menu_btn.grid(row=0, column=2, padx=5)

    def on_calculate(self):
        coin          = self.answers["coin"]
        position_type = self.answers["position_type"]
        entry_price   = self.answers["entry_price"]
        exit_price    = self.answers["exit_price"]
        leverage      = self.answers["leverage"]
        capital       = self.answers["capital"]

        if None in [coin, position_type, entry_price, exit_price, leverage, capital]:
            self.result_label_var.set("Error: missing inputs.")
            return

        notional = capital * leverage
        if position_type.upper() == "LONG":
            fraction = (exit_price - entry_price) / entry_price
            liquidation = entry_price * (1 - 1/leverage)
        else:
            fraction = (entry_price - exit_price) / entry_price
            liquidation = entry_price * (1 + 1/leverage)

        potential_profit = notional * fraction
        text = []
        text.append(f"Coin: {coin}")
        text.append(f"Position: {position_type}")
        text.append(f"Entry={entry_price}, Exit={exit_price}")
        text.append(f"Leverage={leverage}, Capital={capital}")
        text.append(f"Profit approx: {potential_profit:.2f} USDT")
        text.append(f"Liquidation approx: {liquidation:.3f} USDT")

        self.result_label_var.set("\n".join(text))

    def reset_fields(self):
        self.result_label_var.set("")

# --------------------- SCALPER FRAME ----------------------

class ScalperFrame(ttk.Frame):
    """
    Basic scalper UI. 
    In reality you might have multiple steps or real logic. 
    Here we just show a placeholder.
    """
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        ttk.Label(self, text="Scalper Flow", font=("TkDefaultFont", 14)).grid(row=0, column=0, columnspan=2, pady=10)

        menu_btn = ttk.Button(self, text="Back to Menu", command=lambda: controller.show_frame("MenuFrame"))
        menu_btn.grid(row=1, column=0, padx=10, pady=5)

        ttk.Label(self, text="(Placeholder for scalper logic.)").grid(row=2, column=0, columnspan=2, padx=5, pady=5)

# ----------------------------------------------------------

def main():
    app = MainApp()
    app.mainloop()

if __name__ == "__main__":
    main()
