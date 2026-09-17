"""
Craft Brewery Batch Cost Calculator
====================================
Inspired by tfrayner/beerfestdb's CBF_beer_price_calculator.py
https://github.com/tfrayner/beerfestdb/blob/main/tool_dashboard/CBF_beer_price_calculator.py

The original calculates beer sale prices based on cask cost per litre and ABV,
taking the greater of cost-based or ABV-based pricing, then rounding.

This adaptation computes the total cost of a brewing batch from ingredient inputs,
derives cost-per-barrel, and applies a configurable margin to recommend a
selling price per barrel.
"""

import math


def calculate_batch_cost(
    grain_cost_per_lb,
    hops_cost_per_oz,
    yeast_cost_per_unit,
    packaging_cost_per_unit,
    batch_size_barrels=5.0,
    margin_percent=30.0,
    grain_lbs_per_barrel=30.0,
    hops_oz_per_barrel=1.5,
    yeast_units_per_batch=1.0,
    packaging_units_per_barrel=1.0,
):
    """
    Calculate the total cost and recommended selling price for a brewing batch.

    Parameters
    ----------
    grain_cost_per_lb : float  - price of malt grain per pound ($)
    hops_cost_per_oz  : float  - price of hops per ounce ($)
    yeast_cost_per_unit : float - price of yeast per unit/packet ($)
    packaging_cost_per_unit : float - price of bottles/cans per unit ($)
    batch_size_barrels : float  - number of barrels being brewed
    margin_percent     : float  - desired margin percentage on cost
    grain_lbs_per_barrel : float - lbs of grain needed per barrel
    hops_oz_per_barrel   : float - oz of hops needed per barrel
    yeast_units_per_batch : float - yeast units needed for the whole batch
    packaging_units_per_barrel : float - packaging units (bottles/cans) per barrel

    Returns
    -------
    dict with all computed cost and pricing figures
    """

    # ---- Ingredient quantities for the entire batch ----
    total_grain_lbs = grain_lbs_per_barrel * batch_size_barrels
    total_hops_oz = hops_oz_per_barrel * batch_size_barrels
    total_yeast = yeast_units_per_batch
    total_packaging = packaging_units_per_barrel * batch_size_barrels

    # ---- Ingredient dollar costs ----
    grain_cost = total_grain_lbs * grain_cost_per_lb
    hops_cost = total_hops_oz * hops_cost_per_oz
    yeast_cost = total_yeast * yeast_cost_per_unit
    packaging_cost = total_packaging * packaging_cost_per_unit

    # ---- Total batch cost & cost per barrel ----
    total_cost = grain_cost + hops_cost + yeast_cost + packaging_cost
    cost_per_barrel = total_cost / batch_size_barrels if batch_size_barrels > 0 else 0.0

    # ---- Margin & recommended selling price ----
    # Following the original's philosophy: take the greater of cost-based or
    # a value-based estimator, then apply margin.
    value_coefficient = 1.3
    value_based_price = cost_per_barrel * value_coefficient
    base_price = max(cost_per_barrel, value_based_price)

    margin_multiplier = 1.0 + (margin_percent / 100.0)
    recommended_price_per_barrel = base_price * margin_multiplier

    # Round up to the nearest $0.50 for practical pricing
    # (mirrors the original's rounding to nearest 20 pence)
    recommended_price_per_barrel = math.ceil(recommended_price_per_barrel * 2) / 2.0

    return {
        "batch_size_barrels": batch_size_barrels,
        "total_grain_lbs": round(total_grain_lbs, 2),
        "total_hops_oz": round(total_hops_oz, 2),
        "total_yeast_units": round(total_yeast, 2),
        "total_packaging_units": round(total_packaging, 2),
        "grain_cost": round(grain_cost, 2),
        "hops_cost": round(hops_cost, 2),
        "yeast_cost": round(yeast_cost, 2),
        "packaging_cost": round(packaging_cost, 2),
        "total_batch_cost": round(total_cost, 2),
        "cost_per_barrel": round(cost_per_barrel, 2),
        "value_based_price": round(value_based_price, 2),
        "base_price": round(base_price, 2),
        "margin_percent": margin_percent,
        "recommended_price_per_barrel": round(recommended_price_per_barrel, 2),
    }


def print_results(r):
    """Pretty-print the batch cost calculation results."""
    print("=" * 60)
    print("  CRAFT BREWERY BATCH COST CALCULATOR")
    print("=" * 60)
    print(f"\n  Batch Size:        {r['batch_size_barrels']} barrels")
    print(f"\n  --- Ingredient Quantities ---")
    print(f"    Grain:           {r['total_grain_lbs']} lbs")
    print(f"    Hops:            {r['total_hops_oz']} oz")
    print(f"    Yeast:           {r['total_yeast_units']} units")
    print(f"    Packaging:       {r['total_packaging_units']} units")
    print(f"\n  --- Ingredient Costs ---")
    print(f"    Grain cost:      ${r['grain_cost']}")
    print(f"    Hops cost:       ${r['hops_cost']}")
    print(f"    Yeast cost:      ${r['yeast_cost']}")
    print(f"    Packaging cost:  ${r['packaging_cost']}")
    print(f"\n  --- Cost Summary ---")
    print(f"    Total batch cost:       ${r['total_batch_cost']}")
    print(f"    Cost per barrel:        ${r['cost_per_barrel']}")
    print(f"    Value-based price:      ${r['value_based_price']}")
    print(f"    Base price (greater):   ${r['base_price']}")
    print(f"\n  --- Pricing ---")
    print(f"    Margin:                  {r['margin_percent']}%")
    print(f"    >> Recommended sell price/barrel: ${r['recommended_price_per_barrel']}")
    print("\n" + "=" * 60)


# =========================================================================
# SAMPLE RUN - a 5-barrel batch with typical craft-brew parameters
# =========================================================================
if __name__ == "__main__":
    results = calculate_batch_cost(
        grain_cost_per_lb=0.45,
        hops_cost_per_oz=0.80,
        yeast_cost_per_unit=1.50,
        packaging_cost_per_unit=0.10,
        batch_size_barrels=5.0,
        margin_percent=30.0,
    )
    print_results(results)
