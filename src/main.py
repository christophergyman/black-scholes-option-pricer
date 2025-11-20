from types import NoneType
from typing import Union


def blackScholes(
    assetPrice: float,
    strikePrice: float,
    expiration: float,
    riskFreeInterestRate: float,
    volatility: float,
    optionType: str,
    dividendYield: Union[str, NoneType],
) -> float:

    # Input validation
    if (
        (
            assetPrice
            and strikePrice
            and expiration
            and riskFreeInterestRate
            and volatility
            and optionType
            and dividendYield
        )
        > 0
        and (optionType == str)
        and (type(dividendYield) == str or NoneType)
    ):
        print("true")


if __name__ == "__main__":
    blackScholes()
