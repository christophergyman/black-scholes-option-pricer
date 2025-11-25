import yfinance as yf
import pandas as pd
from math import log, sqrt, exp
from scipy.stats import norm
from time import perf_counter
import numbers


# convert input to dict
def returnHashmap(optionInformation: list) -> dict:
    # validate float types for first 5 values
    for i in range(5):
        if not isinstance(optionInformation[i], numbers.Real) or (optionInformation[i] < 0.0):
            print(f"error: {optionInformation[i]} value is not correct type ...")
            break
            quit()

    # valdiate option type input
    if optionInformation[5] not in ("C", "c", "Call", "P", "p", "Put"):
        print(f"error: {optionInformation[5]} value is not correct type ...")
        quit()
    elif optionInformation[5] in ("C", "c", "Call"):
        optionInformation[5] = "Call"
    elif optionInformation[5] in ("P", "p", "Put"):
        optionInformation[5] = "Put"

    # validate divident yeield
    if not isinstance(optionInformation[6], numbers.Real):
        print(type(optionInformation[6]))
        print(f"error: {optionInformation[6]} value is not correct type ...")
        quit()

    return {
        "assetPrice": optionInformation[0],
        "strikePrice": optionInformation[1],
        "expiration": optionInformation[2],
        "riskFreeInterestRate": optionInformation[3],
        "volatility": optionInformation[4],
        "optionType": optionInformation[5],
        "dividentYield": optionInformation[6],
    }


## D1 standardized measure used in black-scholes
# d1 estimates the expected value of the stock relative to the strike, accounting for volatility and time.
def d1Value(option: dict) -> float:
    # d1 = [ln(S/K) + (r - q + σ²/2) × T] / (σ × √T)
    # where q is the dividend yield
    d1 = (
        log(option["assetPrice"] / option["strikePrice"])
        + (option["riskFreeInterestRate"] - option["dividentYield"] + ((option["volatility"] ** 2) / 2))
        * option["expiration"]
    ) / (option["volatility"] * sqrt(option["expiration"]))

    return d1


## D2 standardized measure used in black-scholes
# d2 estimates the probability of exercise at expiration.
def d2Value(option: dict, d1: float) -> float:
    # d2 = d₁ - σ × √T
    d2 = d1 - option["volatility"] * sqrt(option["expiration"])
    return d2


# Main black scholes function to calcualte price
def blackScholesCalculator(option: dict) -> float:
    d1 = d1Value(option)
    d2 = d2Value(option, d1)
    
    # Discount factors
    discount_factor_r = exp(-option["riskFreeInterestRate"] * option["expiration"])
    discount_factor_q = exp(-option["dividentYield"] * option["expiration"])

    if option["optionType"] == "Call":
        # C = S₀ × e^(-q×T) × N(d₁) - K × e^(-r×T) × N(d₂)
        modelCallOptionPrice = option["assetPrice"] * discount_factor_q * norm.cdf(d1) - option[
            "strikePrice"
        ] * discount_factor_r * norm.cdf(d2)
        return modelCallOptionPrice
    if option["optionType"] == "Put":
        # P = K × e^(-r×T) × N(-d₂) - S₀ × e^(-q×T) × N(-d₁)
        modelPutOptionPrice = option["strikePrice"] * discount_factor_r * norm.cdf(-d2) - option["assetPrice"] * discount_factor_q * norm.cdf(-d1)
        return modelPutOptionPrice
    else:
        return None


def performanceTest(iteration: int) -> None:

    optionInformation = [31.45, 22.75, 3.5, 0.05, 0.5, "C", 0.02]
    option = returnHashmap(optionInformation)

    # run 1000 simulations, and print out average
    blackScholesLatencyTimes = []

    for i in range(iteration):
        startTime = perf_counter()
        optionPrice = blackScholesCalculator(option)
        endTime = perf_counter()
        functionTime = (endTime - startTime) * 1000000  # microseconds
        blackScholesLatencyTimes.append(functionTime)

    averageRunTime = sum(blackScholesLatencyTimes) / iteration

    print(
        f"\n {iteration} Iterations have been run and the average time for black scholes calculation is {averageRunTime} \n"
    )

