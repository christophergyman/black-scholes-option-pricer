# Black-Scholes Option Pricer

A custom implementation of the Black-Scholes-Merton option pricing model with real-time market data integration. This project provides a hands-on approach to understanding derivatives pricing, mathematical modeling, and identifying potential market inefficiencies.

## 📚 About This Project

This project has been an incredible learning journey into the world of derivatives pricing and quantitative finance. Building this Black-Scholes option pricer from scratch has deepened my understanding of:

- **Mathematical Finance**: Implementing the Black-Scholes-Merton model with support for dividend yields
- **Real-Time Data Analysis**: Integrating live market data from Yahoo Finance to compare theoretical model prices with actual market prices
- **Market Inefficiencies**: Using mathematical logic and statistical analysis to identify discrepancies between model predictions and market reality
- **Python Best Practices**: Writing production-ready code with proper error handling, type hints, and performance optimization

The ability to apply rigorous mathematical models to real-time financial data and observe how theoretical prices compare to market prices has been both intellectually stimulating and practically valuable. This project demonstrates how quantitative analysis can reveal insights into market behavior and potential arbitrage opportunities.

## ✨ Features

- **Full Black-Scholes-Merton Implementation**: Complete option pricing model with support for:
  - Call and Put options
  - Dividend yield adjustments
  - Custom risk-free rate and volatility inputs
  
- **Real-Time Market Data Integration**: 
  - Fetches live option chain data from Yahoo Finance
  - Compares theoretical model prices with actual market prices
  - Analyzes pricing discrepancies across multiple expiration dates

- **Performance Optimized**:
  - Vectorized pandas operations for efficient data processing
  - Performance benchmarking capabilities
  - Optimized mathematical calculations

- **Production-Ready Code**:
  - Comprehensive error handling and validation
  - Type hints throughout
  - Professional logging framework
  - PEP 8 compliant code style
  - Extensive documentation

## 🚀 Installation

### Prerequisites

- Python 3.8 or higher
- pip package manager

### Setup

1. Clone the repository:
```bash
git clone https://github.com/yourusername/black-scholes-option-pricer.git
cd black-scholes-option-pricer
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

## 📖 Usage

### Basic Option Pricing

```python
from src.main import return_hashmap, black_scholes_calculator

# Define option parameters: [asset_price, strike_price, expiration (years), 
#                           risk_free_rate, volatility, option_type, dividend_yield]
option_info = [100.0, 105.0, 0.25, 0.05, 0.20, "Call", 0.02]

# Convert to dictionary format
option = return_hashmap(option_info)

# Calculate option price
price = black_scholes_calculator(option)
print(f"Option price: ${price:.2f}")
```

### Real-Time Market Analysis

Analyze live option chain data and compare with Black-Scholes model prices:

```python
from src.main import query_yfinance

# Analyze AAPL options across 20 expiration dates
results = query_yfinance("AAPL", option_range=20)
```

This will:
- Fetch call options with open interest > 0
- Calculate Black-Scholes model prices for each option
- Compare model prices with market prices
- Display statistical analysis of pricing discrepancies
- Identify options where model and market prices differ significantly

### Performance Benchmarking

```python
from src.main import performance_test

# Run 10,000 iterations to benchmark calculation speed
performance_test(10000)
```

## 📊 Example Output

When running the market analysis, you'll see output like:

```
================================================================================
BSM Model vs Market Price Analysis (Valid Volatility Cases)
================================================================================

Analyzing 450 options with valid volatility (1% - 200%):

Average absolute difference: $2.34
Average absolute percentage difference: 8.45%
Median absolute percentage difference: 6.23%

Sample comparisons (showing first 10):
Strike   Days   IV %     Market     BSM        Diff $     Diff %  
----------------------------------------------------------------------
150      30     25.50    $5.20      $5.45      $0.25      4.81%
155      30     24.30    $3.10      $3.28      $0.18      5.81%
...
```

## 🏗️ Project Structure

```
black-scholes-option-pricer/
├── src/
│   └── main.py              # Main implementation
├── requirements.txt         # Python dependencies
├── README.md               # This file
└── LICENSE                 # License information
```

## 🔧 Technical Details

### Black-Scholes-Merton Formula

**Call Option:**
```
C = S₀ × e^(-q×T) × N(d₁) - K × e^(-r×T) × N(d₂)
```

**Put Option:**
```
P = K × e^(-r×T) × N(-d₂) - S₀ × e^(-q×T) × N(-d₁)
```

Where:
- `S₀` = Current asset price
- `K` = Strike price
- `r` = Risk-free interest rate
- `q` = Dividend yield
- `T` = Time to expiration (in years)
- `σ` = Volatility
- `N()` = Cumulative standard normal distribution
- `d₁` = [ln(S/K) + (r - q + σ²/2) × T] / (σ × √T)
- `d₂` = d₁ - σ × √T

### Key Functions

- `return_hashmap()`: Validates and converts option parameters to dictionary format
- `d1_value()` / `d2_value()`: Calculate standardized measures for the Black-Scholes model
- `black_scholes_calculator()`: Main pricing function
- `query_yfinance()`: Fetches real-time data and performs comparative analysis
- `calculate_bsm_values_vectorized()`: Efficiently calculates prices for multiple options
- `analyze_bsm_vs_market()`: Statistical analysis of model vs market prices

## 📦 Dependencies

- `pandas` >= 2.0.0 - Data manipulation and analysis
- `yfinance` >= 0.2.0 - Yahoo Finance market data
- `scipy` >= 1.10.0 - Statistical functions (normal distribution)

## 🎯 Learning Outcomes

This project has provided hands-on experience with:

1. **Mathematical Modeling**: Implementing complex financial formulas in code
2. **Data Science**: Processing and analyzing large datasets of financial instruments
3. **Market Analysis**: Identifying patterns and inefficiencies in option pricing
4. **Software Engineering**: Writing maintainable, well-documented, production-quality code
5. **Quantitative Finance**: Understanding the relationship between theoretical models and market reality

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📝 License

See the [LICENSE](LICENSE) file for details.

## ⚠️ Disclaimer

This project is for educational and research purposes only. It is not intended as financial advice. Option trading involves substantial risk and is not suitable for all investors. Always consult with a qualified financial advisor before making investment decisions.

## 🙏 Acknowledgments

- Black-Scholes model by Fischer Black, Myron Scholes, and Robert Merton
- Yahoo Finance for providing market data access
- The quantitative finance community for inspiration and knowledge sharing

---

**Note**: This implementation is a learning project that demonstrates the application of mathematical models to real-world financial data. The comparison between model prices and market prices can reveal interesting insights into market behavior, but should not be used as the sole basis for trading decisions.
