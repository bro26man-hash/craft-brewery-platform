# batch_cost_calculator.py
"""
Craft Brewery Batch Cost Calculator
====================================
Inspired by tfrayner/beerfestdb -> tool_dashboard/CBF_beer_price_calculator.py
(https://github.com/tfrayner/beerfestdb/blob/main/tool_dashboard/CBF_beer_price_calculator.py).

That reference determines a product's sale price from its cask cost and an
ABV-based value, using whichever is greater, then applies a margin. This
script adapts that principle for whole-batch brewing: it tallies the cost of
grain, hops, yeast and packaging for a given batch size (in barrels), derives
the cost-per-barrel and total cost, then applies a configurable margin to
recommend a selling price per barrel.

Usage:
    python batch_cost_calculator.py
"""

# Reference constants
# A US brewing barrel = 31 US gallons
BARREL_TO_GALLONS = 31.0


def calculate_batch_cost(
    grain_cost_per_lb: float,    # $/lb
    hops_cost_per_oz: float,     # $/oz
    yeast_cost_per_unit: float,  # $/unit
    packaging_cost_per_unit: float,  # $/unit
    grain_lbs: float,
    hops_oz: float,
    yeast_units: float,
    packaging_units: float,
    batch_barrels: float,
    margin_percent: float,       # e.g. 30 for 30%
):
    """Compute total cost, cost per barrel, and recommended sale price."""
    # ---- Ingredient line costs ----
    grain_cost      = grain_cost_per_lb * grain_lbs
    hops_cost       = hops_cost_per_oz * hops_oz
    yeast_cost      = yeast_cost_per_unit * yeast_units
    packaging_cost  = packaging_cost_per_unit * packaging_units

    total_ingredient_cost = grain_cost + hops_cost + yeast_cost + packaging_cost

    # ---- Per-barrel metrics ----
    cost_per_barrel = (total_ingredient_cost / batch_barrels) if batch_barrels else 0.0

    # ---- Recommended selling price with margin ----
    # margin_percent is the desired profit margin ON COST
    recommended_price_per_barrel = cost_per_barrel * (1 + margin_percent / 100.0)

    return {
        "grain_cost": grain_cost,
        "hops_cost": hops_cost,
        "yeast_cost": yeast_cost,
        "packaging_cost": packaging_cost,
        "total_ingredient_cost": total_ingredient_cost,
        "batch_barrels": batch_barrels,
        "cost_per_barrel": cost_per_barrel,
        "margin_percent": margin_percent,
        "recommended_price_per_barrel": recommended_price_per_barrel,
    }


def print_report(r: dict):
    print("=" * 55)
    print("   CRAFT BREWERY BATCH COST REPORT")
    print("=" * 55)
    print(f"  Grain cost ............: ${r['grain_cost']:.2f}")
    print(f"  Hops cost .............: ${r['hops_cost']:.2f}")
    print(f"  Yeast cost ............: ${r['yeast_cost']:.2f}")
    print(f"  Packaging cost ........: ${r['packaging_cost']:.2f}")
    print("-" * 55)
    print(f"  TOTAL BATCH COST ......: ${r['total_ingredient_cost']:.2f}")
    print(f"  Batch size ............: {r['batch_barrels']:.2f} bbl")
    print(f"  COST PER BARREL .......: ${r['cost_per_barrel']:.2f}")
    print(f"  Desired margin ........: {r['margin_percent']:.1f}%")
    print("-" * 55)
    print(f"  >> RECOMMENDED SELL PRICE / BARREL: ${r['recommended_price_per_barrel']:.2f}")
    print("=" * 55)


# ------------------------------------------------------------------
# SAMPLE RUN
# ------------------------------------------------------------------
if __name__ == "__main__":
    # Sample 10-barrel batch (a modest craft brew)
    sample = calculate_batch_cost(
        grain_cost_per_lb       = 1.50,    # $/lb
        hops_cost_per_oz        = 0.75,    # $/oz
        yeast_cost_per_unit     = 0.50,    # $/unit
        packaging_cost_per_unit = 0.25,    # $/unit
        grain_lbs               = 200.0,   # lbs
        hops_oz                 = 16.0,    # oz
        yeast_units             = 4.0,     # units
        packaging_units         = 500.0,   # units
        batch_barrels           = 10.0,    # barrels
        margin_percent          = 30.0,    # 30% margin
    )
    print_report(sample)
