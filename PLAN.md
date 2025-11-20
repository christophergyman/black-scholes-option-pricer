# Derivative Pricing Calculator - Implementation Plan

## Project Structure

```
black-scholes-option-pricer/
├── backend/
│   ├── __init__.py
│   ├── app.py                 # Flask/FastAPI application entry point
│   ├── models/
│   │   ├── __init__.py
│   │   ├── options.py         # Black-Scholes pricing and Greeks
│   │   ├── futures.py         # Futures pricing (commodity, equity index)
│   │   └── swaps.py           # Swaps pricing (IRS, currency swaps)
│   ├── api/
│   │   ├── __init__.py
│   │   └── routes.py          # API endpoints for pricing calculations
│   └── utils/
│       ├── __init__.py
│       └── math_utils.py      # Helper functions (CDF, PDF for normal distribution)
├── frontend/
│   ├── index.html             # Main application page
│   ├── css/
│   │   └── styles.css         # Styling for calculator interface
│   ├── js/
│   │   ├── main.js            # Main application logic
│   │   ├── api.js             # API communication functions
│   │   ├── charts.js          # Chart.js/Plotly.js visualization logic
│   │   └── forms.js           # Form handling and validation
│   └── assets/                # Static assets if needed
├── requirements.txt            # Python dependencies
├── README.md                   # Project documentation
└── main.py                     # Legacy entry point (can be updated or removed)
```

## Implementation Phases

### Phase 1: Core Backend Infrastructure

**Backend Setup:**
- Choose between Flask or FastAPI (FastAPI recommended for automatic API docs)
- Set up project structure with proper Python package organization
- Create `requirements.txt` with dependencies: flask/fastapi, numpy, scipy (for statistical functions)
- Implement `utils/math_utils.py` with cumulative distribution function (CDF) and probability density function (PDF) for standard normal distribution using scipy.stats or manual implementation

**API Framework:**
- Create `app.py` with basic server setup
- Configure CORS for frontend-backend communication
- Set up API route structure in `api/routes.py`
- Create health check endpoint

### Phase 2: Options Pricing (Black-Scholes)

**Core Implementation (`models/options.py`):**
- Implement Black-Scholes formula for European call and put options
- Calculate d1 and d2 parameters
- Handle dividend yield (if applicable)
- Support both call and put option types

**Greeks Calculation:**
- Delta: First derivative with respect to underlying price
- Gamma: Second derivative with respect to underlying price
- Theta: First derivative with respect to time
- Vega: First derivative with respect to volatility
- Rho: First derivative with respect to risk-free rate

**API Endpoints:**
- `POST /api/options/price` - Calculate option price
- `POST /api/options/greeks` - Calculate all Greeks
- `POST /api/options/payoff` - Generate payoff data points for visualization

### Phase 3: Futures Pricing

**Implementation (`models/futures.py`):**
- **Commodity Futures:** Forward price formula F = S * e^(r*T) with cost of carry
- **Equity Index Futures:** F = S * e^((r-d)*T) where d is dividend yield
- Handle storage costs and convenience yield for commodities
- Support different contract specifications

**API Endpoints:**
- `POST /api/futures/price` - Calculate futures price
- `POST /api/futures/payoff` - Generate payoff data for visualization

### Phase 4: Swaps Pricing

**Implementation (`models/swaps.py`):**
- **Interest Rate Swaps (IRS):**
  - Fixed-for-floating swap valuation
  - Calculate fixed leg present value
  - Calculate floating leg present value (using forward rates)
  - Net present value = PV(floating) - PV(fixed)
- **Currency Swaps:**
  - Cross-currency swap valuation
  - Handle different currencies and exchange rates
  - Calculate both legs in respective currencies

**API Endpoints:**
- `POST /api/swaps/irs/price` - Calculate IRS value
- `POST /api/swaps/currency/price` - Calculate currency swap value
- `POST /api/swaps/payoff` - Generate payoff data

### Phase 5: Frontend Implementation

**HTML Structure (`frontend/index.html`):**
- Create tabbed or sectioned interface for Options, Futures, and Swaps
- Input forms for each derivative type:
  - Options: S, K, T, r, σ, option type (call/put)
  - Futures: Spot price, risk-free rate, time to maturity, cost of carry/dividend yield
  - Swaps: Notional, fixed rate, floating rate curve, payment frequency, maturity
- Results display area for calculated prices and Greeks
- Chart containers for visualizations

**Styling (`frontend/css/styles.css`):**
- Modern, clean UI design
- Responsive layout
- Clear form layouts with proper labels
- Chart container styling

**JavaScript Core (`frontend/js/main.js`):**
- Application initialization
- Tab/section switching logic
- Form data collection and validation
- Results display management

**API Communication (`frontend/js/api.js`):**
- Functions to call backend endpoints
- Error handling
- Data transformation between frontend and backend formats

**Form Handling (`frontend/js/forms.js`):**
- Input validation
- Real-time calculation triggers
- Form state management

### Phase 6: Visualizations

