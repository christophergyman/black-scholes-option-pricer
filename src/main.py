import yfinance as yf
import pandas as pd
from math import log, sqrt, exp
from scipy.stats import norm
from time import perf_counter


# convert input to dict
def returnHashmap(optionInformation: list) -> dict:
    # validate float types for first 5 values
    for i in range(5):
        if (type(optionInformation[i]) != float) and (optionInformation[i] < 0.0):
            print(f"error: {optionInformation[i]} value is not correct type ...")
            break
            quit()

    # valdiate option type input
    if optionInformation[5] != ("C" or "c" or "Call" or "P" or "p" or "Put"):
        print(f"error: {optionInformation[5]} value is not correct type ...")
        quit()
    elif optionInformation[5] == ("C" or "c" or "Call"):
        optionInformation[5] = "Call"
    elif optionInformation[5] == ("P" or "p" or "Put"):
        optionInformation[5] = "Put"

    # validate divident yeield
    if type(optionInformation[6]) != float:
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
    # d1 = [ln(S/K) + (r + σ²/2) × T] / (σ × √T)
    d1 = (
        log(option["assetPrice"] / option["strikePrice"])
        + (option["riskFreeInterestRate"] + ((option["volatility"] ** 2) / 2))
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

    if option["optionType"] == "Call":
        # C = S₀ × N(d₁) - K × e^(-r×T) × N(d₂)
        modelCallOptionPrice = option["assetPrice"] * norm.cdf(d1) - option[
            "strikePrice"
        ] * exp(-option["riskFreeInterestRate"] * option["expiration"]) * norm.cdf(d2)
        return modelCallOptionPrice
    if option["optionType"] == "Put":
        # P = K × e^(-r×T) × N(-d₂) - S₀ × N(-d₁)
        modelPutOptionPrice = option["strikePrice"] * exp(
            -option["riskFreeInterestRate"] * option["expiration"]
        ) * norm.cdf(-d2) - option["assetPrice"] * norm.cdf(-d1)
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
        callsDF = pd.concat([callsDF, filteredDF])

    # drop first row, its only used as formatting
    callsDF.drop(0, inplace=True)

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
            time_to_expiration = days_to_expiration / 365.0  # Convert to years
            
            # Get volatility (implied volatility from the option chain)
            volatility = float(row['impliedVolatility'])
            
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

            print("done")
            
        except (ValueError, KeyError, TypeError) as e:
            # Handle any errors (missing values, type conversion issues, etc.)
            print(f"Error processing row {idx}: {e}")
            callsDF.at[idx, 'BSM_Model_Value'] = None

    # loop over each row in the dataframe
    # convert each columns and row into a temporary dict
    # pass this dictionary to blackScholesCalculator
    # the return value from the calculator should be inserted into the BSM_Model_value for that row int he dataframe



if __name__ == "__main__":
    queryYfinance("AAPL", 20)