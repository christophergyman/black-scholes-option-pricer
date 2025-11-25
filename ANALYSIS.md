# Black-Scholes Option Pricer: Code Analysis

## Overview

This code implements a Black-Scholes-Merton option pricing model to calculate theoretical option prices and compare them against real market prices from Yahoo Finance. It processes live option chain data and provides statistical analysis of the model's accuracy.

## Why This Code Is Useful

### 1. **Theoretical Price Validation**
- Provides a benchmark for evaluating whether options are overpriced or underpriced in the market
- Helps identify potential arbitrage opportunities or mispricings
- Useful for educational purposes to understand option pricing theory

### 2. **Market Analysis**
- Compares theoretical model prices against actual market prices
- Provides statistical metrics (average differences, percentage accuracy)
- Identifies which options are priced close to or far from theoretical values

### 3. **Performance Benchmarking**
- Includes a performance test function to measure calculation speed
- Useful for optimizing option pricing algorithms

### 4. **Real-Time Data Integration**
- Automatically fetches live option chain data from Yahoo Finance
- Processes multiple expiration dates simultaneously
- Filters options by open interest to focus on liquid contracts

## How The Code Works

### Data Flow

1. **Data Retrieval** (`queryYfinance` function):
   - Fetches option chain data for a given ticker symbol
   - Retrieves call options across multiple expiration dates
   - Filters options with open interest > 0 (liquid contracts)
   - Gets current stock price from historical data

2. **Option Processing Loop**:
   - For each option:
     - Extracts strike price, expiration date, and implied volatility
     - Calculates time to expiration in years
     - Normalizes implied volatility (handles percentage vs decimal formats)
     - Builds option parameters dictionary
     - Calculates Black-Scholes model price

3. **Black-Scholes Calculation**:
   - Calculates d1 and d2 parameters
   - Applies the Black-Scholes formula for call options:
     ```
     C = S₀ × e^(-q×T) × N(d₁) - K × e^(-r×T) × N(d₂)
     ```
   - Where:
     - S₀ = Current stock price
     - K = Strike price
     - T = Time to expiration (years)
     - r = Risk-free interest rate
     - q = Dividend yield
     - σ = Volatility
     - N() = Cumulative normal distribution

4. **Analysis & Comparison**:
   - Filters valid options (reasonable volatility range: 1%-200%)
   - Calculates differences between model prices and market prices
   - Provides statistical summary and sample comparisons

## Hard-Coded Assumptions and Their Impact

### 1. **Risk-Free Interest Rate: 5% (0.05)**

**Location**: Line 145

**Assumption**: Constant 5% risk-free rate for all calculations

**Why It Matters**:
- The risk-free rate is a critical input in option pricing
- Current Treasury rates vary (typically 3-5% as of 2024)
- Different expiration dates should ideally use different rates (yield curve)

**Shortcomings**:
- **Inaccurate for current market conditions**: If actual risk-free rate is 3% or 7%, all option prices will be systematically over/under-valued
- **Ignores yield curve**: Short-term options should use short-term rates, long-term options should use long-term rates
- **Static value**: Doesn't account for changing interest rate environment

**Impact on Results**:
- Higher risk-free rate → Higher call option prices (time value of money)
- Can cause systematic bias in pricing, especially for longer-dated options
- May explain some of the 4-7% differences observed in results

### 2. **Dividend Yield: 2% (0.02)**

**Location**: Line 146

**Assumption**: Constant 2% dividend yield for all stocks

**Why It Matters**:
- Dividend yield directly affects option pricing (dividends reduce call option value)
- Different stocks have vastly different dividend yields (AAPL ~0.5%, utilities ~4-5%)

**Shortcomings**:
- **Stock-specific**: Each stock has its own dividend yield that changes over time
- **Ignores ex-dividend dates**: Options near ex-dividend dates are affected differently
- **Static assumption**: Doesn't account for dividend changes or special dividends

**Impact on Results**:
- If actual dividend yield is higher → Model overvalues call options
- If actual dividend yield is lower → Model undervalues call options
- For AAPL specifically, 2% is higher than actual (~0.5%), causing systematic overvaluation

### 3. **Days Per Year: 365.0**

**Location**: Line 158

**Assumption**: Exactly 365 days per year for time calculations

**Why It Matters**:
- Time to expiration is critical in option pricing (theta decay)
- Small differences in time calculation can affect prices

**Shortcomings**:
- **Ignores leap years**: Should use 365.25 for long-term accuracy
- **Trading days vs calendar days**: Options typically priced using trading days (252), not calendar days
- **Business day conventions**: Should account for market holidays

**Impact on Results**:
- Minor impact for short-term options
- Can cause noticeable differences for long-term options (1+ years)
- Using trading days (252) would be more accurate for financial modeling

### 4. **Volatility Normalization Logic**

**Location**: Lines 168-171

**Assumption**: If volatility > 1.0, it's a percentage; if ≤ 1.0, it's already decimal

**Why It Matters**:
- Yahoo Finance may return volatility in different formats
- Incorrect normalization leads to wildly wrong option prices

**Shortcomings**:
- **Heuristic approach**: No definitive way to know the format
- **Potential for errors**: If Yahoo Finance changes format, calculations break
- **No validation**: Doesn't verify if normalized value is reasonable

**Impact on Results**:
- If normalization is wrong, option prices can be off by orders of magnitude
- The code filters extreme values (1%-200%) but may miss edge cases

### 5. **Constant Volatility Assumption**

**Location**: Uses implied volatility from option chain

**Assumption**: Volatility is constant over the option's lifetime

