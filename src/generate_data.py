"""
Generates a synthetic multi-region retail transactions dataset.

The dataset is entirely synthetic (seeded, reproducible) — it does not
represent any real company, customer, or transaction. It is designed to
resemble a realistic retail operation (seasonality, regional mix, product
categories, discounting, returns) so the analysis techniques below transfer
directly to real point-of-sale / ERP exports.

Usage:
    python src/generate_data.py
"""

from __future__ import annotations

import os

import numpy as np
import pandas as pd

SEED = 42
N_CUSTOMERS = 1_200
N_ORDERS = 18_000
START_DATE = "2023-01-01"
END_DATE = "2024-12-31"

REGIONS = ["North", "South", "East", "West", "Central"]
CATEGORIES = {
    "Electronics": ["Headphones", "Smart Watch", "Bluetooth Speaker", "Laptop Stand", "Webcam"],
    "Home & Kitchen": ["Air Fryer", "Coffee Maker", "Cookware Set", "Vacuum Cleaner", "Blender"],
    "Apparel": ["Running Shoes", "Jacket", "Backpack", "Sunglasses", "Wristwatch"],
    "Office": ["Desk Lamp", "Ergonomic Chair", "Monitor Arm", "Notebook Set", "Whiteboard"],
    "Outdoor": ["Tent", "Camping Chair", "Cooler Box", "Hiking Boots", "Water Bottle"],
}
CHANNELS = ["Online", "In-Store", "Marketplace"]


def _seasonal_weight(dates: pd.DatetimeIndex) -> np.ndarray:
    day_of_year = dates.dayofyear.to_numpy()
    holiday_bump = np.where((dates.month == 11) | (dates.month == 12), 1.35, 1.0)
    seasonal = 1.0 + 0.15 * np.sin(2 * np.pi * (day_of_year / 365.0))
    return seasonal * holiday_bump


def generate() -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    rng = np.random.default_rng(SEED)

    # --- customers ---
    customer_ids = np.arange(1, N_CUSTOMERS + 1)
    signup_dates = pd.to_datetime(START_DATE) + pd.to_timedelta(
        rng.integers(0, 500, size=N_CUSTOMERS), unit="D"
    )
    customers = pd.DataFrame(
        {
            "customer_id": customer_ids,
            "region": rng.choice(REGIONS, size=N_CUSTOMERS, p=[0.24, 0.22, 0.20, 0.19, 0.15]),
            "signup_date": signup_dates,
            "loyalty_member": rng.choice([0, 1], size=N_CUSTOMERS, p=[0.62, 0.38]),
        }
    )

    # --- product catalog ---
    rows = []
    product_id = 1
    for category, products in CATEGORIES.items():
        for name in products:
            base_price = round(rng.uniform(15, 250), 2)
            rows.append(
                {
                    "product_id": product_id,
                    "category": category,
                    "product_name": name,
                    "unit_cost": round(base_price * rng.uniform(0.45, 0.65), 2),
                    "list_price": base_price,
                }
            )
            product_id += 1
    products_df = pd.DataFrame(rows)

    # --- orders ---
    all_days = pd.date_range(START_DATE, END_DATE, freq="D")
    weights = _seasonal_weight(all_days)
    weights = weights / weights.sum()
    order_dates = rng.choice(all_days, size=N_ORDERS, p=weights)

    order_customer = rng.choice(customer_ids, size=N_ORDERS)
    order_product = rng.choice(products_df["product_id"].to_numpy(), size=N_ORDERS)
    order_channel = rng.choice(CHANNELS, size=N_ORDERS, p=[0.52, 0.31, 0.17])
    quantity = rng.integers(1, 5, size=N_ORDERS)

    discount_pct = np.clip(rng.normal(0.08, 0.07, size=N_ORDERS), 0, 0.45)
    # Marketplace channel and Nov/Dec carry heavier average discounting.
    is_marketplace = order_channel == "Marketplace"
    is_holiday = pd.DatetimeIndex(order_dates).month.isin([11, 12])
    discount_pct = np.clip(discount_pct + is_marketplace * 0.03 + is_holiday * 0.05, 0, 0.6)

    orders = pd.DataFrame(
        {
            "order_id": np.arange(1, N_ORDERS + 1),
            "order_date": order_dates,
            "customer_id": order_customer,
            "product_id": order_product,
            "channel": order_channel,
            "quantity": quantity,
            "discount_pct": np.round(discount_pct, 3),
        }
    )
    orders = orders.merge(products_df[["product_id", "category", "unit_cost", "list_price"]], on="product_id")
    orders["region"] = orders["customer_id"].map(customers.set_index("customer_id")["region"])

    orders["gross_revenue"] = (orders["list_price"] * orders["quantity"]).round(2)
    orders["net_revenue"] = (orders["gross_revenue"] * (1 - orders["discount_pct"])).round(2)
    orders["cogs"] = (orders["unit_cost"] * orders["quantity"]).round(2)
    orders["profit"] = (orders["net_revenue"] - orders["cogs"]).round(2)

    # returns: ~6% of orders, biased slightly toward Apparel and Marketplace
    return_prob = 0.06 + (orders["category"] == "Apparel") * 0.03 + (orders["channel"] == "Marketplace") * 0.02
    orders["is_returned"] = rng.random(N_ORDERS) < return_prob

    orders = orders.sort_values("order_date").reset_index(drop=True)
    return customers, products_df, orders


def main() -> None:
    customers, products_df, orders = generate()
    os.makedirs("data", exist_ok=True)  # data/ is git-ignored, so a fresh clone lacks it
    customers.to_csv("data/customers.csv", index=False)
    products_df.to_csv("data/products.csv", index=False)
    orders.to_csv("data/orders.csv", index=False)
    print(f"customers: {len(customers):,} rows")
    print(f"products:  {len(products_df):,} rows")
    print(f"orders:    {len(orders):,} rows")


if __name__ == "__main__":
    main()
