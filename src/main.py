"""
Black-Scholes Option Pricing Model Implementation

This module provides a custom implementation of the Black-Scholes-Merton option
pricing model with support for dividend yields. It includes functions for calculating
option prices, fetching real market data from Yahoo Finance, and comparing model
prices with market prices.
"""

import logging
from math import log, sqrt, exp
from time import perf_counter
from typing import Dict, List, Optional, Union

import numbers
import pandas as pd
import yfinance as yf
from scipy.stats import norm

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Constants
DEFAULT_RISK_FREE_RATE = 0.05  # 5% annual risk-free rate
DEFAULT_DIVIDEND_YIELD = 0.02  # 2% annual dividend yield
MIN_VOLATILITY = 0.01  # 1% minimum reasonable volatility
MAX_VOLATILITY = 2.0  # 200% maximum reasonable volatility
MIN_TIME_TO_EXPIRATION = 0.0001  # Minimum time to expiration in years (to avoid division by zero)
DAYS_PER_YEAR = 365.0
MICROSECONDS_PER_SECOND = 1_000_000


def validate_option_input(option_information: List[Union[float, str]]) -> None:
    """
    Validate option input parameters.
    
    Args:
        option_information: List containing [asset_price, strike_price, expiration,
            risk_free_rate, volatility, option_type, dividend_yield]
    
    Raises:
        ValueError: If any parameter is invalid
        TypeError: If any parameter has incorrect type
    """
    # Validate float types for first 5 values (asset price, strike, expiration, rate, volatility)
    for i, param_name in enumerate(['asset_price', 'strike_price', 'expiration', 
                                     'risk_free_rate', 'volatility']):
        value = option_information[i]
        if not isinstance(value, numbers.Real):
            raise TypeError(f"{param_name} must be a real number, got {type(value).__name__}")
        if value < 0.0:
            raise ValueError(f"{param_name} must be non-negative, got {value}")
    
    # Validate option type input
    option_type = option_information[5]
    valid_types = ("C", "c", "Call", "P", "p", "Put")
    if option_type not in valid_types:
        raise ValueError(f"option_type must be one of {valid_types}, got '{option_type}'")
    
    # Validate dividend yield
    dividend_yield = option_information[6]
    if not isinstance(dividend_yield, numbers.Real):
        raise TypeError(f"dividend_yield must be a real number, got {type(dividend_yield).__name__}")


def normalize_option_type(option_type: str) -> str:
    """
    Normalize option type to standard format.
    
    Args:
        option_type: Option type string (C, c, Call, P, p, Put)
    
    Returns:
        Normalized option type ("Call" or "Put")
    """
    if option_type in ("C", "c", "Call"):
        return "Call"
    elif option_type in ("P", "p", "Put"):
        return "Put"
    else:
        raise ValueError(f"Invalid option type: {option_type}")


def return_hashmap(option_information: List[Union[float, str]]) -> Dict[str, Union[float, str]]:
    """
    Convert option information list to dictionary format with validation.
    
    Args:
        option_information: List containing [asset_price, strike_price, expiration,
            risk_free_rate, volatility, option_type, dividend_yield]
    
    Returns:
        Dictionary with keys: asset_price, strike_price, expiration, risk_free_interest_rate,
        volatility, option_type, dividend_yield
    
    Raises:
        ValueError: If any parameter is invalid
        TypeError: If any parameter has incorrect type
    """
    validate_option_input(option_information)
    
    normalized_option_type = normalize_option_type(option_information[5])
    
    return {
        "asset_price": option_information[0],
        "strike_price": option_information[1],
        "expiration": option_information[2],
        "risk_free_interest_rate": option_information[3],
        "volatility": option_information[4],
        "option_type": normalized_option_type,
        "dividend_yield": option_information[6],
    }


def d1_value(option: Dict[str, Union[float, str]]) -> float:
    """
    Calculate d1 standardized measure used in Black-Scholes model.
    
    d1 estimates the expected value of the stock relative to the strike,
    accounting for volatility and time.
    
    Formula: d1 = [ln(S/K) + (r - q + σ²/2) × T] / (σ × √T)
    where:
        S = asset price
        K = strike price
        r = risk-free interest rate
        q = dividend yield
        σ = volatility
        T = time to expiration
    
    Args:
        option: Dictionary containing option parameters
    
    Returns:
        d1 value as float
    """
    asset_price = option["asset_price"]
    strike_price = option["strike_price"]
    risk_free_rate = option["risk_free_interest_rate"]
    dividend_yield = option["dividend_yield"]
    volatility = option["volatility"]
    expiration = option["expiration"]
    
    sqrt_expiration = sqrt(expiration)
    
    d1 = (
        log(asset_price / strike_price)
        + (risk_free_rate - dividend_yield + (volatility ** 2) / 2) * expiration
    ) / (volatility * sqrt_expiration)
    
    return d1


