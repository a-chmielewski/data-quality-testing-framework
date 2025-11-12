# Data Quality Testing Framework

> A production-ready data quality pipeline demonstrating modern data engineering practices with automated validation, transformation, and monitoring.

[![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://www.python.org/)
[![dbt](https://img.shields.io/badge/dbt-1.8+-orange.svg)](https://www.getdbt.com/)
[![Great Expectations](https://img.shields.io/badge/Great%20Expectations-0.18-red.svg)](https://greatexpectations.io/)
[![DuckDB](https://img.shields.io/badge/DuckDB-1.1+-yellow.svg)](https://duckdb.org/)

## Overview

This project showcases a complete data quality testing framework built around NYC's 311 Service Request data. It demonstrates end-to-end data engineering capabilities including API ingestion, schema validation, data transformation, quality testing, and metrics visualization. The pipeline implements best practices for data reliability using Great Expectations while maintaining simplicity through DuckDB's embedded architecture.

**What it does:**
- Fetches recent and historical 311 complaint data from NYC Open Data API
- Validates data quality at ingestion using Pandera schemas
- Transforms raw data into analytics-ready models with dbt
- Runs comprehensive quality checks via Great Expectations
- Generates automated data quality reports and custom metrics dashboards

## Architecture

```
┌─────────────────────────────────────────────────────────────────────────┐
│                          Data Quality Pipeline                          │
└─────────────────────────────────────────────────────────────────────────┘

    NYC 311 API                 Python ETL                DuckDB
   ┌───────────┐              ┌──────────┐            ┌──────────┐
   │  Open     │   HTTP GET   │ fetch_   │   INSERT   │  raw.    │
   │  Data     │─────────────>│ 311.py   │───────────>│  nyc311_ │
   │  Portal   │   JSON       │          │   Tables   │  {hist,  │
   │           │              │ Pandera  │            │  recent} │
   └───────────┘              │ Schema   │            └──────────┘
                              └──────────┘                  │
                                                            │
                                                            v
    ┌──────────────────────────────────────────────────────┴──────┐
    │                                                              │
    │                    dbt Transformations                       │
    │                                                              │
    │  ┌────────────────┐           ┌───────────────────────┐    │
    │  │  stg_311.sql   │           │ fct_311_complaints.sql│    │
    │  │  - Casting     │───────────>│  - Business logic     │    │
    │  │  - Dedup       │           │  - Computed fields    │    │
    │  │  - Cleansing   │           │  - Analytics-ready    │    │
    │  └────────────────┘           └───────────────────────┘    │
    │                                                              │
    └──────────────────────────────────────────────────────────────┘
                                    │
                                    v
    ┌──────────────────────────────────────────────────────────────┐
    │              Great Expectations Validation                   │
    │                                                              │
    │  ┌─────────────────────┐     ┌─────────────────────┐       │
    │  │ suite_311_recent    │     │ suite_311_hist      │       │
    │  │ - Uniqueness        │     │ - Uniqueness        │       │
    │  │ - Null checks       │     │ - Null checks       │       │
    │  │ - Row counts        │     │ - Row counts        │       │
    │  │ - Borough values    │     │ - Borough values    │       │
    │  └─────────────────────┘     └─────────────────────┘       │
    │                                                              │
    │  checkpoint_311 ──> Store Results ──> Update Data Docs      │
    └──────────────────────────────────────────────────────────────┘
                                    │
                ┌───────────────────┴───────────────────┐
                v                                       v
    ┌──────────────────────┐              ┌──────────────────────┐
    │  GX Data Docs        │              │  Custom Dashboard    │
    │  (Auto-generated)    │              │  (Plotly + Metrics)  │
    │                      │              │                      │
    │  - Test results      │              │  - KPIs              │
    │  - Expectations      │              │  - Trend charts      │
    │  - Profiling         │              │  - Null analysis     │
    └──────────────────────┘              └──────────────────────┘
```

## Key Features

### Multi-Layer Data Validation
- **Schema validation** at ingestion using Pandera for early error detection
- **Quality assertions** via Great Expectations with detailed reporting
- **Transformation tests** through dbt models ensuring data integrity

### Embedded Analytics Database
Leveraged **DuckDB** for its unique combination of SQL analytics power and zero-configuration deployment—ideal for local development and portable demos without infrastructure overhead.

### Automated Pipeline Orchestration
Simple yet effective **Makefile** automation enables one-command execution of the entire pipeline, from data fetch to dashboard generation.

### Temporal Data Comparison
Ingests both recent (last 7 days) and historical (same period in 2019) data to demonstrate drift detection and temporal analysis capabilities.

### Production-Ready Quality Checks
- Uniqueness constraints on primary keys
- NOT NULL assertions on critical fields
- Row count boundaries (50-5000 rows)
- Enumerated value validation (NYC boroughs)
- Custom expectations for domain-specific rules

## Tech Stack

| Component | Technology | Purpose |
|-----------|-----------|---------|
| **Data Source** | NYC Open Data API | Real-world public dataset (311 service requests) |
| **Ingestion** | Python + Requests | API client with retry logic and error handling |
| **Schema Validation** | Pandera 0.20 | Type checking and constraint validation at ingestion |
| **Storage** | DuckDB 1.1 | Embedded OLAP database with full SQL support |
| **Transformation** | dbt-core 1.8 + dbt-duckdb | Modular SQL transformations with lineage |
| **Quality Testing** | Great Expectations 0.18 | Declarative data quality assertions |
| **Visualization** | Plotly 5.24 | Interactive dashboard with custom metrics |
| **Orchestration** | GNU Make | Simple, reproducible pipeline automation |

## Pipeline Workflow

The pipeline executes in five distinct stages:

### 1. Data Ingestion (`make fetch`)
Runs [`scripts/fetch_311.py`](scripts/fetch_311.py) to:
- Query NYC Open Data API with date-range filters
- Fetch last 7 days of recent data (up to 3000 rows)
- Fetch equivalent historical period from 2019
- Validate schemas using Pandera
- Export to CSV files in `data/`
- Load into DuckDB `raw` schema

### 2. dbt Transformations (`make dbt`)
Executes dbt models in [`dbt/models/`](dbt/models/):

**Staging Layer** ([`stg_311.sql`](dbt/models/staging/stg_311.sql)):
- Type casting (timestamps, doubles)
- Deduplication by `unique_key`
- Null-safe transformations

**Mart Layer** ([`fct_311_complaints.sql`](dbt/models/marts/fct_311_complaints.sql)):
- Business logic (e.g., `is_open` flag)
- Aggregation-ready fact table

### 3. GX Setup (`make gx`)
Runs [`scripts/setup_gx.py`](scripts/setup_gx.py) to:
- Initialize Great Expectations context
- Configure Pandas datasource for runtime batches
- Create expectation suites for recent and historical data
- Define checkpoint for validation orchestration

### 4. Quality Validation (`make checkpoint`)
Executes [`scripts/run_checkpoint.py`](scripts/run_checkpoint.py):
- Loads both datasets into GX validators
- Runs all expectations from both suites
- Generates validation results and stores them
- Updates Data Docs HTML reports
- Exits with failure if validations don't pass

### 5. Metrics Generation (`make metrics`)
Runs [`scripts/build_metrics.py`](scripts/build_metrics.py) to compute:
- Row counts per dataset
- Null ratios for key columns
- Top complaint types with share percentages
- Exports to `artifacts/metrics.json` for dashboard consumption

### Run Everything
```bash
make all  # Executes: fetch → dbt → checkpoint → metrics
```

## Project Structure

```
data-quality-testing-framework/
├── data/                          # Raw data exports (CSV)
│   ├── 311_hist.csv              # Historical complaint data
│   └── 311_recent.csv            # Recent complaint data
│
├── duckdb/                        # DuckDB database files
│   └── nyc.duckdb                # Embedded analytics database
│
├── dbt/                           # dbt project
│   ├── models/
│   │   ├── staging/
│   │   │   └── stg_311.sql       # Staging transformations
│   │   └── marts/
│   │       └── fct_311_complaints.sql  # Analytics fact table
│   ├── dbt_project.yml           # dbt configuration
│   └── profiles.yml              # DuckDB connection profile
│
├── gx/                            # Great Expectations
│   ├── expectations/
│   │   ├── suite_311_hist.json   # Historical data expectations
│   │   └── suite_311_recent.json # Recent data expectations
│   ├── checkpoints/
│   │   └── checkpoint_311.yml    # Validation checkpoint
│   ├── great_expectations.yml    # GX project config
│   └── uncommitted/
│       └── data_docs/            # Auto-generated HTML reports
│
├── docs/
│   └── dashboard.html            # Custom Plotly metrics dashboard
│
├── schemas/
│   └── nyc311.py                 # Pandera schema definitions
│
├── scripts/
│   ├── fetch_311.py              # API ingestion script
│   ├── setup_gx.py               # GX initialization
│   ├── run_checkpoint.py         # Validation execution
│   └── build_metrics.py          # Metrics computation
│
├── artifacts/
│   └── metrics.json              # Dashboard metrics output
│
├── Makefile                       # Pipeline automation
├── requirements.txt              # Python dependencies
└── README.md                     # This file
```

## Quick Start

### Prerequisites
- Python 3.11+
- pip
- make (optional but recommended)

### Installation

```bash
# Clone the repository
git clone https://github.com/a-chmielewski/data-quality-testing-framework.git
cd data-quality-testing-framework

# Install dependencies
make init
# or: pip install -r requirements.txt
```

### Running the Pipeline

**Option 1: Full pipeline**
```bash
make all
```

**Option 2: Step-by-step**
```bash
make fetch       # Fetch data from NYC API
make dbt         # Run dbt transformations
make gx          # Initialize Great Expectations (first run only)
make checkpoint  # Run quality validations
make metrics     # Generate dashboard metrics
```

### Viewing Results

**Great Expectations Data Docs:**
```bash
# Open in browser
open gx/uncommitted/data_docs/local_site/index.html
```

**Custom Metrics Dashboard:**
```bash
# Open in browser
open docs/dashboard.html
```

## Data Quality Checks

The framework implements comprehensive quality checks through Great Expectations:

### Expectation Suites

Both [`suite_311_recent`](gx/expectations/suite_311_recent.json) and [`suite_311_hist`](gx/expectations/suite_311_hist.json) enforce:

| Expectation | Purpose | Details |
|------------|---------|---------|
| `expect_table_columns_to_match_set` | Schema validation | Ensures all required columns exist |
| `expect_column_values_to_be_unique` | Primary key constraint | `unique_key` must be unique |
| `expect_column_values_to_not_be_null` | NOT NULL checks | `created_date` and `complaint_type` required |
| `expect_table_row_count_to_be_between` | Volume check | 50 ≤ rows ≤ 5000 |
| `expect_column_values_to_be_in_set` | Enum validation | `borough` must be valid NYC borough (90% threshold) |

### Validation Results

Results are stored in `gx/uncommitted/validations/` with:
- Detailed pass/fail status for each expectation
- Statistics on unexpected values
- Metadata for tracking validation history

Failed validations trigger pipeline failure (exit code 1) to support CI/CD integration.

## Dashboard

The custom dashboard ([`docs/dashboard.html`](docs/dashboard.html)) provides at-a-glance data quality insights:

### Features
- **Row count KPIs**: Recent vs. historical data volumes
- **Complaint type distribution**: Interactive Plotly chart comparing top complaint categories
- **Null rate analysis**: Table showing missing data percentages by column
- **Responsive design**: Dark mode UI optimized for modern browsers

### Architecture
- Self-contained single HTML file (no build step)
- Fetches `artifacts/metrics.json` dynamically
- Client-side rendering with Plotly.js
- Ready for deployment to GitHub Pages or static hosting

## Development Notes

### Design Decisions

**Why DuckDB?**
Chose DuckDB over traditional client-server databases (PostgreSQL, MySQL) for its embedded nature, zero configuration, and exceptional performance on analytical queries. Perfect for local development and portable demos.

**Why Great Expectations Classic?**
Opted for the OSS version (0.18) over GX Cloud to maintain full local control, demonstrate configuration skills, and ensure reproducibility without external dependencies.

**Why Makefile over Airflow/Prefect?**
For this demonstration project, a Makefile provides transparent, reproducible automation without orchestration overhead. Shows understanding of appropriate tool selection for project scale.

**Temporal Comparison Strategy**
Comparing recent data with the same calendar period in 2019 enables demonstration of:
- Data drift detection
- Seasonal pattern analysis
- Historical baseline establishment

### Schema Evolution Strategy
The pipeline handles schema changes gracefully:
- Pandera validates incoming API data
- dbt uses `try_cast()` for type safety
- GX expectations allow schema flexibility with `exact_match: false`

### Error Handling
- API failures surface immediately in fetch script
- Pandera validation errors log but don't block (for demo purposes)
- GX validation failures exit with code 1 (CI-ready)
- DuckDB connection errors handled with informative messages

## Future Enhancements

Potential extensions to demonstrate additional data engineering capabilities:

### Infrastructure
- [ ] Dockerize the pipeline with multi-stage builds
- [ ] Add GitHub Actions CI/CD workflow
- [ ] Deploy dashboard to GitHub Pages automatically
- [ ] Implement data versioning with DVC

### Data Quality
- [ ] Add custom Great Expectations expectations
- [ ] Implement anomaly detection on complaint volumes
- [ ] Build data quality SLA monitoring
- [ ] Create data lineage visualization

### Analytics
- [ ] Geospatial analysis using latitude/longitude
- [ ] Time-series forecasting of complaint patterns
- [ ] Agency response time analysis
- [ ] Borough-level comparison dashboard

### Engineering
- [ ] Migrate orchestration to Airflow/Prefect
- [ ] Add incremental dbt models
- [ ] Implement CDC (Change Data Capture) patterns
- [ ] Add unit tests for transformation logic

## Resources

- **NYC 311 Data**: [NYC Open Data Portal](https://data.cityofnewyork.us/Social-Services/311-Service-Requests-from-2010-to-Present/erm2-nwe9)
- **Great Expectations Docs**: [docs.greatexpectations.io](https://docs.greatexpectations.io/)
- **dbt Documentation**: [docs.getdbt.com](https://docs.getdbt.com/)
- **DuckDB Reference**: [duckdb.org/docs](https://duckdb.org/docs/)

## License

This project is provided as-is for portfolio and educational purposes.

---

**Author**: [a-chmielewski](https://github.com/a-chmielewski)

**Project Type**: Data Engineering Portfolio Demonstration

*Built to showcase modern data quality engineering practices, tool integration capabilities, and production-ready pipeline development.*

