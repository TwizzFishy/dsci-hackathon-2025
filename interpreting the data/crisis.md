# Predictive Model for Business Survival During Economic Crises
## Technical Documentation and Methodology

---

## Executive Summary

This analysis develops a machine learning model to predict which types of businesses in Vancouver are most vulnerable during economic crises. By analyzing ~26,000 business licenses from 1997-2024 across five major economic downturns, we identify vulnerability patterns and provide predictive insights for future recessions.

---

## 1. Methodology

### 1.1 Model Selection: Random Forest Classifier

**Why Random Forest?**

We selected a **Random Forest Classifier** as our primary predictive model for several key reasons:

1. **Handles Non-Linear Relationships**: Business survival during crises isn't linear—interactions between business type, size, location, and crisis severity create complex patterns that tree-based models capture well.

2. **Feature Importance Analysis**: Random Forests provide interpretable feature importance scores, allowing us to identify which factors (business type, employee count, location) most strongly predict survival.

3. **Robust to Imbalanced Data**: Using `class_weight='balanced'`, the model adjusts for the fact that more businesses survive than fail, preventing bias toward the majority class.

4. **Handles Mixed Data Types**: Our features include categorical (business type, crisis period, location) and numerical (number of employees) variables—Random Forests handle this naturally without extensive preprocessing.

5. **Ensemble Method Reduces Overfitting**: By averaging 100 decision trees, the model is less likely to overfit to noise in the training data compared to a single decision tree.

**Model Configuration:**
```python
RandomForestClassifier(
    n_estimators=100,      # 100 trees for stable predictions
    max_depth=10,          # Limits tree depth to prevent overfitting
    class_weight='balanced', # Adjusts for imbalanced classes
    random_state=42        # Reproducibility
)
```

---

## 2. Target Variable Definition

### 2.1 Binary Classification: Survived vs. Failed

**Target Variable:** `survived` (0 = Failed, 1 = Survived)

**Definition Logic:**
- **Failed (0)**: Business issued license during crisis AND closed within 2 years
- **Survived (1)**: Business issued during crisis AND either:
  - Still active today, OR
  - Operated for 2+ years beyond crisis start

**Why 2 Years?**
- Economic research shows most crisis-related failures occur within 18-24 months
- Captures immediate crisis impact while filtering out unrelated closures
- Balances between being too lenient (3+ years) and too strict (<1 year)

**Limitations of This Definition:**
1. **Survivorship Bias**: Businesses still operating are assumed "survivors," but may fail later
2. **Pre-existing Issues**: Some failures may be due to factors unrelated to the crisis
3. **Right-Censored Data**: Recent businesses (2022-2024) haven't had full 2 years to prove survival

---

## 3. Feature Engineering

### 3.1 Features Used

| Feature | Type | Description | Rationale |
|---------|------|-------------|-----------|
| **businesstype** | Categorical | Primary industry classification | Core predictor—some industries inherently more vulnerable |
| **businesssubtype** | Categorical | Detailed business category | Captures nuance within industries |
| **numberofemployees** | Numerical | Employee count at license issuance | Proxy for business size—larger may have more resources |
| **crisis_period** | Categorical | Which crisis (2008, COVID, etc.) | Different crises affect industries differently |
| **localarea** | Categorical | Vancouver neighborhood | Geographic clustering of vulnerability |

### 3.2 Encoding Strategy

**Label Encoding** was used for categorical variables because:
- Random Forests handle ordinal relationships naturally
- More memory-efficient than one-hot encoding with many categories
- Tree splits can learn category groupings automatically

**Missing Data Handling:**
- Categorical: Filled with 'unknown' category
- Numerical (employees): Filled with median value

---

## 4. Model Performance Evaluation

### 4.1 Train-Test Split

- **Test Size**: 30% (stratified by survival outcome)
- **Stratification**: Ensures both train and test sets have same proportion of failures/survivors
- **Random State**: 42 (for reproducibility)

### 4.2 Expected Performance Metrics

**What to Look For:**

1. **Accuracy**: Proportion of correct predictions
   - **Good**: >75%
   - **Excellent**: >85%

2. **Precision (for "Failed" class)**: Of businesses predicted to fail, how many actually failed?
   - **Critical for stakeholders**: False positives waste resources on interventions
   - **Target**: >60%

3. **Recall (for "Failed" class)**: Of businesses that actually failed, how many did we predict?
   - **Critical for policy**: Missing vulnerable businesses leaves them without support
   - **Target**: >70%

4. **F1-Score**: Harmonic mean of precision and recall
   - **Balanced metric**: Useful when both false positives and false negatives matter

### 4.3 Potential Issues with Model Viability

**⚠️ Class Imbalance**
- Most businesses survive crises → model may be biased toward predicting "survived"
- **Mitigation**: `class_weight='balanced'` parameter
- **Check**: Compare precision/recall for both classes

