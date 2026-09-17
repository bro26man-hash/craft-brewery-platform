# batch_cost_calculator.py
"""
Craft Brewery Batch Cost Calculator
====================================
Inspired by tfrayner/beerfestdb -> tool_dashboard/CBF_beer_price_calculator.py
(https://github.com/tfrayner/beerfestdb)

That reference determines a product's sale price from its cask cost and an
ABV-based value, using whichever is greater, then applies a margin. This
script adapts that principle for whole-batch brewing: it tallies the cost of
grain, hops, yeast and packaging for a given batch size (in barrels), derives
the cost-per-barrel and total cost, then applies a configurable margin to
recommend a selling price per barrel.

Usage:
    python batch_cost_calculator.py
"""

from dataclasses import dataclass, field
from typing import Optional


# ---------------------------------------------------------------------------
# Reference constants (inspired by CBF_beer_price_calculator.py defaults)
# ---------------------------------------------------------------------------
DEFAULT_ABV_COEFFICIENT = 70      # pence per % ABV (reference)
DEFAULT_ABV_CONSTANT   = 230     # pence constant (reference)
DEFAULT_L_COEFFICIENT  = 1.64    # pence per litre margin coefficient (reference)

# Conversion constants
LITERS_PER_BARREL = 119.2404    # US liquid barrels -> litres


@dataclass
class BatchInputs:
    """All cost inputs for a single brewing batch."""
    # Ingredient prices
    grain_price_lb: float   # $ per pound of grain
    hops_price_oz: float    # $ per ounce of hops
    yeast_price_unit: float = 0.0    # $ per yeast unit (pitching rate)
    packaging_price_unit: float = 0.0  # $ per packaging unit (bottles/kegs)

    # Quantities used in the batch
    grain_lb: float = 0.0
    hops_oz: float = 0.0
    yeast_units: float = 1.0
    packaging_units: float = 1.0

    # Batch size & margin
    batch_size_barrels: float = 1.0
    margin_percent: float = 30.0    # markup applied to cost to get sale price

    # Optional ABV fields (mirroring the reference concept)
    abv_percent: Optional[float] = None
    abv_coefficient: float = DEFAULT_ABV_COEFFICIENT
    abv_constant: float = DEFAULT_ABV_CONSTANT


def compute_costs(inp: BatchInputs) -> dict:
    """Compute all costs and recommended price. Returns a results dict."""

    # --- Ingredient costs ---
    grain_cost     = inp.grain_price_lb    * inp.grain_lb
    hops_cost      = inp.hops_price_oz     * inp.hops_oz
    yeast_cost     = inp.yeast_price_unit * inp.yeast_units
    packaging_cost = inp.packaging_price_unit * inp.packaging_units

    ingredient_cost = grain_cost + hops_cost + yeast_cost + packaging_cost

    barrels = inp.batch_size_barrels
    if barrels <= 0:
        raise ValueError("batch_size_barrels must be greater than zero.")

    cost_per_barrel = ingredient_cost / barrels
    total_cost = ingredient_cost

    # --- Sale price per barrel: cost + margin (mirrors the reference's
    #     "use the greater of cost/value as the basis" approach below) ---
    margin_multiplier = 1.0 + (inp.margin_percent / 100.0)
    recommended_price_per_barrel = cost_per_barrel * margin_multiplier

    # --- ABV-based value (carried over from reference, optional) ---
    abv_value_per_barrel = None
    if inp.abv_percent is not None:
        # Reference logic: abv_price = abv * coefficient + constant (in pence)
        abp_pence = inp.abv_percent * inp.abv_coefficient + inp.abv_constant  # pence
        abv_value_per_barrel = (abp_pence / 100.0) * (LITERS_PER_BARREL / 100.0) * 100
        # Use whichever basis (cost vs abv-value) is greater, mirroring reference
        if abv_value_per_barrel is not None:
            basis = max(cost_per_barrel, abv_value_per_barrel)
            recommended_price_per_barrel = basis * margin_multiplier

    return {
        "grain_cost": grain_cost,
        "hops_cost": hops_cost,
        "yeast_cost": yeast_cost,
        "packaging_cost": packaging_cost,
        "total_ingredient_cost": ingredient_cost,
        "total_cost": total_cost,
        "cost_per_barrel": cost_per_barrel,
        "margin_percent": inp.margin_percent,
        "recommended_price_per_barrel": recommended_price_per_barrel,
        "abv_value_per_barrel": abv_value_per_barrel,
    }


def print_results(inp: BatchInputs, res: dict) -> None:
    print("=" * 60)
    print(" CRAFT BREWERY BATCH COST CALCULATOR")
    print("=" * 60)
    print(f" Batch size          : {inp.batch_size_barrels:.2f} barrels")
    print(f" Margin              : {inp.margin_percent:.1f}%")
    print("-" * 60)
    print(" INPUTS ($ and quantities)")
    print(f"  Grain              : ${inp.grain_price_lb:.3f}/lb  x {inp.grain_lb:.1f} lb")
    print(f"  Hops               : ${inp.hops_price_oz:.3f}/oz  x {inp.hops_oz:.1f} oz")
    print(f"  Yeast              : ${inp.yeast_price_unit:.3f}/unit x {inp.yeast_units:.1f}")
    print(f"  Packaging          : ${inp.packaging_price_unit:.3f}/unit x {inp.packaging_units:.1f}")
    print("-" * 60)
    print(" BREAKDOWN")
    print(f"  Grain cost         : ${res['grain_cost']:.2f}")
    print(f"  Hops cost          : ${res['hops_cost']:.2f}")
    print(f"  Yeast cost         : ${res['yeast_cost']:.2f}")
    print(f"  Packaging cost     : ${res['packaging_cost']:.2f}")
    print(f"  Ingredient subtotal: ${res['total_ingredient_cost']:.2f}")
    print("-" * 60)
    print(" TOTALS")
    print(f"  Total batch cost   : ${res['total_cost']:.2f}")
    print(f"  Cost per barrel    : ${res['cost_per_barrel']:.2f}")
    print(f"  Recommended price  : ${res['recommended_price_per_barrel']:.2f} / barrel")
    if res["abv_value_per_barrel"] is not None:
        print(f"  ABV basis value    : ${res['abv_value_per_barrel']:.2f} / barrel")
    print("=" * 60)


# ---------------------------------------------------------------------------
# Run a sample batch when executed directly
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    sample = BatchInputs(
        grain_price_lb=1.20,        # $/lb
        hops_price_oz=8.50,         # $/oz
        yeast_price_unit=4.00,      # $/unit
        packaging_price_unit=3.25,  # $/unit (bottles/kegs)

        grain_lb=120.0,
        hops_oz=30.0,
        yeast_units=3.0,
        packaging_units=150.0,

        batch_size_barrels=10.0,
        margin_percent=35.0,

        abv_percent=6.5,  # optional ABV-based valuation
    )

    results = compute_costs(sample)
    print_results(sample, results)
