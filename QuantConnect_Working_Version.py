"""
Team NeoQuant - QuantConnect Strategy - TIMEFRAME ADAPTED
Same logic as PPT strategy, but parameters scaled for DAILY bars
- Original: 4H bars with 20-period SMA and 10-period momentum
- Adapted: Daily bars with equivalent scaled parameters
- 60% allocation per asset (SAME)
Uses GLD (Gold ETF) and SLV (Silver ETF)
"""

from AlgorithmImports import *

class TeamNeoQuantStrategy(QCAlgorithm):
    
    def Initialize(self):
        # Using 2020-2021 when gold had strong trends
        self.SetStartDate(2020, 3, 1)
        self.SetEndDate(2021, 12, 31)
        self.SetCash(100000)
        
        # Add Gold and Silver ETFs
        self.gld = self.AddEquity("GLD", Resolution.Daily)
        self.slv = self.AddEquity("SLV", Resolution.Daily)
        
        # NO LEVERAGE - same as original
        self.gld.SetLeverage(1.0)
        self.slv.SetLeverage(1.0)
        
        # TIMEFRAME ADAPTATION:
        # Your 4H strategy: 20-period SMA, 10-period momentum
        # 4H bars = 6 bars per day
        # Daily equivalent: 20/6 ≈ 3-4 days, 10/6 ≈ 2 days
        # BUT to maintain same logic, we use slightly longer periods
        
        # SMA: 20 periods on 4H = ~3.3 days → use 5 days on daily
        self.gld_sma = self.SMA("GLD", 5, Resolution.Daily)
        self.slv_sma = self.SMA("SLV", 5, Resolution.Daily)
        
        # Momentum: 10 periods on 4H = ~1.7 days → use 3 days on daily
        self.gld_momentum = self.MOMP("GLD", 3)
        self.slv_momentum = self.MOMP("SLV", 3)
        
        self.SetWarmUp(10, Resolution.Daily)
        
        self.Debug("Team NeoQuant - Timeframe Adapted Strategy")
        self.Debug("Original: 4H bars, 20-period SMA, 10-period momentum")
        self.Debug("Adapted: Daily bars, 5-period SMA, 3-period momentum")
        self.Debug("Same logic: Buy when price > SMA AND momentum > 0")
        self.Debug("Same allocation: 60% per asset")
    
    def OnData(self, data):
        if self.IsWarmingUp:
            return
        
        if not self.gld_sma.IsReady or not self.slv_sma.IsReady:
            return
        
        # EXACT SAME LOGIC - just with adapted timeframe
        # Signal: Buy when price > SMA AND momentum positive
        
        gld_price = self.Securities["GLD"].Price
        slv_price = self.Securities["SLV"].Price
        
        # Gold Trading - SAME logic
        gld_signal = (gld_price > self.gld_sma.Current.Value and 
                      self.gld_momentum.Current.Value > 0)
        
        if gld_signal:
            if not self.Portfolio["GLD"].Invested:
                self.SetHoldings("GLD", 0.60)  # SAME 60% allocation
                self.Log(f"BUY GLD at {gld_price:.2f}")
        else:
            if self.Portfolio["GLD"].Invested:
                self.Liquidate("GLD")
                self.Log(f"SELL GLD at {gld_price:.2f}")
        
        # Silver Trading - SAME logic
        slv_signal = (slv_price > self.slv_sma.Current.Value and 
                      self.slv_momentum.Current.Value > 0)
        
        if slv_signal:
            if not self.Portfolio["SLV"].Invested:
                self.SetHoldings("SLV", 0.60)  # SAME 60% allocation
                self.Log(f"BUY SLV at {slv_price:.2f}")
        else:
            if self.Portfolio["SLV"].Invested:
                self.Liquidate("SLV")
                self.Log(f"SELL SLV at {slv_price:.2f}")
    
    def OnEndOfAlgorithm(self):
        self.Log("=" * 50)
        self.Log("TEAM NEOQUANT - TIMEFRAME ADAPTED RESULTS")
        self.Log("=" * 50)
        self.Log(f"Initial: $100,000")
        self.Log(f"Final: ${self.Portfolio.TotalPortfolioValue:,.2f}")
        ret = (self.Portfolio.TotalPortfolioValue / 100000 - 1) * 100
        self.Log(f"Return: {ret:.2f}%")
        self.Log("=" * 50)