def d2_value(option: Dict[str, Union[float, str]], d1: float) -> float:
    """
    Calculate d2 standardized measure used in Black-Scholes model.
    
    d2 estimates the probability of exercise at expiration.
    
    Formula: d2 = d₁ - σ × √T
    
    Args:
        option: Dictionary containing option parameters
        d1: Pre-calculated d1 value
    
    Returns:
        d2 value as float
    """
    volatility = option["volatility"]
    expiration = option["expiration"]
    
    d2 = d1 - volatility * sqrt(expiration)
    return d2


def black_scholes_calculator(option: Dict[str, Union[float, str]]) -> Optional[float]:
    """
    Calculate Black-Scholes-Merton option price.
    
    For Call options: C = S₀ × e^(-q×T) × N(d₁) - K × e^(-r×T) × N(d₂)
    For Put options: P = K × e^(-r×T) × N(-d₂) - S₀ × e^(-q×T) × N(-d₁)
    
    where:
        S₀ = current asset price
        K = strike price
        r = risk-free interest rate
        q = dividend yield
        T = time to expiration
        N() = cumulative standard normal distribution
    
    Args:
        option: Dictionary containing option parameters
    
    Returns:
        Option price as float, or None if option type is invalid
    """
    d1 = d1_value(option)
    d2 = d2_value(option, d1)
    
    # Discount factors
    discount_factor_r = exp(-option["risk_free_interest_rate"] * option["expiration"])
    discount_factor_q = exp(-option["dividend_yield"] * option["expiration"])
    
    option_type = option["option_type"]
    
    if option_type == "Call":
        # C = S₀ × e^(-q×T) × N(d₁) - K × e^(-r×T) × N(d₂)
        model_call_option_price = (
            option["asset_price"] * discount_factor_q * norm.cdf(d1)
            - option["strike_price"] * discount_factor_r * norm.cdf(d2)
        )
        return model_call_option_price
    
    elif option_type == "Put":
        # P = K × e^(-r×T) × N(-d₂) - S₀ × e^(-q×T) × N(-d₁)
        model_put_option_price = (
            option["strike_price"] * discount_factor_r * norm.cdf(-d2)
            - option["asset_price"] * discount_factor_q * norm.cdf(-d1)
        )
        return model_put_option_price
    
    logger.warning(f"Invalid option type: {option_type}")
    return None


def performance_test(iteration: int) -> None:
    """
    Run performance benchmark for Black-Scholes calculation.
    
    Args:
        iteration: Number of iterations to run
    """
    option_information = [31.45, 22.75, 3.5, 0.05, 0.5, "C", 0.02]
    option = return_hashmap(option_information)
    
    black_scholes_latency_times = []
    
    for _ in range(iteration):
        start_time = perf_counter()
        _ = black_scholes_calculator(option)
        end_time = perf_counter()
        function_time = (end_time - start_time) * MICROSECONDS_PER_SECOND
        black_scholes_latency_times.append(function_time)
    
    average_runtime = sum(black_scholes_latency_times) / iteration
    
    logger.info(
        f"{iteration} iterations completed. "
        f"Average Black-Scholes calculation time: {average_runtime:.2f} microseconds"
    )


def fetch_option_chain_data(ticker: str, option_range: int) -> pd.DataFrame:
    """
    Fetch option chain data from Yahoo Finance.
    
    Args:
        ticker: Stock ticker symbol
        option_range: Number of expiration dates to fetch
    
    Returns:
        DataFrame containing call options with open interest > 0
    """
    logger.info(f"Fetching option chain data for {ticker}")
    dat = yf.Ticker(ticker)
    
    if not dat.options:
        raise ValueError(f"No option chain data available for ticker {ticker}")
    
    # Get column structure from first option chain
    first_chain = dat.option_chain(dat.options[0]).calls
    columns = first_chain.columns.tolist()
    
    # Initialize list to store dataframes
    dataframes = []
    
    # Fetch and filter all option chains
    for i in range(min(option_range, len(dat.options))):
        try:
            chain = dat.option_chain(dat.options[i]).calls
            filtered_chain = chain[chain['openInterest'] > 0].copy()
            
            if not filtered_chain.empty:
                # Add expiration date column
                filtered_chain['expiration'] = dat.options[i]
                dataframes.append(filtered_chain)
        except Exception as e:
            logger.warning(f"Error fetching option chain {i} ({dat.options[i]}): {e}")
            continue
    
    if not dataframes:
        raise ValueError(f"No option data with open interest > 0 found for {ticker}")
    
    # Concatenate all dataframes
    calls_df = pd.concat(dataframes, ignore_index=True)
    logger.info(f"Fetched {len(calls_df)} call options with open interest > 0")
    
    return calls_df


