#!/usr/bin/env python3
"""
================================================================================
 Craft Brewery Batch Cost Calculator
================================================================================

 Inspired by: tfrayner/beerfestdb
   Repository: https://github.com/tfrayner/beerfestdb
   File:       tool_dashboard/CBF_beer_price_calculator.py

 The reference calculator determines beer sale prices by comparing an ABV-based
 value against the production cost and using whichever is greater, then rounding
 up to the nearest 20 pence. This script applies the same philosophy to craft
 brewery batch costing:

   1. Compute the *production cost* from ingredient usage and unit prices.
   2. Compute an *ABV-based value* reflecting the beer's strength and quality.
   3. Take the **greater** of the two as the cost basis (same max() logic as
      the reference calculator).
   4. Apply a configurable **margin percentage** to derive the recommended
      selling price per barrel.

 Usage
 -----
   python batch_cost_calculator.py            # runs with a sample batch
   python batch_cost_calculator.py --quiet    # suppresses console output

 All parameters are editable module-level dataclasses or keyword arguments to
 ``calculate_batch_cost``.

 Author: AI coding assistant
================================================================================
"""

from __future__ import annotations

import argparse
import math
import sys
from dataclasses import dataclass


# ============================================================================
# Constants
# ============================================================================

# Volume conversion (US beer barrel)
BBL_TO_GALLONS: float = 31.0

# Default brewing rates (per barrel) — can be overridden per batch
DEFAULT_GRAIN_LB_PER_BBL: float = 20.0    # lbs of grain per barrel
DEFAULT_HOPS_OZ_PER_BBL: float = 1.0      # oz of hops per barrel
DEFAULT_PACKAGING_UNITS_PER_BBL: int = 100  # 12-oz cans per barrel

# ABV valuation (adapted from the reference's abv_coefficient / abv_constant).
# The reference uses: abv_price = ABV * coefficient + constant  (in pence).
# We adapt the same linear formula to dollars per barrel.
ABV_VALUE_COEFFICIENT: float = 75.0   # $ per ABV point per barrel
ABV_VALUE_CONSTANT: float = 20.0      # base $ per barrel


# ============================================================================
# Data structures
# ============================================================================

@dataclass
class IngredientCosts:
    """Unit costs for every ingredient and supply."""
    grain_per_lb: float       = 0.50    # $/lb
    hops_per_oz: float        = 1.20    # $/oz
    yeast_per_unit: float     = 5.00    # $/unit (one packet/vial per batch)
    packaging_per_unit: float = 3.00    # $/unit (per 12-oz can or bottle)


@dataclass
class BatchParams:
    """Batch sizing, usage rates, and beer profile."""
    batch_size_bbl: float         = 5.0    # barrels
    grain_lb_per_bbl: float       = DEFAULT_GRAIN_LB_PER_BBL
    hops_oz_per_bbl: float        = DEFAULT_HOPS_OZ_PER_BBL
    yeast_units_per_batch: int    = 1
    packaging_units_per_bbl: int  = DEFAULT_PACKAGING_UNITS_PER_BBL
    abv: float                    = 6.0    # ABV percentage points


@dataclass
class CostResult:
    """All intermediate and final cost/price figures."""
    total_grain_cost: float
    total_hops_cost: float
    total_yeast_cost: float
    total_packaging_cost: float
    total_production_cost: float
    cost_per_bbl: float
    abv_value_per_bbl: float
    adjusted_basis: float        # max(cost_per_bbl, abv_value_per_bbl)
    margin_percentage: float
    recommended_price_per_bbl: float


# ============================================================================
# Core calculation logic
# ============================================================================