def queryYfinance(ticker: str, optionRange: int)-> pd:
    # Todo
    # pull in live yfinance data and calculate the black scholes option model price
    # compare the difference and output to log file.
    # Query yFinance for ticket data
    dat = yf.Ticker(ticker)
    df = dat.option_chain(dat.options[0]).calls

    # initialise clean empty dataframe
    callsDF = {}
    columnValues = df.columns.values
    for i, value in enumerate(columnValues):
        callsDF.update({value: [i]})
    callsDF = pd.DataFrame(callsDF)

    # filter and concat all openInterest > 0 calls
    for i in range(optionRange):
        filteredDF = dat.option_chain(dat.options[i]).calls
        filteredDF = filteredDF[filteredDF['openInterest'] > 0]
        # Add expiration date column to track which expiration each row belongs to
        filteredDF['expiration'] = dat.options[i]
        callsDF = pd.concat([callsDF, filteredDF], ignore_index=True)

    # drop first row, its only used as formatting
    callsDF.drop(0, inplace=True)
    
    # Reset index to ensure unique indices after dropping
    callsDF.reset_index(drop=True, inplace=True)

    callsDF['BSM_Model_Value'] = None

    # Get current stock price (needed for assetPrice)
    current_stock_price = dat.history(period="1d")['Close'].iloc[-1]

    # You'll need to set these values (or fetch them):
    risk_free_rate = 0.05  # Example: 5% - you may want to fetch this from a source
    dividend_yield = 0.02  # Example: 2% - you may want to fetch this from ticker info

    # Loop over each row in the dataframe
    for idx, row in callsDF.iterrows():
        try:
            # Extract values from the row
            strike_price = float(row['strike'])
            
            # Calculate time to expiration (in years)
            # Assuming 'expiration' column exists as a date, convert to days then years
            expiration_date = pd.to_datetime(row['expiration'])
            days_to_expiration = (expiration_date - pd.Timestamp.now()).days
            time_to_expiration = max(days_to_expiration / 365.0, 0.0001)  # Convert to years, ensure positive
            
            # Get volatility (implied volatility from the option chain)
            # yfinance returns implied volatility as a decimal (e.g., 0.20 = 20%)
            # Typical IV values are between 0.10 (10%) and 0.50 (50%) for most stocks
            raw_volatility = float(row['impliedVolatility'])
            
            # Normalize volatility: yfinance typically returns as decimal
            # If value > 1.0, it's likely in percentage form and needs to be divided by 100
            # If value <= 1.0, it's already in decimal form (0.0429 = 4.29%)
            if raw_volatility > 1.0:
                volatility = raw_volatility / 100.0
            else:
                volatility = raw_volatility
            
            # Sanity check: volatility should be reasonable (between 0.01 and 2.0)
            # Note: Unusual volatility values are filtered out in the analysis
            
            # Option type - since we're only processing calls
            option_type = "Call"
            
            # Build the option information list as expected by returnHashmap
            option_information = [
                current_stock_price,      # assetPrice
                strike_price,             # strikePrice
                time_to_expiration,       # expiration (in years)
                risk_free_rate,           # riskFreeInterestRate
                volatility,               # volatility
                option_type,              # optionType
                dividend_yield            # dividentYield
            ]
            
            # Convert to dictionary format
            option_dict = returnHashmap(option_information)
            
            # Calculate Black-Scholes model value
            bsm_value = blackScholesCalculator(option_dict)
            
            # Store the result in the BSM_Model_Value column
            callsDF.at[idx, 'BSM_Model_Value'] = bsm_value
            
        except (ValueError, KeyError, TypeError) as e:
            # Handle any errors (missing values, type conversion issues, etc.)
            callsDF.at[idx, 'BSM_Model_Value'] = None

    # Analyze BSM values vs market prices for valid volatility cases
    print("\n" + "="*80)
    print("BSM Model vs Market Price Analysis (Valid Volatility Cases)")
    print("="*80)
    
    # Filter rows with valid BSM values and reasonable volatility
    valid_rows = callsDF[
        (callsDF['BSM_Model_Value'].notna()) & 
        (callsDF['impliedVolatility'].notna()) &
        (callsDF['lastPrice'].notna())
    ].copy()
    
    # Calculate normalized volatility for filtering
    valid_rows['normalized_vol'] = valid_rows['impliedVolatility'].apply(
        lambda x: x / 100.0 if x > 1.0 else x
    )
    
    # Filter out unusual volatility cases (keep between 0.01 and 2.0)
    valid_rows = valid_rows[
        (valid_rows['normalized_vol'] >= 0.01) & 
        (valid_rows['normalized_vol'] <= 2.0)
    ]
    
    if len(valid_rows) > 0:
        valid_rows['price_diff'] = valid_rows['BSM_Model_Value'] - valid_rows['lastPrice']
        valid_rows['price_diff_pct'] = (valid_rows['price_diff'] / valid_rows['lastPrice']) * 100
        valid_rows['abs_diff_pct'] = valid_rows['price_diff_pct'].abs()
        
        print(f"\nAnalyzing {len(valid_rows)} options with valid volatility (1% - 200%):")
        print(f"\nAverage absolute difference: ${valid_rows['price_diff'].abs().mean():.2f}")
        print(f"Average absolute percentage difference: {valid_rows['abs_diff_pct'].mean():.2f}%")
        print(f"Median absolute percentage difference: {valid_rows['abs_diff_pct'].median():.2f}%")
        
        # Show some examples
        print(f"\nSample comparisons (showing first 10):")
        print(f"{'Strike':<8} {'Days':<6} {'IV %':<8} {'Market':<10} {'BSM':<10} {'Diff $':<10} {'Diff %':<8}")
        print("-" * 70)
        
        for _, row in valid_rows.head(10).iterrows():
            iv_pct = row['normalized_vol'] * 100
            days = (pd.to_datetime(row['expiration']) - pd.Timestamp.now()).days
            print(f"{row['strike']:<8.0f} {days:<6} {iv_pct:<8.2f} ${row['lastPrice']:<9.2f} ${row['BSM_Model_Value']:<9.2f} ${row['price_diff']:<9.2f} {row['price_diff_pct']:<7.2f}%")
        
        # Verify strike 120 rows specifically
        strike_120_rows = valid_rows[abs(valid_rows['strike'] - 120.0) < 1.0]
        if len(strike_120_rows) > 0:
            print(f"\n=== Verification: All Strike 120 Rows ===")
            print(f"Found {len(strike_120_rows)} strike 120 option(s):")
            for idx, row in strike_120_rows.iterrows():
                days = (pd.to_datetime(row['expiration']) - pd.Timestamp.now()).days
                iv_pct = row['normalized_vol'] * 100
                print(f"  Days: {days}, IV: {iv_pct:.2f}%, Market: ${row['lastPrice']:.2f}, BSM: ${row['BSM_Model_Value']:.2f}, Diff: ${row['price_diff']:.2f} ({row['price_diff_pct']:.1f}%)")
            print("="*50)
        
        # Count how many are within reasonable ranges
        within_5pct = (valid_rows['abs_diff_pct'] <= 5.0).sum()
        within_10pct = (valid_rows['abs_diff_pct'] <= 10.0).sum()
        
        print(f"\nOptions within 5% of market price: {within_5pct}/{len(valid_rows)} ({within_5pct/len(valid_rows)*100:.1f}%)")
        print(f"Options within 10% of market price: {within_10pct}/{len(valid_rows)} ({within_10pct/len(valid_rows)*100:.1f}%)")
    else:
        print("\nNo valid rows found for analysis.")
    
    print("\n" + "="*80 + "\n")



if __name__ == "__main__":
    queryYfinance("AAPL", 20)