def normalize_volatility(raw_volatility: float) -> float:
    """
    Normalize volatility value to decimal form.
    
    Args:
        raw_volatility: Raw volatility value (may be in percentage or decimal form)
    
    Returns:
        Volatility in decimal form (e.g., 0.20 for 20%)
    """
    if raw_volatility > 1.0:
        return raw_volatility / 100.0
    return raw_volatility


def calculate_time_to_expiration(expiration_date: Union[str, pd.Timestamp]) -> float:
    """
    Calculate time to expiration in years.
    
    Args:
        expiration_date: Expiration date as string or Timestamp
    
    Returns:
        Time to expiration in years (minimum 0.0001 to avoid division by zero)
    """
    expiration = pd.to_datetime(expiration_date)
    days_to_expiration = (expiration - pd.Timestamp.now()).days
    time_to_expiration = max(days_to_expiration / DAYS_PER_YEAR, MIN_TIME_TO_EXPIRATION)
    return time_to_expiration


def calculate_bsm_values_vectorized(
    calls_df: pd.DataFrame,
    current_stock_price: float,
    risk_free_rate: float,
    dividend_yield: float
) -> pd.DataFrame:
    """
    Calculate Black-Scholes model values for all options using vectorized operations.
    
    Args:
        calls_df: DataFrame containing option chain data
        current_stock_price: Current stock price
        risk_free_rate: Risk-free interest rate
        dividend_yield: Dividend yield
    
    Returns:
        DataFrame with added 'BSM_Model_Value' column
    """
    calls_df = calls_df.copy()
    calls_df['BSM_Model_Value'] = None
    
    # Calculate time to expiration for all rows
    calls_df['time_to_expiration'] = calls_df['expiration'].apply(calculate_time_to_expiration)
    
    # Normalize volatility
    calls_df['normalized_vol'] = calls_df['impliedVolatility'].apply(normalize_volatility)
    
    # Filter valid rows (non-null values and reasonable volatility)
    valid_mask = (
        calls_df['strike'].notna() &
        calls_df['impliedVolatility'].notna() &
        calls_df['time_to_expiration'].notna() &
        (calls_df['normalized_vol'] >= MIN_VOLATILITY) &
        (calls_df['normalized_vol'] <= MAX_VOLATILITY)
    )
    
    valid_df = calls_df[valid_mask].copy()
    
    if valid_df.empty:
        logger.warning("No valid options found for BSM calculation")
        return calls_df
    
    # Vectorized BSM calculation
    def calculate_bsm_row(row: pd.Series) -> Optional[float]:
        """Calculate BSM value for a single row."""
        try:
            option_information = [
                current_stock_price,
                float(row['strike']),
                row['time_to_expiration'],
                risk_free_rate,
                row['normalized_vol'],
                "Call",
                dividend_yield
            ]
            option_dict = return_hashmap(option_information)
            return black_scholes_calculator(option_dict)
        except (ValueError, TypeError, KeyError) as e:
            logger.debug(f"Error calculating BSM for row: {e}")
            return None
    
    # Apply BSM calculation
    valid_df['BSM_Model_Value'] = valid_df.apply(calculate_bsm_row, axis=1)
    
    # Update original dataframe
    calls_df.loc[valid_mask, 'BSM_Model_Value'] = valid_df['BSM_Model_Value']
    
    return calls_df