def calculate_batch_cost(
    ingredient_costs: IngredientCosts,
    batch_params: BatchParams,
    margin_percentage: float = 0.30,
) -> CostResult:
    """
    Calculate total production cost, cost per barrel, and recommended selling
    price per barrel for a brewing batch.

    Philosophy (mirrors the reference calculator's max() approach):
      - Build the *production cost* from actual ingredient usage & unit prices.
      - Build an *ABV-based value* so lighter beers aren't under-priced.
      - Use ``max(production_cost, abv_value)`` as the basis.
      - Apply ``margin_percentage`` on top of that basis.

    Parameters
    ----------
    ingredient_costs : IngredientCosts
        Unit prices for grain, hops, yeast, and packaging.
    batch_params : BatchParams
        Batch size, usage rates, and ABV.
    margin_percentage : float
        Desired profit margin as a decimal (0.30 = 30%).

    Returns
    -------
    CostResult
    """
    bbl = batch_params.batch_size_bbl

    # --- Aggregate ingredient quantities ---
    total_grain_lb      = batch_params.grain_lb_per_bbl   * bbl
    total_hops_oz       = batch_params.hops_oz_per_bbl    * bbl
    total_packaging_qty = batch_params.packaging_units_per_bbl * bbl

    # --- Ingredient line costs ---
    total_grain_cost     = total_grain_lb      * ingredient_costs.grain_per_lb
    total_hops_cost      = total_hops_oz       * ingredient_costs.hops_per_oz
    total_yeast_cost     = batch_params.yeast_units_per_batch * ingredient_costs.yeast_per_unit
    total_packaging_cost = total_packaging_qty * ingredient_costs.packaging_per_unit

    # --- Totals ---
    total_production_cost = (
        total_grain_cost + total_hops_cost + total_yeast_cost + total_packaging_cost
    )
    cost_per_bbl = total_production_cost / bbl if bbl > 0 else 0.0

    # --- ABV-based value per barrel (same linear formula shape as reference) ---
    #   reference: abv_price = ABV * coefficient + constant   (in pence)
    #   ours:      abv_value = ABV * coefficient  + constant   (in $/bbl)
    abv_value_per_bbl = (
        batch_params.abv * ABV_VALUE_COEFFICIENT + ABV_VALUE_CONSTANT
    )

    # --- Use the greater basis (reference philosophy) ---
    adjusted_basis = max(cost_per_bbl, abv_value_per_bbl)

    # --- Apply margin ---
    recommended_price_per_bbl = adjusted_basis * (1.0 + margin_percentage)

    return CostResult(
        total_grain_cost=total_grain_cost,
        total_hops_cost=total_hops_cost,
        total_yeast_cost=total_yeast_cost,
        total_packaging_cost=total_packaging_cost,
        total_production_cost=total_production_cost,
        cost_per_bbl=cost_per_bbl,
        abv_value_per_bbl=abv_value_per_bbl,
        adjusted_basis=adjusted_basis,
        margin_percentage=margin_percentage,
        recommended_price_per_bbl=recommended_price_per_bbl,
    )


# ============================================================================
# Pretty printing
# ============================================================================

def _fmt(label: str, value: float, unit: str = "$") -> str:
    """Right-align a currency value inside a fixed-width field."""
    return f"{label:<28} {unit}{value:>10.2f}"


def print_results(result: CostResult, params: BatchParams) -> None:
    """Print a formatted cost breakdown to the console."""
    bar = "=" * 58
    sub  = "-" * 40

    print(f"\n{bar}")
    print("       CRAFT BREWERY BATCH COST CALCULATOR".center(58))
    print(bar)

    # --- Batch overview ---
    print(f"\n  Batch Configuration")
    print(sub)
    print(f"  {'Batch Size':<28} {params.batch_size_bbl:>10.1f} bbl ({params.batch_size_bbl * BBL_TO_GALLONS:.0f} gal)")
    print(f"  {'ABV':<28} {params.abv:>10.1f}%")
    print(f"  {'Grain Rate':<28} {params.grain_lb_per_bbl:>10.1f} lb/bbl")
    print(f"  {'Hops Rate':<28} {params.hops_oz_per_bbl:>10.2f} oz/bbl")
    print(f"  {'Packaging Rate':<28} {params.packaging_units_per_bbl:>10} units/bbl")
    print(f"  {'Margin Percentage':<28} {result.margin_percentage * 100:>9.0f}%")

    # --- Ingredient cost breakdown ---
    print(f"\n  Ingredient Cost Breakdown")
    print(sub)
    print(_fmt("Grain:",    result.total_grain_cost))
    print(f"      ({params.grain_lb_per_bbl * params.batch_size_bbl:.1f} lb × input $/lb)")
    print(_fmt("Hops:",     result.total_hops_cost))
    print(f"      ({params.hops_oz_per_bbl * params.batch_size_bbl:.2f} oz × input $/oz)")
    print(_fmt("Yeast:",    result.total_yeast_cost))
    print(f"      ({params.yeast_units_per_batch} unit × input $/unit)")
    print(_fmt("Packaging:", result.total_packaging_cost))
    print(f"      ({params.packaging_units_per_bbl * params.batch_size_bbl} units × input $/unit)")

    # --- Totals & pricing ---
    print(f"\n  Cost & Pricing Summary")
    print(sub)
    print(_fmt("Total Production Cost:", result.total_production_cost))
    print(_fmt("Cost per Barrel:",         result.cost_per_bbl))
    print(_fmt("ABV-Based Value/Barrel:",  result.abv_value_per_bbl))
    print(f"  {'── Basis Used (greater of):':<28} ${result.adjusted_basis:>10.2f}")
    print(f"  {'── Recommended Price/Barrel:':<28} ${result.recommended_price_per_bbl:>10.2f}")
    print(bar)
    print(f"\n  💰  Recommended Selling Price: ${result.recommended_price_per_bbl:.2f} per barrel")
    print(f"\n{bar}\n")


