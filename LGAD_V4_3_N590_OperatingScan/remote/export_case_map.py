#!/usr/bin/env python3
"""Export one V4.3 DF-ISE case to a Silicon_1 vertex CSV (Python 3.6)."""

import argparse
import csv
import math
from pathlib import Path
import re


NUMBER = re.compile(r"[-+]?(?:\d+\.\d*|\.\d+|\d+)(?:[eE][-+]?\d+)?")


def numbers(text):
    return [float(value) for value in NUMBER.findall(text)]


def read_vertices(path):
    vertices = []
    expected = None
    reading = False
    for line in Path(path).read_text(errors="replace").splitlines():
        if not reading:
            match = re.search(r"Vertices\s*\((\d+)\)", line)
            if match:
                expected = int(match.group(1))
                reading = True
            continue
        values = numbers(line)
        if len(values) == 2:
            vertices.append((values[0], values[1]))
        if len(vertices) == expected:
            return vertices
    raise RuntimeError("Vertices block could not be read")


def dataset_blocks(text, name):
    pattern = re.compile(
        r'Dataset \("{}"\)\s*\{{(.*?)\n\s*\}}\s*\n\s*\}}'.format(
            re.escape(name)
        ),
        re.DOTALL,
    )
    for block in pattern.findall(text):
        value_match = re.search(
            r"Values\s*\((\d+)\)\s*\{(.*)", block, re.DOTALL
        )
        if value_match:
            yield int(value_match.group(1)), numbers(value_match.group(2))


def scalar_dataset(text, name, count):
    for expected, values in dataset_blocks(text, name):
        if expected == count and len(values) == count:
            return values
    raise RuntimeError("scalar dataset not found: {} ({})".format(name, count))


def vector_dataset(text, name, count):
    for expected, values in dataset_blocks(text, name):
        if expected == 2 * count and len(values) == 2 * count:
            return values[0::2], values[1::2]
    raise RuntimeError("vector dataset not found: {} ({})".format(name, count))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--dat", required=True)
    parser.add_argument("--grd", required=True)
    parser.add_argument("--vertex-ids", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--summary", required=True)
    parser.add_argument("--temperature", required=True, type=float)
    parser.add_argument("--bias", required=True, type=float)
    args = parser.parse_args()

    text = Path(args.dat).read_text(errors="replace")
    vertex_ids = [int(value) for value in Path(args.vertex_ids).read_text().split()]
    count = len(vertex_ids)
    vertices = read_vertices(args.grd)

    scalar_names = {
        "potential_V": "ElectrostaticPotential",
        "lattice_temperature_K": "LatticeTemperature",
        "electric_field_mag_V_per_cm": "ElectricField",
        "space_charge_cm-3": "SpaceCharge",
        "net_doping_cm-3": "DopingConcentration",
        "donor_cm-3": "DonorConcentration",
        "acceptor_cm-3": "AcceptorConcentration",
        "eMobility_cm2_per_Vs": "eMobility",
        "hMobility_cm2_per_Vs": "hMobility",
        "eVelocity_cm_per_s": "eVelocity",
        "hVelocity_cm_per_s": "hVelocity",
        "srh_recombination_cm-3_s-1": "srhRecombination",
        "auger_recombination_cm-3_s-1": "AugerRecombination",
        "avalanche_generation_cm-3_s-1": "ImpactIonization",
        "eIonIntegral": "eIonIntegral",
        "hIonIntegral": "hIonIntegral",
        "eAlphaAvalanche_cm-1": "eAlphaAvalanche",
        "hAlphaAvalanche_cm-1": "hAlphaAvalanche",
    }
    fields = {
        output_name: scalar_dataset(text, dataset_name, count)
        for output_name, dataset_name in scalar_names.items()
    }
    ex, ey = vector_dataset(text, "ElectricField", count)

    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = [
        "vertex_id", "x_um", "depth_um", "temperature_K", "bias_V",
        "Ex_V_per_cm", "Ey_or_Ez_V_per_cm",
    ] + list(fields.keys())
    with output.open("w", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=fieldnames)
        writer.writeheader()
        for index, vertex_id in enumerate(vertex_ids):
            x_um, depth_um = vertices[vertex_id]
            row = {
                "vertex_id": vertex_id,
                "x_um": x_um,
                "depth_um": depth_um,
                "temperature_K": args.temperature,
                "bias_V": -abs(args.bias),
                "Ex_V_per_cm": ex[index],
                "Ey_or_Ez_V_per_cm": ey[index],
            }
            for name, values in fields.items():
                row[name] = values[index]
            writer.writerow(row)

    field = fields["electric_field_mag_V_per_cm"]
    e_alpha = fields["eAlphaAvalanche_cm-1"]
    h_alpha = fields["hAlphaAvalanche_cm-1"]
    vector_error = max(
        abs(magnitude - math.hypot(x_value, y_value))
        for magnitude, x_value, y_value in zip(field, ex, ey)
    )
    summary_lines = [
        "V4.3 n590 operating-map export",
        "rows = {}".format(count),
        "temperature_K = {}".format(args.temperature),
        "bias_V = {}".format(-abs(args.bias)),
        "field_min_V_per_cm = {:.17g}".format(min(field)),
        "field_max_V_per_cm = {:.17g}".format(max(field)),
        "eAlpha_max_cm-1 = {:.17g}".format(max(e_alpha)),
        "hAlpha_max_cm-1 = {:.17g}".format(max(h_alpha)),
        "electric_field_vector_max_abs_error = {:.17g}".format(vector_error),
    ]
    Path(args.summary).write_text("\n".join(summary_lines) + "\n")
    print(output)


if __name__ == "__main__":
    main()

