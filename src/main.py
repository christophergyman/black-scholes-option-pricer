from types import NoneType
from typing import Union, Any, Callable

def blackScholes(
    assetPrice: float,
    strikePrice: float,
    expiration: float,
    riskFreeInterestRate: float,
    volatility: float,
    optionType: str,
    dividendYield: Union[str, NoneType],
) -> float:

    print("Hello world")


if __name__ == "__main__":
    blackScholes()
