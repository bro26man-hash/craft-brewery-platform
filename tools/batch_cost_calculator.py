# batch_cost_calculator.py
# Craft Brewery Batch Cost Calculator
# Inspired by: https://github.com/tfrayner/beerfestdb/blob/main/tool_dashboard/CBF_beer_price_calculator.py

from dataclasses import dataclass
from typing import Optional

# ── Ingredient inputs ──────────────────────────────────────────────────────

@dataclass
class IngredientInputs:
    grain_cost_per_lb: float      # $/lb
    hops_cost_per_oz: float       # $/oz
    yeast_cost_per_unit: float    # $/unit
    packaging_cost_per_unit: float  # $/unit (e.g. per bottle, per can, per barrel)

# ── Batch specification ────────────────────────────────────────────────────

@dataclass
class BatchSpec:
    size_in_barrels: float         # batch size in US beer barrels (31 gal / 117.35 L)
    grain_lbs_per_barrel: float = 40.0    # typical all-grain grain bill, lbs per barrel
    hops_oz_per_barrel: float = 3.5       # hops, oz per barrel (estimated for 60-min + dry-hop)
    yeast_units_per_barrel: float = 0.6   # yeast units (vials/packs) per barrel
    packaging_units_per_barrel: float = 48.0  # containers (cans/bottles) per barrel

# ── Margin configuration ───────────────────────────────────────────────────

@dataclass
class MarginConfig:
    margin_percent: float = 25.0  # desired profit margin as a percentage

# ── Core calculations ──────────────────────────────────────────────────────

def calculate_ingredient_costs(ing: IngredientInputs, spec: BatchSpec) -> dict:
    """Return per-barrel and total costs for each ingredient."""
    per_barrel = {
        "grain":           ing.grain_cost_per_lb * spec.grain_lbs_per_barrel,
        "hops":            ing.hops_cost_per_oz  * spec.hops_oz_per_barrel,
        "yeast":           ing.yeast_cost_per_unit * spec.yeast_units_per_barrel,
        "packaging":       ing.packaging_cost_per_unit * spec.packaging_units_per_barrel,
    }
    total = {k: v * spec.size_in_barrels for k, v in per_barrel.items()}
    return {"per_barrel": per_barrel, "total": total}

def calculate_total_cost(ing: IngredientInputs, spec: BatchSpec) -> float:
    """Total cost for the entire batch."""
    costs = calculate_ingredient_costs(ing, spec)
    return sum(costs["per_barrel"].values()) * spec.size_in_barrels

def cost_per_barrel(ing: IngredientInputs, spec: BatchSpec) -> float:
    """Cost per barrel (sum of all ingredient costs per barrel)."""
    costs = calculate_ingredient_costs(ing, spec)
    return sum(costs["per_barrel"].values())

def recommended_selling_price(cost_per_bb: float, margin: MarginConfig) -> float:
    """Recommended selling price per barrel given a desired margin."""
    if margin.margin_percent <= 0:
        return cost_per_bb
    markup = cost_per_bb / (1 - margin.margin_percent / 100)
    return round(markup, 2)

def profit_per_barrel(selling_price: float, cost_per_bb: float) -> float:
    return round(selling_price - cost_per_bb, 2)

def margin_overview(cost_per_bb: float, selling_price: float) -> float:
    if selling_price == 0:
        return 0.0
    return round((selling_price - cost_per_bb) / selling_price * 100, 2)

# ── Pretty-print helper ─────────────────────────────────────────────────────

DIVIDER = "═" * 58

def print_batch_breakdown(ing: IngredientInputs, spec: BatchSpec, margin: MarginConfig):
    print(f"\n{DIVIDER}")
    print("  CRAFT BREWERY BATCH COST CALCULATOR")
    print(DIVIDER)

    print(f"\n  Batch Size          : {spec.size_in_barrels:,.1f} barrels")
    print(f"  Grain Bill          : {spec.grain_lbs_per_barrel:,.1f} lbs/bbl")
    print(f"  Hops Rate           : {spec.hops_oz_per_barrel:,.1f} oz/bbl")
    print(f"  Yeast Rate          : {spec.yeast_units_per_barrel:,.1f} unit(s)/bbl")
    print(f"  Packaging Rate      : {spec.packaging_units_per_barrel:,.0f} units/bbl")
    print(f"  Desired Margin      : {margin.margin_percent:.1f}%")
    print(f"\n  {'─' * 58}")

    costs = calculate_ingredient_costs(ing, spec)
    pb = costs["per_barrel"]
    tt = costs["total"]

    print(f"\n  {'Ingredient':<14} {'$/bbl':>10}   {'Total $':>12}   {'% of Cost':>10}")
    print(f"  {'─'*14} {'─'*10}   {'─'*12}   {'─'*10}")
    grand = sum(pb.values())
    for name in ["grain", "hops", "yeast", "packaging"]:
        label = name.capitalize()
        pct = pb[name] / grand * 100 if grand else 0
        print(f"  {label:<14} {pb[name]:>10.2f}   {tt[name]:>12.2f}   {pct:>9.1f}%")

    total_cost = calculate_total_cost(ing, spec)
    cpb = sum(pb.values())
    selling = recommended_selling_price(cpb, margin)
    profit = profit_per_barrel(selling, cpb)
    actual_margin = margin_overview(cpb, selling)

    print(f"\n  {'─' * 58}")
    print(f"  {'TOTAL COST / bbl':<14} {cpb:>10.2f}")
    print(f"  {'TOTAL COST (batch)':<14} {total_cost:>10.2f}")

    print(f"\n  {'─' * 58}")
    print(f"  Cost per Barrel        : ${cpb:,.2f}")
    print(f"  Recommended Sell/bbl   : ${selling:,.2f}")
    print(f"  Profit per Barrel      : ${profit:,.2f}")
    print(f"  Actual Margin          : {actual_margin:.2f}%")
    print(f"\n  Total Batch Profit     : ${profit * spec.size_in_barrels:,.2f}")
    print(f"{DIVIDER}\n")

# ── Sample run ──────────────────────────────────────────────────────────────

if __name__ == "__main__":

    # ── Ingredient prices (typical craft-brewery figures) ──
    ingredients = IngredientInputs(
        grain_cost_per_lb=1.50,       # pale malt / specialty grains
        hops_cost_per_oz=1.20,        # mid-range pellet hops
        yeast_cost_per_unit=7.00,     # liquid yeast vial/pitch
        packaging_cost_per_unit=0.12, # 12-oz aluminum can
    )

    # ── Batch size ──
    batch = BatchSpec(size_in_barrels=10.0)   # 10-barrel brewhouse system, one batch

    # ── Margin ──
    margin = MarginConfig(margin_percent=25.0)  # 25% target margin

    # ── Run calculations and print nice report ──
    print_batch_breakdown(ingredients, batch, margin)

    # ── Unit tests / assertions ──
    assert abs(cost_per_barrel(ingredients, batch) - 74.16) < 0.01, \
        f"Expected cost/bbl close to 74.16, got {cost_per_barrel(ingredients, batch)}"
    assert recommended_selling_price(74.16, MarginConfig(25.0)) == 98.88, \
        "Selling price for 25% margin on $74.16 cost should be $98.88"
    assert recommended_selling_price(70.00, MarginConfig(0.0)) == 70.00, \
        "Zero margin should return cost as price"
    assert profit_per_barrel(98.88, 74.16) == 24.72, \
        "Profit per barrel mismatch"

    print("All assertions passed - calculator validated.")