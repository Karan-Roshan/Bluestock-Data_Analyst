# Nifty 100 Financial Intelligence Platform

## Overview

The **Nifty 100 Financial Intelligence Platform** is a financial data
analytics project designed to transform company financial statements
into structured, comparable insights. It brings together company
profiles, profit and loss statements, balance sheets, cash flow
statements, sector mappings, valuation data, and calculated financial
ratios in a unified analytical workflow.

The platform is designed to help analysts explore company fundamentals,
compare businesses with sector peers, screen companies using financial
criteria, and review key financial indicators through reports and an
interactive dashboard.

## Objectives

-   Build a repeatable ETL pipeline for financial datasets.
-   Clean, normalize, validate, and store financial data in a relational
    database.
-   Calculate financial ratios and key performance indicators (KPIs).
-   Analyze profitability, leverage, liquidity, growth, valuation, and
    cash flow.
-   Compare companies across sectors and defined peer groups.
-   Support company screening using configurable financial criteria.
-   Present findings through analytical outputs, reports, and a
    dashboard.

## Project Scope

The project specification covers a universe of **92 Nifty 100
companies** after applying data-availability filters. It describes **7
core datasets and 5 supplementary datasets**, more than **50 financial
KPIs**, and multiple analytics modules.

The intended platform includes data engineering, financial ratio
calculations, company profiles, investment screening, financial health
scoring, sector analytics, cash-flow analysis, trend analysis, peer
comparisons, reporting, document references, and alerts/watchlists.
Features should be described as completed only where they are
implemented in the repository.

## Technology Stack

  Technology       Purpose
  ---------------- ---------------------------------------------------------
  Python           ETL, data processing, and analytics
  Pandas           Data loading, cleaning, transformation, and aggregation
  NumPy            Numerical computations
  SQLite           Relational data storage
  SQL              Data querying and joins
  openpyxl         Reading Excel workbooks
  SciPy            Statistical calculations
  scikit-learn     Scaling, clustering, and analytical workflows
  Matplotlib       Static visualizations
  Plotly           Interactive charts
  Streamlit        Interactive analytical dashboard
  FastAPI          Optional REST API layer described in the specification
  Uvicorn          Running the FastAPI application
  ReportLab        PDF report generation
  pytest           Automated testing
  Git and GitHub   Version control

## Data Sources and Datasets

The specification describes the following core datasets:

  -----------------------------------------------------------------------
  Dataset                             Purpose
  ----------------------------------- -----------------------------------
  `companies.xlsx`                    Company master information and
                                      identifiers

  `profitandloss.xlsx`                Annual revenue, expenses, operating
                                      profit, net profit, and EPS

  `balancesheet.xlsx`                 Equity, borrowings, assets, and
                                      liabilities

  `cashflow.xlsx`                     Operating, investing, and financing
                                      cash flows

  `analysis.xlsx`                     Pre-computed growth and financial
                                      analysis text

  `documents.xlsx`                    Annual report links

  `prosandcons.xlsx`                  Qualitative company observations
  -----------------------------------------------------------------------

Supplementary datasets described in the project specification include:

-   `sectors.xlsx` --- sector and subsector mappings.
-   `stock_prices.xlsx` --- monthly price history.
-   `market_cap.xlsx` --- valuation multiples and market capitalization.
-   `financial_ratios.xlsx` --- financial KPI records.
-   `peer_groups.xlsx` --- company peer-group mappings.

The document identifies public financial sources such as Screener.in,
BSE filings, and annual-report links. Some supplementary market-price
and valuation records are described as simulated. Review source and
provenance notes before interpreting any result as actual market data.

## Data Engineering and ETL

The ETL workflow is intended to:

-   Load Excel datasets with the correct header rows.
-   Normalize company tickers and year labels.
-   Validate required columns, data types, and key fields.
-   Detect duplicate company-year records.
-   Check relationships between company master records and financial
    tables.
-   Load normalized datasets into a SQLite database.
-   Record loading statistics and data-quality issues for review.

The project specification describes a database named `nifty100.db` and a
10-table storage layer covering company profiles, financial statements,
supporting datasets, and analytical inputs.

## Financial Ratio Engine

The platform specification includes calculations for more than 50
financial KPIs across available company-year records.

