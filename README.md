# DSCI Hackathon 2024 — Vancouver Business Licenses (1997–2024)

## Team Members
- Fisher
- Neerja
- Siluni
- Minh


# 📉 Crash Tested  
A data-driven study of how major Canadian financial crises affected business sectors, and how these historical patterns can be used to understand and evaluate the **current recession**.

## Team Members
- Fisher
- Neerja
- Siluni
- Minh

## 🧭 Project Aim

This project investigates five major Canadian recessions to uncover:
- The **causes** behind each downturn  
- **Which business sectors grew or declined**  
- **Why** certain industries were resilient while others collapsed  
- **Patterns** that repeat across different crises  
- **Predictors** of business vulnerability  

By identifying these cross-crisis patterns, we connect them directly to **today’s recession**, allowing us to evaluate:
- Which sectors are currently most vulnerable  
- Which businesses are likely to remain stable  
- Whether current economic trends resemble past downturns  
- How historical behavior can inform tomorrow’s business decisions  

The end goal is to build a clear, evidence-based framework for understanding and forecasting **how the current recession will impact businesses in cities like Vancouver**.

---

## 🕰️ Crises Analyzed

We examine the following major downturns:

1. **Dot-Com Crash (2000–2002)**
2. **Great Recession / Housing & Credit Crisis (2008–2009)**
3. **Oil Price Crash (2014–2016)**
4. **COVID-19 Shutdown Recession (2020–2021)**
5. **Interest Rate & Inflation Shock (2022–2024)**

## Datasets
Links to Vancouver Open Data Portal:
- Business Licenses (1997–2012)
- Business Licenses (2013–2024)
- Current Business Licenses (2024+)



### For each crisis, we analyze:
- Economic trigger  
- Sector-level performance  
- Business openings vs closures  
- Explanation of trends based on economic conditions  
- Long-term effects  

---

## 🔗 Connecting Historical Crises to the Current Recession

Our project does **not** attempt to fully model or predict the 2024–2025 recession.  
Instead, we use historical patterns to **contextualize** what is happening today.

We connect our findings to the current recession by:

- Identifying **recurring sector behaviors** across past downturns (resilience, vulnerability, cyclicality)  
- Using these patterns as a **framework** to interpret early signs of the current recession  
- Comparing general economic signals today (slower growth, reduced openings) to typical historical trends  
- Highlighting historically **vulnerable** and **resilient** sectors to provide context for potential pressures  
- Building a foundation for future work that could directly analyze **current Vancouver business license data or economic indicators**  

---

# DSCI Hackathon 2024 — Vancouver Business Licenses (1997–2024)

## Team Members
- Fisher
- Neerja
- Siluni
- Minh

---

# 📉 Crash Tested  
A data-driven study of how major Canadian financial crises affected business sectors, and how these historical patterns can be used to understand and evaluate the **current recession**.

## 🧭 Project Aim

This project investigates five major Canadian recessions to uncover:
- The **causes** behind each downturn  
- **Which business sectors grew or declined**  
- **Why** certain industries were resilient while others collapsed  
- **Patterns** that repeat across different crises  
- **Predictors** of business vulnerability  

By identifying these cross-crisis patterns, we connect them directly to **today's recession**, allowing us to evaluate:
- Which sectors are currently most vulnerable  
- Which businesses are likely to remain stable  
- Whether current economic trends resemble past downturns  
- How historical behavior can inform tomorrow's business decisions  

The end goal is to build a clear, evidence-based framework for understanding and forecasting **how the current recession will impact businesses in cities like Vancouver**.

---

## 🕰️ Crises Analyzed

We examine the following major downturns:

1. **Dot-Com Crash (2000–2002)**
2. **Great Recession / Housing & Credit Crisis (2008–2009)**
3. **Oil Price Crash (2014–2016)**
4. **COVID-19 Shutdown Recession (2020–2021)**
5. **Interest Rate & Inflation Shock (2022–2024)**

### For each crisis, we analyze:
- Economic trigger  
- Sector-level performance  
- Business openings vs closures  
- Explanation of trends based on economic conditions  
- Long-term effects  

---

## 📊 Datasets