def analyze_bsm_vs_market(calls_df: pd.DataFrame) -> None:
    """
    Analyze and display comparison between BSM model values and market prices.
    
    Args:
        calls_df: DataFrame containing option data with BSM_Model_Value column
    """
    logger.info("Analyzing BSM Model vs Market Price")
    print("\n" + "="*80)
    print("BSM Model vs Market Price Analysis (Valid Volatility Cases)")
    print("="*80)
    
    # Filter rows with valid BSM values and market prices
    valid_rows = calls_df[
        (calls_df['BSM_Model_Value'].notna()) &
        (calls_df['impliedVolatility'].notna()) &
        (calls_df['lastPrice'].notna())
    ].copy()
    
    if valid_rows.empty:
        logger.warning("No valid rows found for analysis")
        print("\nNo valid rows found for analysis.")
        print("\n" + "="*80 + "\n")
        return
    
    # Calculate normalized volatility for filtering
    valid_rows['normalized_vol'] = valid_rows['impliedVolatility'].apply(normalize_volatility)
    
    # Filter out unusual volatility cases
    valid_rows = valid_rows[
        (valid_rows['normalized_vol'] >= MIN_VOLATILITY) &
        (valid_rows['normalized_vol'] <= MAX_VOLATILITY)
    ]
    
    if valid_rows.empty:
        logger.warning("No rows with reasonable volatility found")
        print("\nNo rows with reasonable volatility found.")
        print("\n" + "="*80 + "\n")
        return
    
    # Calculate differences
    valid_rows['price_diff'] = valid_rows['BSM_Model_Value'] - valid_rows['lastPrice']
    valid_rows['price_diff_pct'] = (valid_rows['price_diff'] / valid_rows['lastPrice']) * 100
    valid_rows['abs_diff_pct'] = valid_rows['price_diff_pct'].abs()
    
    print(f"\nAnalyzing {len(valid_rows)} options with valid volatility (1% - 200%):")
    print(f"\nAverage absolute difference: ${valid_rows['price_diff'].abs().mean():.2f}")
    print(f"Average absolute percentage difference: {valid_rows['abs_diff_pct'].mean():.2f}%")
    print(f"Median absolute percentage difference: {valid_rows['abs_diff_pct'].median():.2f}%")
    
    # Show sample comparisons
    print(f"\nSample comparisons (showing first 10):")
    print(f"{'Strike':<8} {'Days':<6} {'IV %':<8} {'Market':<10} {'BSM':<10} {'Diff $':<10} {'Diff %':<8}")
    print("-" * 70)
    
    for _, row in valid_rows.head(10).iterrows():
        iv_pct = row['normalized_vol'] * 100
        days = (pd.to_datetime(row['expiration']) - pd.Timestamp.now()).days
        print(
            f"{row['strike']:<8.0f} {days:<6} {iv_pct:<8.2f} "
            f"${row['lastPrice']:<9.2f} ${row['BSM_Model_Value']:<9.2f} "
            f"${row['price_diff']:<9.2f} {row['price_diff_pct']:<7.2f}%"
        )
    
    # Verify strike 120 rows specifically
    strike_120_rows = valid_rows[abs(valid_rows['strike'] - 120.0) < 1.0]
    if len(strike_120_rows) > 0:
        print(f"\n=== Verification: All Strike 120 Rows ===")
        print(f"Found {len(strike_120_rows)} strike 120 option(s):")
        for _, row in strike_120_rows.iterrows():
            days = (pd.to_datetime(row['expiration']) - pd.Timestamp.now()).days
            iv_pct = row['normalized_vol'] * 100
            print(
                f"  Days: {days}, IV: {iv_pct:.2f}%, Market: ${row['lastPrice']:.2f}, "
                f"BSM: ${row['BSM_Model_Value']:.2f}, Diff: ${row['price_diff']:.2f} "
                f"({row['price_diff_pct']:.1f}%)"
            )
        print("="*50)
    
    # Count options within reasonable ranges
    within_5pct = (valid_rows['abs_diff_pct'] <= 5.0).sum()
    within_10pct = (valid_rows['abs_diff_pct'] <= 10.0).sum()
    
    print(f"\nOptions within 5% of market price: {within_5pct}/{len(valid_rows)} "
          f"({within_5pct/len(valid_rows)*100:.1f}%)")
    print(f"Options within 10% of market price: {within_10pct}/{len(valid_rows)} "
          f"({within_10pct/len(valid_rows)*100:.1f}%)")
    
    print("\n" + "="*80 + "\n")


def query_yfinance(
    ticker: str,
    option_range: int,
    risk_free_rate: float = DEFAULT_RISK_FREE_RATE,
    dividend_yield: float = DEFAULT_DIVIDEND_YIELD
) -> pd.DataFrame:
    """
    Query Yahoo Finance for option chain data and calculate Black-Scholes model values.
    
    Args:
        ticker: Stock ticker symbol
        option_range: Number of expiration dates to fetch
        risk_free_rate: Risk-free interest rate (default: 0.05)
        dividend_yield: Dividend yield (default: 0.02)
    
    Returns:
        DataFrame containing option chain data with BSM_Model_Value column
    """
    # Fetch option chain data
    calls_df = fetch_option_chain_data(ticker, option_range)
    
    # Get current stock price
    logger.info(f"Fetching current stock price for {ticker}")
    dat = yf.Ticker(ticker)
    current_stock_price = dat.history(period="1d")['Close'].iloc[-1]
    logger.info(f"Current stock price: ${current_stock_price:.2f}")
    
    # Calculate BSM values
    calls_df = calculate_bsm_values_vectorized(
        calls_df,
        current_stock_price,
        risk_free_rate,
        dividend_yield
    )
    
    # Analyze results
    analyze_bsm_vs_market(calls_df)
    
    return calls_df


if __name__ == "__main__":
    query_yfinance("AAPL", 20)
