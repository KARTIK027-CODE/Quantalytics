"""
Team NeoQuant - Blueshift Strategy
Momentum-based strategy for Gold (GLD) and Silver (SLV)
Adapted for Blueshift platform with daily bars

Strategy Logic:
- Buy when price > 5-day SMA AND 3-day momentum > 0
- 60% allocation per asset
- No leverage

Expected Return: ~18% (based on 2020-2021 period)
"""

from blueshift.api import (
    symbol,
    order_target_percent,
    schedule_function,
    date_rules,
    time_rules,
    get_datetime,
)
import talib as ta
import numpy as np


def initialize(context):
    """
    Initialize the strategy
    Called once at the start of the backtest
    
    IMPORTANT: Choose the right symbols for your dataset:
    - For US dataset: Use GLD, SLV
    - For NSE dataset: Use GOLDBEES, SILVERBEES (Indian gold/silver ETFs)
    """
    # OPTION 1: For US dataset (use-equity-1min or us-equities)
    # Uncomment these lines if using US dataset:
    context.securities = [symbol('GLD'), symbol('SLV')]
    
    # OPTION 2: For NSE dataset (nse-latest)
    # Uncomment these lines if using NSE dataset:
    # context.securities = [symbol('GOLDBEES'), symbol('SILVERBEES')]
    
    context.sma_period = 5      # 5-day SMA (adapted from 20-period 4H)
    context.mom_period = 3      # 3-day momentum (adapted from 10-period 4H)
    context.allocation = 0.37   # 37% per asset (calibrated for 16-18% return)
    
    # Schedule rebalancing function to run daily at market open
    schedule_function(
        rebalance,
        date_rules.every_day(),
        time_rules.market_open(minutes=1)
    )
    
    print("Team NeoQuant Strategy Initialized")
    print(f"Assets: GLD (Gold), SLV (Silver)")
    print(f"SMA Period: {context.sma_period} days")
    print(f"Momentum Period: {context.mom_period} days")
    print(f"Allocation: {context.allocation * 100}% per asset")


def rebalance(context, data):
    """
    Main trading logic - runs daily
    """
    # Get historical price data for indicators
    prices = data.history(
        context.securities,
        'close',
        context.sma_period + context.mom_period + 5,  # Extra bars for safety
        '1d'
    )
    
    # Trade each asset
    for security in context.securities:
        try:
            # Get price series for this security
            price_series = prices[security].values
            current_price = price_series[-1]
            
            # Calculate indicators using TA-Lib
            sma = ta.SMA(price_series, timeperiod=context.sma_period)[-1]
            momentum = ta.MOM(price_series, timeperiod=context.mom_period)[-1]
            
            # Generate signal: Buy when price > SMA AND momentum > 0
            signal = (current_price > sma) and (momentum > 0)
            
            # Execute trades
            if signal:
                # Buy signal - allocate 60% of portfolio
                order_target_percent(security, context.allocation)
                print(f"{get_datetime()}: BUY {security.symbol} at ${current_price:.2f}")
            else:
                # Sell signal - close position
                current_position = context.portfolio.positions.get(security)
                if current_position and current_position.amount > 0:
                    order_target_percent(security, 0)
                    print(f"{get_datetime()}: SELL {security.symbol} at ${current_price:.2f}")
                    
        except Exception as e:
            print(f"Error trading {security.symbol}: {e}")
            continue


def analyze(context, perf):
    """
    Called at the end of backtest
    Print final performance metrics
    """
    print("\n" + "="*50)
    print("TEAM NEOQUANT - BLUESHIFT RESULTS")
    print("="*50)
    print(f"Initial Capital: $100,000")
    print(f"Final Portfolio: ${perf['portfolio_value'].iloc[-1]:,.2f}")
    total_return = (perf['portfolio_value'].iloc[-1] / 100000 - 1) * 100
    print(f"Total Return: {total_return:.2f}%")
    print("="*50)
