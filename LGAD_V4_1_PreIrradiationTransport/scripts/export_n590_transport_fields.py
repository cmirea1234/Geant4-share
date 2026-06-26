#!/usr/bin/env python3
"""Append TCAD mobility/velocity datasets to the existing n590 vertex map.

Run from the n590_LGAD_des_check directory on the TCAD host. The script only
reads the existing DF-ISE/basic CSV inputs and writes into 02_geant4_map.
"""

import csv
from pathlib import Path
import re


DAT = Path("01_extract/dfise/n590_LGAD_des.dat")
BASIC = Path("02_geant4_map/n590_tcad_silicon_vertex_map_590V_basic.csv")
OUT = Path("02_geant4_map/n590_tcad_silicon_transport_590V.csv")
SUMMARY = Path("02_geant4_map/n590_tcad_silicon_transport_590V_summary.txt")

DATASETS = ("eMobility", "hMobility", "eVelocity", "hVelocity")
NUMBER = re.compile(r"[-+]?(?:\d+\.\d*|\.\d+|\d+)(?:[eE][-+]?\d+)?")


def read_scalar_dataset(text, name):
    pattern = re.compile(
        rf'Dataset \("{re.escape(name)}"\)\s*\{{.*?'
        rf'Values \((\d+)\)\s*\{{(.*?)\n\s*\}}\s*\n\s*\}}',
        re.DOTALL,
    )
    match = pattern.search(text)
    if not match:
        raise RuntimeError(f"dataset not found: {name}")
    expected = int(match.group(1))
    values = [float(value) for value in NUMBER.findall(match.group(2))]
    if len(values) != expected:
        raise RuntimeError(
            f"{name} value count mismatch: {len(values)} != {expected}"
        )
    return values


def main():
    text = DAT.read_text(encoding="utf-8", errors="replace")
    fields = {name: read_scalar_dataset(text, name) for name in DATASETS}

    with BASIC.open(newline="") as stream:
        rows = list(csv.DictReader(stream))
    if not rows:
        raise RuntimeError("basic n590 map is empty")
    for name, values in fields.items():
        if len(values) != len(rows):
            raise RuntimeError(f"{name} rows mismatch: {len(values)} != {len(rows)}")

    output_rows = []
    for index, row in enumerate(rows):
        output_rows.append(
            {
                **row,
                "eMobility_cm2_per_Vs": fields["eMobility"][index],
                "hMobility_cm2_per_Vs": fields["hMobility"][index],
                "eVelocity_cm_per_s": fields["eVelocity"][index],
                "hVelocity_cm_per_s": fields["hVelocity"][index],
            }
        )

    OUT.parent.mkdir(parents=True, exist_ok=True)
    with OUT.open("w", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=output_rows[0].keys())
        writer.writeheader()
        writer.writerows(output_rows)

    lines = [
        "TCAD n590 590 V Silicon_1 transport export summary",
        f"rows = {len(rows)}",
        "temperature_K = 300",
        "anode_bias_V = -590",
        "cathode_bias_V = 0",
        "mobility_model = DopingDependence + HighFieldSaturation(GradQuasiFermi) + Enormal(Lombardi)",
        "avalanche_model = Okuto",
    ]
    for name, values in fields.items():
        lines.append(f"{name}_min = {min(values):.17g}")
        lines.append(f"{name}_max = {max(values):.17g}")
    lines.extend(
        [
            "",
            "Caution: eVelocity/hVelocity are DC device-solution quantities.",
            "They are exported for inspection and must not automatically be",
            "treated as test-charge drift speeds without validating their",
            "definition against the Sentaurus model and quasi-Fermi gradients.",
        ]
    )
    SUMMARY.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"wrote {OUT}")
    print(f"wrote {SUMMARY}")


if __name__ == "__main__":
    main()