Data sourced from Vancouver Open Data Portal:
- [Business Licenses (1997–2012)](https://opendata.vancouver.ca/explore/dataset/business-licences-1997-to-2012)
- [Business Licenses (2013–2024)](https://opendata.vancouver.ca/explore/dataset/business-licences-2013-to-2024)
- [Current Business Licenses (2024+)](https://opendata.vancouver.ca/explore/dataset/business-licences)

**Total Records**: ~30,000 business licenses spanning 27 years

---

## 🔗 Connecting Historical Crises to the Current Recession

Our project does **not** attempt to fully model or predict the 2024–2025 recession.  
Instead, we use historical patterns to **contextualize** what is happening today.

We connect our findings to the current recession by:

- Identifying **recurring sector behaviors** across past downturns (resilience, vulnerability, cyclicality)  
- Using these patterns as a **framework** to interpret early signs of the current recession  
- Comparing general economic signals today (slower growth, reduced openings) to typical historical trends  
- Highlighting historically **vulnerable** and **resilient** sectors to provide context for potential pressures  
- Building a foundation for future work that could directly analyze **current Vancouver business license data or economic indicators**  

---

## 🛠️ Technical Approach

### Data Pipeline

1. **Data Acquisition** (`fetch_data.py`)
   - Parallel API requests using ThreadPoolExecutor
   - Fetches from 3 separate Vancouver Open Data endpoints
   - ~15 concurrent workers for optimal throughput
   - Handles pagination and rate limiting

2. **Data Cleaning** (`clean_data.py`)
   - Standardizes column names and formats
   - Normalizes business types and statuses
   - Handles mixed date formats (ISO 8601 with/without timezone)
   - Consolidates 30,000+ records into unified dataset

3. **Crisis Analysis** (`crisis_analysis.py`)
   - Identifies crisis periods using date ranges
   - Calculates baseline vs crisis period metrics
   - **Bootstrap resampling** (1,000 iterations) for confidence intervals
   - Linear regression forecasting for 2025-2029
   - Statistical modeling with OLS regression

### Statistical Methods

#### Bootstrap Confidence Intervals
- **Purpose**: Quantify uncertainty in crisis impact estimates
- **Method**: Poisson resampling (appropriate for count data)
- **Iterations**: 1,000 bootstrap samples
- **Output**: 95% confidence intervals for all metrics

#### Forecasting
- **Model**: Linear regression on historical yearly counts
- **Bootstrap**: 500 samples per business type
- **Horizon**: 2025-2029 (5-year forecast)
- **Output**: Predicted counts with confidence bounds

#### Crisis Impact Model
- **Dependent Variable**: Monthly business license count
- **Independent Variable**: Crisis indicator (binary)
- **Method**: OLS regression with bootstrapped coefficients
- **Purpose**: Test statistical significance of crisis effects

---

## 📈 Key Findings

### Crisis Patterns Discovered

1. **Contractor Dominance During Downturns**
   - Electrical, general, and specialty contractors consistently rank in top 5 during all crises
   - Suggests construction/renovation as recession-resistant sector

2. **Sector-Specific Vulnerabilities**
   - Retail and hospitality show highest volatility
   - Professional services (office, financial) remain stable
   - Short-term rental sector exploded 2023-2024

3. **Recovery Timelines**
   - Dot-Com: ~2 years to baseline
   - Great Recession: ~3 years to baseline
   - COVID-19: Rapid V-shaped recovery (data gap limits full analysis)

4. **Current Recession Indicators (2022-2024)**
   - Interest rate shock period shows 9,945 licenses
   - Dominated by short-term rental operators
   - Suggests shift toward alternative income sources

### Statistical Significance
- Crisis periods show **not statistically significant** impact on monthly license counts (p > 0.05)
- Suggests other factors (seasonality, long-term trends) dominate short-term crisis effects
- Indicates resilience in Vancouver's business ecosystem

---

## 🚀 Getting Started

### Prerequisites
```bash
Python 3.9+
pip install -r requirements.txt
```

### Installation
```bash
git clone https://github.com/your-team/dsci-hackathon-2025.git
cd dsci-hackathon-2025
pip install -r requirements.txt
```

### Running the Analysis

1. **Fetch Raw Data**
```bash
   python notebooks/fetch_data.py
```
   - Downloads ~30,000 records from Vancouver Open Data
   - Takes ~2-3 minutes with 15 concurrent workers

2. **Clean & Merge Data**
```bash
   python notebooks/clean_data.py
```
   - Produces `business_licences_1997_2024.csv`
   - Handles date format inconsistencies

3. **Run Crisis Analysis**
```bash
   python notebooks/crisis_analysis.py
```
   - Generates all statistical analyses
   - Produces forecasts with confidence intervals
  

4. **Generate Visualizations**
```bash
   jupyter notebook notebooks/visualization.ipynb
```
   - Interactive plots and charts
   - Export publication-ready figures

---

## 📊 Dependencies
```txt
pandas>=2.0.0
numpy>=1.24.0
matplotlib>=3.7.0
seaborn>=0.12.0
scikit-learn>=1.3.0
statsmodels>=0.14.0
scipy>=1.10.0
requests>=2.31.0
jupyter>=1.0.0
```

---

## 🔍 Data Limitations

### Known Issues

1. **Missing Years (2021-2022)**
   - Dataset gap between `2013_2024.csv` and `current_2024_plus.csv`
   - Impacts COVID-19 and Interest Rate Shock baseline calculations
   - **Solution**: Adjusted baseline years or flagged as insufficient data

2. **Date Format Inconsistencies**
   - Pre-2020: Simple dates (`1998-02-25`)
   - Post-2020: ISO 8601 with timezone (`2023-03-01T05:57:01+00:00`)
   - Handled with timezone-aware parsing

3. **Business Type Evolution**
   - Category names changed over time (e.g., `*historic*` suffix added)
   - Normalization applied for consistency

4. **Incomplete Status Information**
   - Some records missing `status` field
   - ~15% null values for business status

---

## 🎯 Future Work

1. **Fill Data Gaps**
   - Source 2021-2022 data from Vancouver Open Data archives
   - Complete COVID-19 recession analysis

2. **Enhanced Forecasting**
   - Incorporate external economic indicators (GDP, unemployment, interest rates)
   - ARIMA/SARIMA models for seasonal patterns
   - Machine learning models (Random Forest, XGBoost)

3. **Real-Time Dashboard**
   - Live connection to Vancouver Open Data API
   - Automated monthly updates
   - Interactive Tableau/PowerBI visualizations

4. **Comparative Analysis**
   - Compare Vancouver to other Canadian cities
   - Cross-city resilience patterns

5. **Sectoral Deep Dives**
   - Industry-specific reports
   - Supply chain vulnerability mapping

---

## 📝 License

This project is licensed under the MIT License - see LICENSE file for details.

---

## 🙏 Acknowledgments

- **Vancouver Open Data**: For providing comprehensive business license datasets
- **DSCI Hackathon Organizers**: For the opportunity and support

---


