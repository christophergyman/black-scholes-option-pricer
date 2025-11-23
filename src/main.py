from math import log, sqrt

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
def d1Value(option: dict) -> float:
    # d1 = [ln(S/K) + (r + σ²/2) × T] / (σ × √T)

    return 0.0


## D2 standardized measure used in black-scholes 
def d2Value() -> float:
    return 0.0


# Main black scholes function to calcualte price
def blackScholesCalculator(option: dict) -> float:
    d1 = d1Value(option)
    d2 = d2Value(option)

    return 0.0


if __name__ == "__main__":
    # assetPrice: float,
    # strikePrice: float,
    # expiration: float,
    # riskFreeInterestRate: float,
    # volatility: float,
    # optionType: str,
    # dividendYield: Union[str, NoneType],

    optionInformation = [31.55, 22.75, 3.5, 0.05, 0.5, "C", 0.02]
    option = returnHashmap(optionInformation)
    blackScholesCalculator(option)