**⚠️ Limited Training Data**
- Only 5 crises in dataset → limited examples of crisis conditions
- Businesses issued during crises are subset of total data
- **Impact**: Model may not generalize to unprecedented crisis types

**⚠️ Feature Correlation**
- `businesstype` and `businesssubtype` are highly correlated
- May lead to feature redundancy
- **Check**: Feature importance scores—if subtype dominates, type may be redundant

**⚠️ Temporal Bias**
- Economic conditions changed dramatically from 2000 to 2024
- A restaurant in 2000 vs 2020 faces different environments
- **Limitation**: Model assumes crisis impacts are stationary over time

---

## 5. Feature Importance Analysis

### 5.1 Interpreting Feature Importance

The model outputs importance scores (0 to 1) for each feature:
- **High Importance (>0.3)**: Primary driver of survival/failure
- **Moderate (0.1-0.3)**: Supporting factor
- **Low (<0.1)**: Minimal predictive power

**Expected Rankings:**
1. **businesstype / businesssubtype**: Likely most important—restaurants vs tech firms have vastly different crisis resilience
2. **crisis_period**: COVID-19 had unique impacts (lockdowns) vs Great Recession (credit freeze)
3. **numberofemployees**: Larger businesses may have more resources to weather downturns
4. **localarea**: Some neighborhoods (tourist areas, downtown) more vulnerable

### 5.2 Actionable Insights from Feature Importance

If **businesstype** dominates:
- **Interpretation**: Industry is destiny—policy should focus sector-specific support
- **Action**: Create targeted relief programs for vulnerable industries

If **crisis_period** is highly important:
- **Interpretation**: Not all crises are equal—pandemic ≠ recession
- **Action**: Predictive value may be limited if next crisis is novel

If **numberofemployees** is important:
- **Interpretation**: Size matters—small businesses disproportionately affected
- **Action**: Scale support based on business size

---

## 6. Business Type Vulnerability Analysis

### 6.1 Survival Rate Calculation

For each business type, we calculate:

