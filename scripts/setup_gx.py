from pathlib import Path
from great_expectations.data_context import FileDataContext
from great_expectations.core.expectation_configuration import ExpectationConfiguration

# Ensure base folder and initialize context
gx_dir = Path("gx")

if not (gx_dir / "great_expectations.yml").exists():
    context = FileDataContext.create(project_root_dir=".")
else:
    context = FileDataContext(context_root_dir=str(gx_dir))

datasource_name = "nyc311_pandas"
if datasource_name not in [ds["name"] for ds in context.list_datasources()]:
    context.add_datasource(
        name=datasource_name,
        class_name="Datasource",
        execution_engine={"class_name": "PandasExecutionEngine"},
        data_connectors={
            "default_runtime_data_connector": {
                "class_name": "RuntimeDataConnector",
                "batch_identifiers": ["default_identifier_name"],
            },
        },
    )


def create_suite(suite_name: str, columns: list[str]):
    try:
        suite = context.get_expectation_suite(suite_name)
    except Exception:
        suite = context.add_expectation_suite(suite_name)

    # Basic expectations (table + key + nulls + enums + formats)
    exps = [
        ExpectationConfiguration(
            expectation_type="expect_table_columns_to_match_set",
            kwargs={"column_set": columns, "exact_match": False},
        ),
        ExpectationConfiguration(
            expectation_type="expect_column_values_to_be_unique",
            kwargs={"column": "unique_key"},
        ),
        ExpectationConfiguration(
            expectation_type="expect_column_values_to_not_be_null",
            kwargs={"column": "created_date"},
        ),
        ExpectationConfiguration(
            expectation_type="expect_column_values_to_not_be_null",
            kwargs={"column": "complaint_type"},
        ),
        ExpectationConfiguration(
            expectation_type="expect_table_row_count_to_be_between",
            kwargs={"min_value": 50, "max_value": 5000},
        ),
        ExpectationConfiguration(
            expectation_type="expect_column_values_to_be_in_set",
            kwargs={
                "column": "borough",
                "value_set": [
                    "MANHATTAN",
                    "BROOKLYN",
                    "BRONX",
                    "QUEENS",
                    "STATEN ISLAND",
                    None,
                ],
                "mostly": 0.9,
            },
        ),
    ]
    for e in exps:
        suite.add_expectation(e)

    context.save_expectation_suite(suite)
    print(f"Saved suite: {suite_name}")


# Define two suites (recent/historical)
columns = [
    "unique_key",
    "created_date",
    "closed_date",
    "agency",
    "complaint_type",
    "descriptor",
    "city",
    "borough",
    "latitude",
    "longitude",
]
create_suite("suite_311_recent", columns)
create_suite("suite_311_hist", columns)

# Add a Checkpoint that validates both datasets
# Note: Actual data loading happens in run_checkpoint.py
# Delete existing checkpoint if it exists
try:
    context.delete_checkpoint("checkpoint_311")
except Exception:
    pass

checkpoint_config = {
    "name": "checkpoint_311",
    "config_version": 1.0,
    "class_name": "Checkpoint",
    "run_name_template": "nyc311__%Y-%m-%dT%H-%M-%S",
    "validations": [
        {
            "batch_request": {
                "datasource_name": datasource_name,
                "data_connector_name": "default_runtime_data_connector",
                "data_asset_name": "nyc311_recent",
                "runtime_parameters": {},
                "batch_identifiers": {"default_identifier_name": "recent"},
            },
            "expectation_suite_name": "suite_311_recent",
        },
        {
            "batch_request": {
                "datasource_name": datasource_name,
                "data_connector_name": "default_runtime_data_connector",
                "data_asset_name": "nyc311_hist",
                "runtime_parameters": {},
                "batch_identifiers": {"default_identifier_name": "hist"},
            },
            "expectation_suite_name": "suite_311_hist",
        },
    ],
    "action_list": [
        {
            "name": "store_validation_result",
            "action": {"class_name": "StoreValidationResultAction"},
        },
        {
            "name": "store_evaluation_params",
            "action": {"class_name": "StoreEvaluationParametersAction"},
        },
        {
            "name": "update_data_docs",
            "action": {"class_name": "UpdateDataDocsAction"},
        },
    ],
}

context.add_checkpoint(**checkpoint_config)
print("Checkpoint 'checkpoint_311' ready.")
