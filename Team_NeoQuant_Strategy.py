"""
SIMPLE PROFITABLE STRATEGY - Team NeoQuant
Pure momentum + trend following (no ML complexity)

Usage: python Team_NeoQuant_Strategy_SIMPLE.py --xau_csv DAT_MT_XAUUSD_M1_2024.csv --xag_csv DAT_MT_XAGUSD_M1_2024.csv
"""

import pandas as pd
import numpy as np
import argparse
import warnings
warnings.filterwarnings('ignore')


def load_and_prepare_data(xau_csv, xag_csv, timeframe='4H'):
    """Load data"""
    print(f"\n[1/3] Loading data...")
    
    xau = pd.read_csv(xau_csv, header=None, names=['Date', 'Time', 'Open', 'High', 'Low', 'Close', 'Volume'])
    xau['DateTime'] = pd.to_datetime(xau['Date'].astype(str) + ' ' + xau['Time'].astype(str))
    xau = xau.set_index('DateTime')[['Open', 'High', 'Low', 'Close', 'Volume']]
    xau = xau.apply(pd.to_numeric, errors='coerce').sort_index()
    
    xag = pd.read_csv(xag_csv, header=None, names=['Date', 'Time', 'Open', 'High', 'Low', 'Close', 'Volume'])
    xag['DateTime'] = pd.to_datetime(xag['Date'].astype(str) + ' ' + xag['Time'].astype(str))
    xag = xag.set_index('DateTime')[['Open', 'High', 'Low', 'Close', 'Volume']]
    xag = xag.apply(pd.to_numeric, errors='coerce').sort_index()
    
    xau_r = xau.resample(timeframe).agg({'Open': 'first', 'High': 'max', 'Low': 'min', 'Close': 'last', 'Volume': 'sum'}).dropna()
    xag_r = xag.resample(timeframe).agg({'Open': 'first', 'High': 'max', 'Low': 'min', 'Close': 'last', 'Volume': 'sum'}).dropna()
    
    xau_r.columns = ['XAU_' + c for c in xau_r.columns]
    xag_r.columns = ['XAG_' + c for c in xag_r.columns]
    df = pd.concat([xau_r, xag_r], axis=1, join='inner')
    
    print(f"  Loaded {len(df):,} bars")
    return df


def backtest_simple(df, initial_capital=100000):
    """Simple momentum strategy"""
    print(f"\n[2/3] Running momentum strategy...")
    
    # Calculate simple indicators
    for asset in ['XAU', 'XAG']:
        close = df[f'{asset}_Close']
        df[f'{asset}_sma_20'] = close.rolling(20).mean()
        df[f'{asset}_sma_50'] = close.rolling(50).mean()
        df[f'{asset}_ret_10'] = close.pct_change(10)
        
        # Signal: Buy when price > SMA20 AND momentum positive
        df[f'{asset}_signal'] = ((close > df[f'{asset}_sma_20']) & (df[f'{asset}_ret_10'] > 0)).astype(int)
    
    df = df.dropna()
    
    # Use last 15% as test
    test_start = int(len(df) * 0.85)
    test_df = df.iloc[test_start:].copy()
    
    print(f"  Test period: {len(test_df)} bars")
    print(f"  XAU signals: {test_df['XAU_signal'].sum()} ({test_df['XAU_signal'].mean():.1%})")
    print(f"  XAG signals: {test_df['XAG_signal'].sum()} ({test_df['XAG_signal'].mean():.1%})")
    
    # Backtest
    capital = initial_capital
    equity = [capital]
    
    for i in range(1, len(test_df)):
        pnl = 0
        
        for asset in ['XAU', 'XAG']:
            signal = test_df[f'{asset}_signal'].iloc[i]
            ret = test_df[f'{asset}_Close'].iloc[i] / test_df[f'{asset}_Close'].iloc[i-1] - 1
            
            if signal == 1:
                pnl += capital * 0.60 * ret  # 60% per asset when signal
        
        capital += pnl
        equity.append(capital)
    
    equity_series = pd.Series(equity, index=test_df.index[:len(equity)])
    returns = equity_series.pct_change().dropna()
    
    return equity_series, returns


def calculate_metrics(returns, initial_capital, final_capital):
    """Calculate metrics"""
    print(f"\n[3/3] Calculating metrics...")
    
    total_return = (final_capital / initial_capital) - 1
    annual_return = (1 + total_return) ** (252 / len(returns)) - 1 if len(returns) > 0 else 0
    volatility = returns.std() * np.sqrt(252) if len(returns) > 0 else 0
    sharpe = annual_return / volatility if volatility > 0 else 0
    
    if len(returns) > 0:
        cumulative = (1 + returns).cumprod()
        drawdown = (cumulative - cumulative.cummax()) / cumulative.cummax()
        max_dd = drawdown.min()
        win_rate = (returns > 0).sum() / len(returns)
    else:
        max_dd = 0
        win_rate = 0
    
    return {
        'Total Return': total_return,
        'Annual Return': annual_return,
        'Volatility': volatility,
        'Sharpe Ratio': sharpe,
        'Max Drawdown': max_dd,
        'Win Rate': win_rate
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--xau_csv', default='DAT_MT_XAUUSD_M1_2024.csv')
    parser.add_argument('--xag_csv', default='DAT_MT_XAGUSD_M1_2024.csv')
    parser.add_argument('--capital', type=float, default=100000)
    args = parser.parse_args()
    
    print("="*80)
    print("TEAM NEOQUANT - TRADING STRATEGY")
    print("="*80)
    
    df = load_and_prepare_data(args.xau_csv, args.xag_csv)
    equity, returns = backtest_simple(df, args.capital)
    metrics = calculate_metrics(returns, args.capital, equity.iloc[-1])
    
    print("\n" + "="*80)
    print("RESULTS")
    print("="*80)
    print(f"\nInitial Capital: ${args.capital:,.2f}")
    print(f"Final Capital:   ${equity.iloc[-1]:,.2f}")
    print(f"Total Return:    {metrics['Total Return']:.2%}")
    print(f"Annual Return:   {metrics['Annual Return']:.2%}")
    print(f"Sharpe Ratio:    {metrics['Sharpe Ratio']:.2f}")
    print(f"Max Drawdown:    {metrics['Max Drawdown']:.2%}")
    print(f"Win Rate:        {metrics['Win Rate']:.2%}")
    print(f"Volatility:      {metrics['Volatility']:.2%}")
    print("\n" + "="*80)
    
    return metrics


if __name__ == "__main__":
    main()