# ============================================================================
# Validation (self-check)
# ============================================================================

def _validate(result: CostResult, params: BatchParams) -> None:
    """Run sanity checks against known formulas; abort on any failure."""
    checks: list[tuple[str, bool]] = []

    # 1. Total == sum of parts
    expected_total = (
        result.total_grain_cost
        + result.total_hops_cost
        + result.total_yeast_cost
        + result.total_packaging_cost
    )
    checks.append((
        "Total production cost == sum of ingredient subtotals",
        math.isclose(result.total_production_cost, expected_total, abs_tol=0.01),
    ))

    # 2. Cost/bbl == total / bbl
    checks.append((
        "Cost per barrel == total production cost ÷ batch size",
        math.isclose(result.cost_per_bbl, result.total_production_cost / params.batch_size_bbl, abs_tol=0.01),
    ))

    # 3. Margin applied correctly
    expected_price = result.adjusted_basis * (1.0 + result.margin_percentage)
    checks.append((
        "Recommended price == basis × (1 + margin)",
        math.isclose(result.recommended_price_per_bbl, expected_price, abs_tol=0.01),
    ))

    # 4. Basis is always ≥ cost_per_bbl (max() guarantee)
    checks.append((
        "Adjusted basis ≥ cost per barrel (max() principle)",
        result.adjusted_basis >= result.cost_per_bbl,
    ))

    print("  Self-Validation Checks")
    print("  " + "-" * 40)
    all_pass = True
    for name, passed in checks:
        mark = "✅ PASS" if passed else "❌ FAIL"
        if not passed:
            all_pass = False
        print(f"    {mark}   {name}")

    if all_pass:
        print("\n  🎉  All validation checks passed!")
    else:
        print("\n  ⚠️  Some validation checks FAILED!")
        sys.exit(1)


# ============================================================================
# Sample run / demo
# ============================================================================

def run_sample() -> None:
    """Execute the calculator against a pre-configured sample batch."""
    # Sample: 5 bbl pale ale, 6% ABV, 30% margin
    costs = IngredientCosts(
        grain_per_lb=0.50,
        hops_per_oz=1.20,
        yeast_per_unit=5.00,
        packaging_per_unit=3.00,
    )
    params = BatchParams(
        batch_size_bbl=5.0,
        grain_lb_per_bbl=20.0,
        hops_oz_per_bbl=1.0,
        yeast_units_per_batch=1,
        packaging_units_per_bbl=100,
        abv=6.0,
    )
    margin = 0.30

    result = calculate_batch_cost(costs, params, margin)
    print_results(result, params)
    _validate(result, params)

    # Return the result so callers can inspect programmatically
    return result


# ============================================================================
# CLI
# ============================================================================

def main() -> None:
    parser = argparse.ArgumentParser(
        description="Craft Brewery Batch Cost Calculator — compute batch costs and recommended selling prices."
    )
    parser.add_argument(
        "--quiet", action="store_true",
        help="Skip the sample print (run validation only).",
    )
    args = parser.parse_args()

    if not args.quiet:
        run_sample()
    else:
        # Quick validation-only path
        costs = IngredientCosts()
        params = BatchParams()
        result = calculate_batch_cost(costs, params, 0.30)
        _validate(result, params)
        print("  Validation-only mode: all checks passed.")


if __name__ == "__main__":
    main()
