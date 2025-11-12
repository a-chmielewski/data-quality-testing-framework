from pathlib import Path
import pandas as pd
from great_expectations.data_context import FileDataContext
from great_expectations.core.batch import RuntimeBatchRequest

gx_dir = Path("gx")
ctx = FileDataContext(context_root_dir=str(gx_dir))

# Load data from CSV files (fallback if DuckDB is locked)
df_recent = pd.read_csv("data/311_recent.csv")
df_hist = pd.read_csv("data/311_hist.csv")

# Validate recent data
print("Validating recent data...")
batch_request_recent = RuntimeBatchRequest(
    datasource_name="nyc311_pandas",
    data_connector_name="default_runtime_data_connector",
    data_asset_name="nyc311_recent",
    runtime_parameters={"batch_data": df_recent},
    batch_identifiers={"default_identifier_name": "recent"},
)

validator_recent = ctx.get_validator(
    batch_request=batch_request_recent,
    expectation_suite_name="suite_311_recent"
)
results_recent = validator_recent.validate()

# Validate historical data
print("Validating historical data...")
batch_request_hist = RuntimeBatchRequest(
    datasource_name="nyc311_pandas",
    data_connector_name="default_runtime_data_connector",
    data_asset_name="nyc311_hist",
    runtime_parameters={"batch_data": df_hist},
    batch_identifiers={"default_identifier_name": "hist"},
)

validator_hist = ctx.get_validator(
    batch_request=batch_request_hist,
    expectation_suite_name="suite_311_hist"
)
results_hist = validator_hist.validate()

# Build data docs
print("\nBuilding data docs...")
ctx.build_data_docs()

# Check success
success = results_recent.success and results_hist.success
print(f"\nValidation complete!")
print(f"Recent data: {'PASS' if results_recent.success else 'FAIL'}")
print(f"Historical data: {'PASS' if results_hist.success else 'FAIL'}")
print(f"Overall success: {success}")

if not success:
    print("\nValidation failures:")
    
    if not results_recent.success:
        print("\nRecent dataset failures:")
        for result in results_recent.results:
            if not result.success:
                print(f"  - {result.expectation_config.expectation_type}")
                if result.result:
                    print(f"    {result.result}")
    
    if not results_hist.success:
        print("\nHistorical dataset failures:")
        for result in results_hist.results:
            if not result.success:
                print(f"  - {result.expectation_config.expectation_type}")
                if result.result:
                    print(f"    {result.result}")
    
    import sys
    sys.exit(1)