**Actual Survival Rate** = (# survived) / (# total during crises)

**Predicted Survival Probability** = Model's average predicted probability for that type

### 6.2 Identifying High-Risk Industries

**Most Vulnerable Business Types** (Expected):
- **Hospitality**: Restaurants, bars, hotels (discretionary spending)
- **Tourism**: Travel agencies, tour operators (border closures, fear)
- **Retail**: Non-essential retail (e-commerce competition + crisis spending cuts)
- **Arts & Entertainment**: Theaters, event venues (gathering restrictions, discretionary spending)

**Most Resilient Business Types** (Expected):
- **Essential Services**: Grocery stores, pharmacies, healthcare
- **Professional Services**: Legal, accounting, consulting (B2B revenue streams)
- **Technology**: Software, IT services (remote work enablers)
- **Construction**: Infrastructure spending, housing demand

### 6.3 Validation Check

**Model is viable if:**
- Predicted survival rates **correlate strongly** with actual survival rates (R² > 0.6)
- Ordering of vulnerable → resilient matches economic intuition
- Differences between types are **statistically significant** (not due to small sample sizes)

**Red Flags:**
- Predicted and actual rates diverge widely → model isn't learning true patterns
- Counterintuitive results (e.g., restaurants more resilient than grocery stores)
- High variance within business types → definitions too broad

---

## 7. Model Limitations and Caveats

### 7.1 Data Quality Issues

1. **Sparse Historical Data**: 1997-2012 data has gaps, reducing training examples
2. **Inconsistent Date Formats**: Required complex parsing, may have introduced errors
3. **Missing Values**: ~13% of records lack year/date information
4. **Business Type Granularity**: Some categories too broad ("Miscellaneous Services")

### 7.2 Methodological Limitations

1. **Survival Definition**: 2-year threshold is arbitrary—sensitivity analysis needed
2. **Omitted Variables**: No data on:
   - Revenue/profitability
   - Debt levels
   - Owner experience
   - Market competition
3. **Selection Bias**: Only licensed businesses in dataset—excludes informal economy
4. **Ecological Fallacy**: Model predicts at business-type level, but individual businesses vary widely

### 7.3 Generalizability Concerns

1. **Vancouver-Specific**: Economic conditions differ across cities
2. **Historical Crises**: Past patterns may not predict future unprecedented events (e.g., AI disruption)
3. **Policy Changes**: Government support programs (CERB in COVID) alter outcomes
4. **Time Period**: 28-year span includes major structural economic shifts

---

## 8. Model Viability Assessment

### 8.1 When This Model IS Useful

✅ **Strategic Planning**: Identify high-risk sectors for early intervention
✅ **Resource Allocation**: Target relief funds to vulnerable business types
✅ **Comparative Analysis**: Benchmark current crisis against historical patterns
✅ **Scenario Planning**: Estimate impact of hypothetical recession scenarios

### 8.2 When This Model IS NOT Useful

❌ **Individual Business Predictions**: Too much variance within business types
❌ **Unprecedented Crises**: If next crisis is unlike past 5 (e.g., cyberattack), model fails
❌ **Short-Term Forecasting**: Predicts survival, not month-by-month license trends
❌ **Causal Inference**: Model identifies associations, not causation

---

## 9. Recommendations for Improvement

### 9.1 Data Enhancements

1. **External Economic Indicators**: Add unemployment rate, GDP growth, interest rates as features
2. **Business Age**: Calculate years in operation before crisis hit
3. **Ownership Type**: Sole proprietor vs corporation vs franchise
4. **Revenue Data**: If available from tax records (privacy-protected)

### 9.2 Modeling Enhancements

1. **Survival Analysis**: Use Cox Proportional Hazards model to estimate time-to-failure (not just binary outcome)
2. **Crisis-Specific Models**: Train separate models for pandemic vs recession vs oil shock
3. **Ensemble Approach**: Combine Random Forest with Gradient Boosting and Logistic Regression
4. **Cross-Validation**: Use time-series CV (train on early crises, test on later ones)

### 9.3 Validation Strategies

1. **Out-of-Time Testing**: Train on 2000-2019, test on COVID-19 period only
2. **Sensitivity Analysis**: Vary survival threshold (1 year, 2 years, 3 years) and compare results
3. **Subgroup Analysis**: Separate models for small (<10 employees) vs large businesses
4. **Calibration Check**: Do predicted probabilities match observed frequencies?

---

## 10. Interpretation Guide for Stakeholders

### 10.1 For Policymakers

**Key Takeaway**: This model identifies which sectors are **systematically vulnerable** across multiple crisis types.

**Use Case**: Design sector-specific relief programs based on vulnerability scores. For example:
- High-risk sectors (survival rate <50%): Emergency grants, rent relief
- Moderate-risk (50-70%): Low-interest loans, training programs
- Low-risk (>70%): Standard support only

**Caution**: Model predictions are **probabilistic**, not deterministic. A 40% survival rate means 4 in 10 businesses of that type survive—not that all fail.

### 10.2 For Business Owners

**Key Takeaway**: Your industry matters more than individual effort during crises.

**Use Case**: If you're in a high-risk category:
1. Build larger cash reserves (6-12 months expenses)
2. Diversify revenue streams
3. Develop crisis contingency plans early

**Caution**: Being in a "vulnerable" category doesn't guarantee failure—many individual businesses thrive despite sector-wide struggles.

### 10.3 For Researchers

**Key Takeaway**: This is a **descriptive/predictive** model, not a **causal** model.

**Use Case**: Starting point for deeper investigation:
- Why are certain sectors vulnerable? (supply chain, consumer behavior, capital intensity)
- How do policy interventions moderate vulnerability?
- What business strategies correlate with survival within high-risk sectors?

**Caution**: Correlation ≠ causation. Feature importance shows associations, not mechanisms.

---

## 11. Conclusion

### 11.1 Model Viability Summary

**Strengths:**
- ✅ Leverages 28 years of real-world crisis data
- ✅ Captures non-linear relationships between features
- ✅ Provides interpretable business-type vulnerability rankings
- ✅ Balances precision and recall for practical use

**Weaknesses:**
- ⚠️ Limited to 5 historical crises (small sample of crisis types)
- ⚠️ Assumes past patterns predict future (may not hold for unprecedented events)
- ⚠️ Omits key variables (revenue, debt, owner characteristics)
- ⚠️ Vulnerable to class imbalance and temporal bias

### 11.2 Overall Verdict

**This model is MODERATELY VIABLE for strategic planning purposes**, with important caveats:

1. **Best Used For**: High-level sector prioritization, resource allocation, scenario analysis
2. **Should NOT Be Used For**: Individual business decisions, precise failure predictions, causal claims
3. **Improvement Needed**: Add economic indicators, try survival analysis, validate on out-of-time test set

The model provides valuable **directional insights** into which business types face elevated risk during economic downturns, but predictions should be combined with domain expertise and real-time economic monitoring.

---

## 12. Future Work

1. **Incorporate Macroeconomic Data**: Unemployment, GDP, consumer confidence indices
2. **Survival Analysis**: Cox regression to model time-to-failure hazard rates
3. **Spatial Analysis**: Geographic clustering of vulnerable businesses (heat maps)
4. **Deep Learning**: LSTM networks to capture temporal dynamics of crisis progression
5. **Causal Inference**: Difference-in-differences analysis of policy interventions (e.g., CERB impact)

---

## Appendix: Code Quality and Reproducibility

**Strengths:**
- Clear variable naming and comments
- Modular structure (feature engineering → training → evaluation)
- Saves outputs (CSVs, visualizations) for external review

**Areas for Improvement:**
- Add logging for debugging
- Implement cross-validation for more robust performance estimates
- Version control for model artifacts (pickle files)
- Unit tests for data processing functions

**Reproducibility:** ✅ High—fixed random seed (42), clear dependencies, documented workflow