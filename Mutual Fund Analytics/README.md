# Mutual Fund Analytics Platform

## Project Overview

The **Mutual Fund Analytics Platform** is a data analytics project
developed as part of my Data Analyst Internship at **Bluestock Fintech
Pvt. Ltd.** The project focuses on building an end-to-end data workflow
to collect, clean, store, explore, and analyze mutual fund data using
Python, SQL, and data visualization libraries.

The platform transforms raw financial datasets into structured,
analysis-ready information and evaluates mutual fund performance through
historical Net Asset Value (NAV) trends, returns, risk metrics, and
benchmark comparisons.

## Objectives

-   Build a Python-based ETL pipeline for mutual fund data ingestion.
-   Clean, validate, and standardize financial datasets.
-   Design a relational SQLite database for structured data storage.
-   Perform exploratory data analysis to identify financial trends and
    patterns.
-   Calculate mutual fund returns and risk-adjusted performance metrics.
-   Compare fund performance against benchmark indices.
-   Develop a data-driven fund scorecard to support comparative
    analysis.

## Technology Stack

  Technology         Purpose
  ------------------ ------------------------------------------------
  Python             Data processing and analytics
  Pandas             Data cleaning, transformation, and aggregation
  NumPy              Numerical computations and financial metrics
  SQL                Database querying and financial analysis
  SQLite             Relational database management
  SQLAlchemy         Database connectivity and data loading
  Matplotlib         Data visualization
  Seaborn            Statistical charts and heatmaps
  Plotly             Interactive visualizations
  Jupyter Notebook   Exploratory analysis and documentation
  Requests           API integration and data retrieval
  Git and GitHub     Version control and project management

## Data Sources

The project uses publicly available mutual fund and financial market
data from the following sources:

-   **AMFI India:** Mutual fund NAV and industry-level financial
    information.
-   **mfapi.in:** Historical mutual fund NAV data through a REST API.
-   **NSE India:** Benchmark index data.
-   **BSE India:** Market index information.
-   **AMFI Monthly Reports:** SIP inflows and industry trends.
-   **Provided CSV datasets:** Fund master records, NAV history, AUM,
    investor transactions, portfolio holdings, and performance metrics.

The datasets combine publicly sourced financial information with
synthetic investor transaction records for analytical purposes.

## Data Ingestion and ETL Pipeline

Developed a Python-based data ingestion workflow to prepare raw
financial data for downstream analysis.

-   Created a structured project environment for datasets, scripts,
    notebooks, SQL files, and reports.
-   Loaded multiple CSV datasets using Pandas.
-   Retrieved historical NAV data from the mfapi.in API.
-   Parsed API responses and stored retrieved data in CSV format.
-   Inspected dataset dimensions, column types, and sample records.
-   Examined fund houses, categories, subcategories, and risk
    classifications.
-   Validated AMFI scheme codes against the fund master and NAV history
    datasets.

This workflow establishes a consistent process for collecting and
preparing mutual fund data.

## Data Cleaning and SQL Database Design

Implemented data preparation and database management processes to
improve data quality and enable efficient querying.

### Data Cleaning and Validation

-   Converted date fields into consistent datetime formats.
-   Sorted NAV records by scheme code and date.
-   Identified and removed duplicate records.
-   Checked for missing NAV values and handled gaps according to the
    data-cleaning rules.
-   Validated that NAV values were positive.
-   Standardized transaction types, including SIP, Lumpsum, and
    Redemption.
-   Validated transaction amounts, KYC status values, and date formats.
-   Checked financial performance fields for valid numeric values.
-   Examined expense ratios and flagged potentially invalid or negative
    performance metrics.

### SQL Database Design

Designed a relational SQLite database to organize mutual fund data into
related tables.

The database structure includes entities and fact tables for:

-   Fund master information
-   Historical NAV records
-   Investor transactions
-   Fund performance metrics

Implemented primary and foreign key relationships where appropriate to
maintain data integrity and support consistent joins.

### SQL Analysis

Developed SQL queries to support financial and business analysis,
including:

-   Identifying funds with the highest assets under management.
-   Calculating monthly average NAV.
-   Analyzing year-over-year SIP inflow growth.
-   Examining investor transactions by state.
-   Filtering funds based on expense ratios.
-   Supporting additional aggregations and comparisons through
    structured queries.