Representative metrics include:

  -----------------------------------------------------------------------
  Category                            Example Metrics
  ----------------------------------- -----------------------------------
  Profitability                       Operating profit margin, net profit
                                      margin, ROE, ROCE, ROA

  Leverage                            Debt-to-equity, total debt,
                                      interest coverage

  Efficiency                          Asset turnover

  Growth                              Revenue CAGR, profit CAGR, EPS
                                      growth

  Cash Flow                           Free cash flow, cash from
                                      operations, CapEx

  Valuation                           P/E, P/B, EV/EBITDA, dividend
                                      yield, FCF yield
  -----------------------------------------------------------------------

Calculations should handle missing values, division by zero, negative
equity, debt-free companies, and differences in financial-statement
coverage. Monetary amounts are generally expressed in Indian Rupees
crore unless stated otherwise.

## Investment Screening and Financial Analysis

The specified analytical capabilities include:

-   Filtering companies by financial ratios and valuation metrics.
-   Ranking companies using selected criteria.
-   Generating a composite Financial Health Score on a 0--100 scale.
-   Comparing companies with sector benchmarks.
-   Calculating peer-group percentile rankings.
-   Analyzing historical revenue, profit, EPS, and cash-flow trends.
-   Identifying capital-allocation patterns and potential cash-flow
    concerns.
-   Examining valuation multiples relative to historical and sector
    benchmarks.

These outputs are analytical aids, not guarantees of future performance
or investment recommendations.

## Dashboard and Reporting

The project specification describes an analyst-facing Streamlit
dashboard with screens for:

-   Home and market overview
-   Company profile
-   Financial screener
-   Peer comparison
-   Trend analysis
-   Sector analysis
-   Capital allocation
-   Annual reports

It also describes company tearsheets, portfolio summaries, sector
reports, screener exports, and Excel outputs. A FastAPI service layer is
specified as an optional way to expose company, financial statement,
ratio, sector, peer, and screener data.

Only list dashboards, APIs, and reports as available deliverables after
confirming that the corresponding files and functionality exist in your
project repository.

## Architecture

The intended data flow is:

``` text
Source Excel / Supporting Data
              |
              v
      Data Ingestion
              |
              v
  Cleaning and Normalization
              |
              v
    Data Quality Validation
              |
              v
        SQLite Database
              |
              v
 Financial KPI and Analytics
              |
       +------+------+
       |             |
       v             v
   Dashboard     Reports/Exports
```

## Setup

### Prerequisites

-   Python 3.10 or later, compatible with the dependencies used by the
    project
-   pip
-   Git

### 1. Clone the repository

``` bash
git clone <your-github-repository-url>
cd <repository-folder>
```

### 2. Create a virtual environment

``` bash
python3 -m venv .venv
source .venv/bin/activate
```

On Windows, activate it with:

``` powershell
.venv\Scripts\activate
```

### 3. Install dependencies

If the repository contains a `requirements.txt` file:

``` bash
python -m pip install --upgrade pip
pip install -r requirements.txt
```

### 4. Prepare the datasets

Place the source workbooks in the configured raw-data directory. Confirm
that paths and expected column names match the project configuration
before running the pipeline.

### 5. Run the project

Run the ETL, analytics, tests, dashboard, or API using the entry points
present in your repository. Example commands below are templates;
replace the paths with the actual scripts in your project.

``` bash
python -m pytest
```

If a Streamlit application is implemented:

``` bash
streamlit run app.py
```

If a FastAPI application is implemented and exposes `app` from
`main.py`:

``` bash
uvicorn main:app --reload
```

## Data Quality and Testing

The specification calls for checks covering schema validity, missing or
invalid values, duplicate records, financial formula consistency, and
relationships between company and financial records. Automated tests
should validate ETL behavior, ratio calculations, edge cases, and
analytical outputs.

Run the available test suite from the project root:

``` bash
python -m pytest
```

Report test counts and coverage only from the actual results produced by
your current codebase.

## Key Skills Demonstrated

-   Python-based data engineering and ETL
-   Data cleaning, normalization, and validation
-   SQL and relational database design
-   Financial statement analysis
-   Financial KPI and ratio calculations
-   Exploratory and comparative data analysis
-   Sector and peer benchmarking
-   Data visualization and dashboard design
-   Automated testing and documentation
-   Financial reporting and data interpretation