**Chart Library Selection:**
- Choose Chart.js, Plotly.js, or D3.js (Plotly.js recommended for financial charts)
- Include library via CDN or local file

**Visualization Implementation (`frontend/js/charts.js`):**
- **Payoff Diagrams:**
  - Options: Profit/loss vs underlying price at expiration
  - Futures: Profit/loss vs underlying price
  - Swaps: Net cash flow over time
- **Greeks Visualization:**
  - Line charts showing how each Greek changes with underlying price
  - Surface plots for Greeks vs multiple variables (if using 3D capable library)
- **Price Sensitivity Charts:**
  - Option price vs underlying price (multiple volatility levels)
  - Option price vs time to expiration
  - Option price vs volatility (volatility smile)
  - Greeks heatmaps or contour plots

**Chart Update Logic:**
- Dynamic chart generation based on user inputs
- Real-time updates when inputs change
- Multiple chart instances for different visualizations

### Phase 7: Integration and Testing

**Integration:**
- Connect all frontend forms to backend APIs
- Ensure data flow works end-to-end
- Test all calculation paths

**Error Handling:**
- Backend: Validate inputs, return appropriate error messages
- Frontend: Display user-friendly error messages
- Handle edge cases (negative values, invalid ranges, etc.)

**Local Development Setup:**
- Instructions for running backend server
- Instructions for serving frontend (simple HTTP server or integrated with backend)
- Development workflow documentation

## Key Technical Considerations

**Performance:**
- Use numpy for vectorized calculations where possible
- Cache repeated calculations (e.g., normal CDF lookups)
- Optimize chart rendering for large datasets

**Mathematical Accuracy:**
- Use high-precision libraries (scipy.stats.norm) for statistical functions
- Implement proper numerical methods for Greeks (finite differences or analytical derivatives)
- Validate against known textbook examples

**User Experience:**
- Real-time calculations as user types (with debouncing)
- Clear labeling of all inputs and outputs
- Tooltips or help text for financial terms
- Responsive design for different screen sizes

## Dependencies

**Backend:**
- Flask or FastAPI
- numpy (numerical computations)
- scipy (statistical functions)
- flask-cors or fastapi-cors (CORS handling)

**Frontend:**
- Chart.js, Plotly.js, or D3.js (visualization)
- No framework required (vanilla JS) or optional lightweight framework

## Reference Formulas

**Black-Scholes:**
- Call: C = S*N(d1) - K*e^(-r*T)*N(d2)
- Put: P = K*e^(-r*T)*N(-d2) - S*N(-d1)
- d1 = (ln(S/K) + (r + σ²/2)*T) / (σ*√T)
- d2 = d1 - σ*√T

**Futures:**
- F = S * e^((r - d + u - y)*T) where u = storage cost, y = convenience yield

**Swaps:**
- IRS: Value = PV(floating leg) - PV(fixed leg)
- Use discount factors and forward rates for floating leg valuation

## Implementation Todos

1. **Setup Backend** - Set up backend project structure with Flask/FastAPI, create app.py, configure CORS, and set up basic API route structure

2. **Math Utils** - Implement math_utils.py with CDF and PDF functions for standard normal distribution

3. **Black-Scholes** - Implement Black-Scholes option pricing formula in models/options.py with support for calls and puts (depends on: Math Utils)

4. **Greeks Calculation** - Implement all Greeks (delta, gamma, theta, vega, rho) calculations in models/options.py (depends on: Black-Scholes)

5. **Options API** - Create API endpoints for options pricing, Greeks, and payoff data generation (depends on: Greeks Calculation)

6. **Futures Pricing** - Implement futures pricing models for commodity and equity index futures in models/futures.py (depends on: Math Utils)

7. **Futures API** - Create API endpoints for futures pricing and payoff data (depends on: Futures Pricing)

8. **Swaps Pricing** - Implement interest rate swaps and currency swaps pricing in models/swaps.py (depends on: Math Utils)

9. **Swaps API** - Create API endpoints for IRS and currency swap pricing (depends on: Swaps Pricing)

10. **Frontend HTML** - Create index.html with tabbed interface and input forms for all derivative types

11. **Frontend Styling** - Implement CSS styling for modern, responsive UI design (depends on: Frontend HTML)

12. **Frontend API** - Implement API communication functions in frontend/js/api.js to connect with backend (depends on: Frontend HTML)

13. **Frontend Forms** - Implement form handling, validation, and data collection in frontend/js/forms.js (depends on: Frontend HTML)

14. **Payoff Visualization** - Implement payoff diagram visualizations for options, futures, and swaps (depends on: Frontend API, Frontend Forms)

15. **Greeks Visualization** - Implement Greeks visualization charts showing how each Greek changes with underlying price (depends on: Frontend API, Payoff Visualization)

16. **Sensitivity Charts** - Implement price sensitivity charts (price vs underlying, time, volatility) and Greeks heatmaps (depends on: Greeks Visualization)

17. **Integration Testing** - Integrate all components, add error handling, and test end-to-end functionality (depends on: Sensitivity Charts)

