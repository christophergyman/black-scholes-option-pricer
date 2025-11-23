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

    for i in range (iteration):
        startTime = perf_counter()
        optionPrice = blackScholesCalculator(option)
        endTime = perf_counter()
        functionTime = (endTime - startTime) * 1000000 #microseconds
        blackScholesLatencyTimes.append(functionTime)

    averageRunTime = sum(blackScholesLatencyTimes)/iteration
    
    print(f"\n {iteration} Iterations have been run and the average time for black scholes calculation is {averageRunTime} \n")


if __name__ == "__main__":
    performanceTest(100000)