Created a data dictionary to document dataset columns, data types, and
sources.

## Exploratory Data Analysis

Performed exploratory data analysis using Python to understand
historical NAV movements, mutual fund industry growth, investor
activity, and financial performance patterns.

### NAV and Fund House Analysis

-   Analyzed historical NAV trends across mutual fund schemes.
-   Examined AUM growth across asset management companies.
-   Compared financial performance across funds and fund categories.
-   Identified trends, fluctuations, and potential anomalies in
    financial datasets.

### SIP and Industry Trends

-   Analyzed monthly SIP inflows over time.
-   Examined category-wise mutual fund inflows.
-   Investigated mutual fund folio growth.
-   Compared industry-level indicators across reporting periods.

### Investor and Portfolio Analysis

-   Explored investor age-group distributions.
-   Analyzed SIP amounts across demographic groups.
-   Examined geographic differences in investor transactions.
-   Investigated sector-wise portfolio holdings and allocation patterns.

### Statistical Analysis and Visualization

Created visualizations to communicate financial trends and
relationships, including:

-   Time-series line charts
-   Bar charts for AUM comparisons
-   Category-wise heatmaps
-   Investor demographic charts
-   Geographic distribution charts
-   Correlation matrices for fund returns
-   Portfolio sector allocation charts

Documented key observations in Jupyter Notebook to make analytical
findings easier to interpret and reproduce.

## Fund Performance Analytics

Developed analytical calculations to evaluate mutual fund performance
using historical NAV data and benchmark indices.

### Return Calculations

-   Calculated daily returns from consecutive NAV observations.
-   Computed compound annual growth rate (CAGR) for available one-year,
    three-year, and five-year periods.
-   Compared returns across selected mutual fund schemes.
-   Prepared structured outputs for performance reporting.

### Risk-Adjusted Performance Metrics

  -----------------------------------------------------------------------
  Metric                              Purpose
  ----------------------------------- -----------------------------------
  Sharpe Ratio                        Evaluates returns relative to total
                                      volatility and a risk-free rate
                                      proxy.

  Sortino Ratio                       Evaluates returns relative to
                                      downside volatility.

  Alpha                               Measures performance relative to a
                                      benchmark using the specified
                                      model.

  Beta                                Measures sensitivity to benchmark
                                      movements.

  Standard Deviation                  Measures variability in returns.

  Maximum Drawdown                    Measures the largest peak-to-trough
                                      decline.

  CAGR                                Measures annualized compound growth
                                      over a specified period.
  -----------------------------------------------------------------------

### Fund Scorecard and Benchmark Comparison

-   Developed a composite fund scoring methodology using return, risk,
    alpha, expense ratio, and drawdown rankings.
-   Assigned weighted scores to support consistent comparisons between
    funds.
-   Compared selected funds against benchmark indices such as Nifty 50
    and Nifty 100.
-   Prepared benchmark comparison visualizations.
-   Calculated tracking error to examine differences between fund and
    benchmark returns.
-   Organized results into CSV reports for further analysis.

## Project Workflow

1.  **Data Collection:** Load source datasets and retrieve historical
    NAV information.
2.  **Data Processing:** Clean, standardize, and validate the collected
    data.
3.  **Data Storage:** Organize processed records in a relational SQLite
    database.
4.  **Exploratory Analysis:** Investigate trends, distributions,
    correlations, and anomalies.
5.  **Performance Evaluation:** Calculate returns, risk metrics, and
    benchmark comparisons.
6.  **Analytical Reporting:** Generate visualizations, scorecards, and
    structured outputs.

## Key Skills Demonstrated
-   Data ingestion and ETL pipeline development
-   Data cleaning and preprocessing
-   SQL database design and querying
-   Relational data management
-   Exploratory data analysis
-   Statistical analysis and data visualization
-   Financial return and risk calculations
-   Benchmark analysis and comparative scoring
-   Python scripting and Jupyter Notebook development
-   Analytical reporting and documentation

## Conclusion
This project strengthened my practical understanding of the data
analytics workflow, from raw data ingestion and database design to
exploratory analysis and financial performance evaluation. It provided
hands-on experience in transforming financial datasets into structured
information, applying analytical methods, and communicating findings
through visualizations and reports.