**Why It Matters**:
- Black-Scholes assumes constant volatility (one of its key limitations)
- Real markets show volatility smile/skew (different strikes have different implied volatilities)

**Shortcomings**:
- **Volatility smile ignored**: ATM, ITM, and OTM options have different implied volatilities
- **Time-varying volatility**: Volatility changes over time (GARCH models account for this)
- **Volatility clustering**: High volatility periods cluster together

**Impact on Results**:
- Model may price options incorrectly, especially for:
  - Deep in-the-money options
  - Deep out-of-the-money options
  - Options with very short or very long expiration

### 6. **European-Style Options Only**

**Location**: Black-Scholes formula implementation

**Assumption**: Options can only be exercised at expiration (European-style)

**Why It Matters**:
- Most US stock options are American-style (can be exercised early)
- Early exercise affects option value, especially for dividend-paying stocks

**Shortcomings**:
- **No early exercise premium**: American options are worth more than European options
- **Dividend impact**: Should exercise early before ex-dividend dates for deep ITM calls
- **Binomial/trinomial models**: More appropriate for American options

**Impact on Results**:
- Model undervalues American options
- Differences are most pronounced for:
  - Deep in-the-money options
  - Options on high-dividend stocks
  - Options near ex-dividend dates

### 7. **No Transaction Costs**

**Assumption**: Trading is costless

**Why It Matters**:
- Real trading involves commissions, bid-ask spreads, and slippage
- These costs affect arbitrage opportunities

**Shortcomings**:
- **Bid-ask spreads**: Market prices are mid-points, actual execution may differ
- **Commission costs**: Reduce profitability of arbitrage strategies
- **Slippage**: Large orders move prices

**Impact on Results**:
- Model prices may appear to differ from market prices, but differences may be within transaction costs
- Small differences (1-2%) may not be exploitable after costs

### 8. **Lognormal Price Distribution**

**Assumption**: Stock prices follow a lognormal random walk

**Why It Matters**:
- Black-Scholes assumes stock returns are normally distributed
- Real markets show fat tails, skewness, and jumps

**Shortcomings**:
- **Fat tails**: Extreme moves (crashes, rallies) happen more often than model predicts
- **Jump risk**: Sudden price jumps not captured by continuous model
- **Regime changes**: Market volatility regimes change over time

**Impact on Results**:
- Model may misprice options during:
  - High volatility periods
  - Market stress events
  - Earnings announcements
  - Major news events

### 9. **Continuous Trading Assumption**

**Assumption**: Trading happens continuously

**Why It Matters**:
- Real markets have discrete trading, gaps, and after-hours trading
- Overnight and weekend gaps affect option pricing

**Shortcomings**:
- **Market hours**: Options can't be traded 24/7
- **Gap risk**: Overnight gaps can't be hedged continuously
- **After-hours trading**: Limited liquidity affects pricing

**Impact on Results**:
- Minor impact for most options
- More significant for very short-term options (0-1 DTE)

### 10. **Single Stock Price Source**

**Location**: Line 142

**Assumption**: Uses last close price from 1-day history

**Why It Matters**:
- Option pricing is sensitive to current stock price
- Using stale or incorrect price leads to wrong option values

**Shortcomings**:
- **Stale data**: If market is closed, uses previous close
- **No real-time data**: Doesn't use current bid/ask or last trade
- **Single source**: No validation against multiple data sources

**Impact on Results**:
- If stock price has moved significantly, all option prices will be wrong
- Can cause systematic bias if using closing price during trading hours

## Summary of Shortcomings

### High Impact Shortcomings:
1. **Hard-coded risk-free rate (5%)** - Can cause systematic pricing errors
2. **Hard-coded dividend yield (2%)** - Stock-specific, causes systematic bias
3. **European-style assumption** - Undervalues American options
4. **Constant volatility** - Ignores volatility smile/skew

### Medium Impact Shortcomings:
5. **365 days per year** - Should use trading days (252) or account for leap years
6. **No transaction costs** - Differences may not be exploitable
7. **Lognormal distribution** - Misses fat tails and jumps

### Low Impact Shortcomings:
8. **Volatility normalization heuristic** - Works but not robust
9. **Continuous trading assumption** - Minor impact for most cases
10. **Single price source** - Usually fine, but can be stale

## Recommendations for Improvement

1. **Fetch risk-free rate dynamically**: Use current Treasury yield (10-year for long-term, 3-month for short-term)
2. **Calculate dividend yield per stock**: Fetch from ticker info or calculate from dividend history
3. **Use trading days**: Calculate time using 252 trading days per year
4. **Consider American options**: Implement binomial/trinomial model for early exercise
5. **Account for volatility smile**: Use strike-specific implied volatilities
6. **Add transaction costs**: Include bid-ask spreads in analysis
7. **Real-time price data**: Use current market price, not just close price
8. **Robust volatility handling**: Validate and handle edge cases better

## Conclusion

This code provides a solid foundation for option pricing analysis and is useful for:
- Educational purposes
- Quick theoretical price estimates
- Identifying general pricing patterns
- Performance benchmarking

However, the hard-coded assumptions limit its accuracy for:
- Real trading decisions
- Arbitrage opportunities
- Risk management
- Production trading systems

The observed 4-7% differences between model and market prices are likely due to a combination of:
- Hard-coded risk-free rate and dividend yield
- European-style assumption (most US options are American)
- Volatility smile not being accounted for
- Transaction costs and bid-ask spreads

For production use, these assumptions should be made configurable and fetched dynamically from reliable data sources.
