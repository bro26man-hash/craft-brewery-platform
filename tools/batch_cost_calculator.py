#!/usr/bin/env python3
"""
Craft Brewery Batch Cost Calculator
====================================
Calculates batch economics for a craft brewery:
  - Total ingredient / packaging cost
  - Cost per barrel
  - Recommended selling price per barrel (configurable margin)

Inspired by: TFrayner/beerfestdb CBF_beer_price_calculator.py
GitHub: https://github.com/tfrayner/beerfestdb
"""

import sys


def get_float_input(prompt: str, default: float) -> float:
    """Prompt for a float value, falling back to *default* on empty input."""
    raw = input(f"{prompt} [{default}]: ").strip()
    return float(raw) if raw else default


def calculate_batch_cost(
    grain_cost_per_lb: float,
    grain_lbs: float,
    hops_cost_per_oz: float,
    hops_oz: float,
    yeast_cost_per_unit: float,
    yeast_units: float,
    packaging_cost_per_unit: float,
    packaging_units: float,
    batch_size_barrels: float,
):
    """Return (total_cost, cost_per_barrel, cost_breakdown)."""
    grain_cost = grain_cost_per_lb * grain_lbs
    hops_cost = hops_cost_per_oz * hops_oz
    yeast_cost = yeast_cost_per_unit * yeast_units
    packaging_cost = packaging_cost_per_unit * packaging_units

    total_cost = grain_cost + hops_cost + yeast_cost + packaging_cost
    cost_per_barrel = total_cost / batch_size_barrels

    breakdown = {
        "grain": grain_cost,
        "hops": hops_cost,
        "yeast": yeast_cost,
        "packaging": packaging_cost,
    }
    return total_cost, cost_per_barrel, breakdown


def recommended_price(cost_per_barrel: float, margin_percent: float) -> float:
    """Recommended selling price per barrel for a given margin (%) ."""
    return cost_per_barrel * (1 + margin_percent / 100.0)


def run_sample():
    """Run a representative sample batch with no user input required."""
    print("=" * 62)
    print("  Craft Brewery Batch Cost Calculator")
    print("  Inspired by: tfrayner/beerfestdb beer price calculator")
    print("  GitHub: https://github.com/tfrayner/beerfestdb")
    print("=" * 62)
    print("\n--- Sample batch (no manual input) ---\n")

    grain_cost_per_lb, grain_lbs = 5.50, 1200
    hops_cost_per_oz, hops_oz = 3.00, 40
    yeast_cost_per_unit, yeast_units = 12.00, 2
    packaging_cost_per_unit, packaging_units = 1.50, 500
    batch_size_barrels = 40.0
    margin_percent = 60.0

    total_cost, cost_per_barrel, breakdown = calculate_batch_cost(
        grain_cost_per_lb,
        grain_lbs,
        hops_cost_per_oz,
        hops_oz,
        yeast_cost_per_unit,
        yeast_units,
        packaging_cost_per_unit,
        packaging_units,
        batch_size_barrels,
    )
    price_per_barrel = recommended_price(cost_per_barrel, margin_percent)

    print("  Ingredient cost breakdown:")
    print(f"    Grain     (5.50 $/lb x 1200 lb):   ${breakdown['grain']:.2f}")
    print(f"    Hops      (3.00 $/oz x 40 oz):     ${breakdown['hops']:.2f}")
    print(f"    Yeast     (12.00 $/unit x 2 units): ${breakdown['yeast']:.2f}")
    print(f"    Packaging (1.50 $/unit x 500 units): ${breakdown['packaging']:.2f}")
    print(f"  Total batch cost:        ${total_cost:.2f}")
    print(f"  Batch size:              {batch_size_barrels:.1f} bbl")
    print(f"  Cost per barrel:         ${cost_per_barrel:.2f}")
    print(f"  Desired margin:          {margin_percent:.1f}%")
    print(f"  Recommended price/bbl:   ${price_per_barrel:.2f}")

    # Validation assertions
    assert breakdown["grain"] == 6600.0
    assert breakdown["hops"] == 120.0
    assert breakdown["yeast"] == 24.0
    assert breakdown["packaging"] == 750.0
    assert total_cost == 7494.0
    assert abs(cost_per_barrel - 187.35) < 0.001
    assert abs(price_per_barrel - 299.76) < 0.001
    print("\n  [OK] Sample executed successfully; all assertions passed.\n")
    return total_cost, cost_per_barrel, price_per_barrel


def main():
    if len(sys.argv) > 1 and sys.argv[1] == "--sample":
        run_sample()
        return

    print("=" * 62)
    print("  Craft Brewery Batch Cost Calculator")
    print("  Inspired by: tfrayner/beerfestdb beer price calculator")
    print("  GitHub: https://github.com/tfrayner/beerfestdb")
    print("=" * 62)
    print()

    # Ingredient cost inputs
    print("--- Ingredient Cost Inputs ---")
    grain_cost_per_lb = get_float_input("Grain cost ($/lb)", 5.50)
    grain_lbs = get_float_input("Total grain (lbs)", 1200)
    hops_cost_per_oz = get_float_input("Hops cost ($/oz)", 3.00)
    hops_oz = get_float_input("Total hops (oz)", 40)
    yeast_cost_per_unit = get_float_input("Yeast cost ($/unit)", 12.00)
    yeast_units = get_float_input("Total yeast units", 2)
    packaging_cost_per_unit = get_float_input("Packaging cost ($/unit)", 1.50)
    packaging_units = get_float_input("Total packaging units", 500)

    # Batch size
    print()
    print("--- Batch Size ---")
    batch_size_barrels = get_float_input("Batch size (barrels)", 40)

    # Margin
    print()
    print("--- Margin ---")
    margin_percent = get_float_input("Desired margin (%)", 60)

    total_cost, cost_per_barrel, breakdown = calculate_batch_cost(
        grain_cost_per_lb,
        grain_lbs,
        hops_cost_per_oz,
        hops_oz,
        yeast_cost_per_unit,
        yeast_units,
        packaging_cost_per_unit,
        packaging_units,
        batch_size_barrels,
    )
    price_per_barrel = recommended_price(cost_per_barrel, margin_percent)

    print()
    print("=" * 62)
    print("  RESULTS")
    print("=" * 62)
    print("  Ingredient cost breakdown:")
    print(f"    Grain:     ${breakdown['grain']:,.2f}")
    print(f"    Hops:      ${breakdown['hops']:,.2f}")
    print(f"    Yeast:     ${breakdown['yeast']:,.2f}")
    print(f"    Packaging: ${breakdown['packaging']:,.2f}")
    print(f"  Total batch cost:    ${total_cost:,.2f}")
    print(f"  Batch size:          {batch_size_barrels:.1f} bbl")
    print(f"  Cost per barrel:     ${cost_per_barrel:,.2f}")
    print(f"  Desired margin:      {margin_percent:.1f}%")
    print(f"  Recommended price/bbl:${price_per_barrel:,.2f}")
    print("=" * 62)


if __name__ == "__main__":
    main()
