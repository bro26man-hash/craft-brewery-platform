"""
batch_cost_calculator.py
========================
A standalone craft brewery batch cost calculator inspired by the reference
code in tfrayner/beerfestdb (`tool_dashboard/CBF_beer_price_calculator.py`).

The original project derives a sale price from the *greater* of an ABV-based
value and a cask-based cost, then applies a pricing coefficient. This script
adapts that idea for batch-level costing: it accumulates ingredient and
packaging costs across a batch, derives the cost per barrel, and applies a
configurable margin to recommend a selling price per barrel.

Inputs
------
- grain       : $/lb  and lbs used
- hops        : $/oz  and oz used
- yeast       : $/unit and units used
- packaging   : $/unit and units used
- batch_size  : batch size in barrels
- margin_pct  : desired margin percentage (e.g. 30 for 30%)

Outputs
-------
- total_cost          : sum of all ingredient + packaging costs
- cost_per_barrel     : total_cost / batch_size
- recommended_price   : cost_per_barrel * (1 + margin_pct/100)
"""


def calculate_batch_cost(
    grain_price_per_lb: float, grain_lbs: float,
    hops_price_per_oz: float, hops_oz: float,
    yeast_price_per_unit: float, yeast_units: float,
    packaging_price_per_unit: float, packaging_units: float,
    batch_size_barrels: float,
    margin_pct: float,
) -> dict:
    """Compute total cost, cost per barrel, and recommended sale price."""
    if batch_size_barrels <= 0:
        raise ValueError("batch_size_barrels must be greater than zero")

    grain_cost = grain_price_per_lb * grain_lbs
    hops_cost = hops_price_per_oz * hops_oz
    yeast_cost = yeast_price_per_unit * yeast_units
    packaging_cost = packaging_price_per_unit * packaging_units

    total_cost = grain_cost + hops_cost + yeast_cost + packaging_cost
    cost_per_barrel = total_cost / batch_size_barrels

    # Recommended selling price applies the configured margin on top of cost.
    recommended_price = cost_per_barrel * (1 + margin_pct / 100.0)

    return {
        "grain_cost": grain_cost,
        "hops_cost": hops_cost,
        "yeast_cost": yeast_cost,
        "packaging_cost": packaging_cost,
        "total_cost": total_cost,
        "batch_size_barrels": batch_size_barrels,
        "cost_per_barrel": cost_per_barrel,
        "margin_pct": margin_pct,
        "recommended_price_per_barrel": recommended_price,
    }


def _usd(value: float) -> str:
    return f"${value:,.2f}"


def main():
    # ---- Sample batch ---------------------------------------------------
    # A 10 BBL batch with modest ingredient quantities and a 30% margin.
    grain_price_per_lb = 0.75    # $/lb
    grain_lbs = 600.0            # lbs

    hops_price_per_oz = 12.00    # $/oz
    hops_oz = 50.0               # oz

    yeast_price_per_unit = 150.0 # $/unit
    yeast_units = 4.0            # units

    packaging_price_per_unit = 3.00  # $/unit
    packaging_units = 200.0         # units

    batch_size_barrels = 10.0   # barrels
    margin_pct = 30.0           # percent

    result = calculate_batch_cost(
        grain_price_per_lb, grain_lbs,
        hops_price_per_oz, hops_oz,
        yeast_price_per_unit, yeast_units,
        packaging_price_per_unit, packaging_units,
        batch_size_barrels,
        margin_pct,
    )

    print("=" * 55)
    print("CRAFT BREWERY BATCH COST CALCULATOR")
    print("=" * 55)
    print(f"Grain cost        : {_usd(result['grain_cost'])}")
    print(f"Hops cost         : {_usd(result['hops_cost'])}")
    print(f"Yeast cost        : {_usd(result['yeast_cost'])}")
    print(f"Packaging cost    : {_usd(result['packaging_cost'])}")
    print("-" * 55)
    print(f"TOTAL COST        : {_usd(result['total_cost'])}")
    print(f"BATCH SIZE        : {result['batch_size_barrels']:.1f} barrels")
    print("-" * 55)
    print(f"COST PER BARREL   : {_usd(result['cost_per_barrel'])}")
    print(f"MARGIN            : {result['margin_pct']:.0f}%")
    print("-" * 55)
    print(f"RECOMMENDED SALE  : {_usd(result['recommended_price_per_barrel'])} / barrel")
    print("=" * 55)

    # --- self-checks (corrected to match the sample-batch math) ----------
    # grain 0.75*600=450, hops 12*50=600, yeast 150*4=600, packaging 3*200=600
    assert abs(result["total_cost"] - 2250.0) < 1e-6, result["total_cost"]
    assert abs(result["cost_per_barrel"] - 225.0) < 1e-6, result["cost_per_barrel"]
    # 225 * 1.30 = 292.50
    assert abs(result["recommended_price_per_barrel"] - 292.50) < 1e-6, result["recommended_price_per_barrel"]
    # zero-volume batch must be rejected
    try:
        calculate_batch_cost(1, 1, 1, 1, 1, 1, 1, 1, 0, 10)
        raise SystemExit("Expected ValueError for zero batch size was not raised")
    except ValueError:
        pass
    print("\n[OK] Sample batch validated successfully.")


if __name__ == "__main__":
    main()
