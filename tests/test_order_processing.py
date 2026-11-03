import pandas as pd
import pandera.pandas as pa
import pytest

from src.order_processing import (
    calculate_order_total,
    load_orders,
    summarize_orders,
    validate_orders,
)

ORDERS_FILE = "data/orders.csv"
CALCULATION_CASES_FILE = (
    "data/calculation_test_cases.csv"
)
VALIDATION_CASES_FILE = (
    "data/validation_test_cases.csv"
)

calculation_cases = pd.read_csv(
    CALCULATION_CASES_FILE
)

validation_cases = pd.read_csv(
    VALIDATION_CASES_FILE
)


@pytest.mark.parametrize(
    "case",
    calculation_cases.to_dict("records"),
    ids=calculation_cases["test_case_id"]
)
def test_order_calculation(case):
    actual = calculate_order_total(
        case["quantity"],
        case["unit_price"],
        case["discount_pct"]
    )

    assert actual == pytest.approx(
        case["expected_total"],
        abs=0.01
    )


def prepare_validation_scenario(
    orders,
    scenario
):
    orders = orders.copy()

    if scenario == "duplicate_order_id":
        orders.loc[1, "order_id"] = (
            orders.loc[0, "order_id"]
        )

    elif scenario == "zero_quantity":
        orders.loc[0, "quantity"] = 0

    elif scenario == "invalid_payment_status":
        orders.loc[0, "payment_status"] = "Unknown"

    elif scenario == "invalid_discount":
        orders.loc[0, "discount_pct"] = 150

    return orders


@pytest.mark.parametrize(
    "case",
    validation_cases.to_dict("records"),
    ids=validation_cases["test_case_id"]
)
def test_data_validation(case):
    orders = pd.read_csv(ORDERS_FILE)

    scenario_data = prepare_validation_scenario(
        orders,
        case["scenario"]
    )

    expected_valid = case["expected_valid"]

    if expected_valid:
        validate_orders(scenario_data)
    else:
        with pytest.raises(pa.errors.SchemaError):
            validate_orders(scenario_data)


def test_order_summary():
    orders = load_orders(ORDERS_FILE)
    summary = summarize_orders(orders)

    assert summary["order_count"] == 5
    assert summary["paid_orders"] == 3
    assert summary["total_revenue"] == pytest.approx(
        1623.5,
        abs=0.01
    )
