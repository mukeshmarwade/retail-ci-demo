import pandas as pd
import pandera.pandas as pa

order_schema = pa.DataFrameSchema({
    "order_id": pa.Column(
        int,
        unique=True,
        nullable=False
    ),
    "customer_id": pa.Column(
        int,
        nullable=False
    ),
    "quantity": pa.Column(
        int,
        checks=pa.Check.greater_than(0)
    ),
    "unit_price": pa.Column(
        float,
        checks=pa.Check.greater_than(0)
    ),
    "discount_pct": pa.Column(
        int,
        checks=pa.Check.in_range(0, 100)
    ),
    "payment_status": pa.Column(
        str,
        checks=pa.Check.isin(
            ["Paid", "Pending", "Cancelled"]
        )
    ),
},
    strict=True
)


def load_orders(file_path):
    orders = pd.read_csv(file_path)
    return validate_orders(orders)


def validate_orders(orders):
    return order_schema.validate(orders)


def calculate_order_total(quantity,
                          unit_price,
                          discount_pct
                          ):
    subtotal = quantity * unit_price
    discount = subtotal * discount_pct / 100
    return round(subtotal - discount, 2)


def add_order_totals(orders):
    orders = orders.copy()
    orders["order_total"] = orders.apply(
        lambda row: calculate_order_total(
            row["quantity"],
            row["unit_price"],
            row["discount_pct"]
        ),
        axis=1
    )
    return orders


def summarize_orders(orders):
    processed = add_order_totals(orders)
    paid_orders = processed[
        processed["payment_status"] == "Paid"
    ]
    return {
        "order_count": len(processed),
        "paid_orders": len(paid_orders),
        "total_revenue": round(
            paid_orders["order_total"].sum(),
            2
        ),
    }
