#!/usr/bin/env bash
set -euo pipefail

ROOT="${1:-/home/partical/TCAD/OvO/LGAD_V4_3_N590_OperatingScan}"
STATUS="$ROOT/05_export_status.tsv"
VIDS="$ROOT/00_input/silicon_vertex_ids_v3.txt"

mkdir -p "$ROOT/04_exports"
printf 'temperature_K\tbias_V\tstatus\tcsv\n' > "$STATUS"

for temperature in 253 300; do
  for voltage in 450 470 490 510 530 550 570 590 610; do
    tag="T${temperature}_V${voltage}"
    prefix="n590_${tag}"
    case_dir="$ROOT/01_cases/$tag"
    tdr="$case_dir/${prefix}_des.tdr"
    export_dir="$ROOT/04_exports/$tag"
    csv="$export_dir/${prefix}_map.csv"
    summary="$export_dir/${prefix}_summary.txt"
    mkdir -p "$export_dir"

    if [[ ! -s "$tdr" ]]; then
      printf '%s\t%s\tmissing_tdr\t%s\n' "$temperature" "$voltage" "$csv" >> "$STATUS"
      continue
    fi
    if [[ -s "$csv" ]]; then
      printf '%s\t%s\treused\t%s\n' "$temperature" "$voltage" "$csv" >> "$STATUS"
      continue
    fi

    cp -p "$tdr" "$export_dir/${prefix}.tdr"
    (
      cd "$export_dir"
      tdx -dd "${prefix}.tdr" > "${prefix}_tdx.log" 2>&1
    )
    python3 "$ROOT/03_scripts/export_case_map.py" \
      --dat "$export_dir/${prefix}.dat" \
      --grd "$export_dir/${prefix}.grd" \
      --vertex-ids "$VIDS" \
      --output "$csv" \
      --summary "$summary" \
      --temperature "$temperature" \
      --bias "$voltage"
    printf '%s\t%s\tcomplete\t%s\n' "$temperature" "$voltage" "$csv" >> "$STATUS"
  done
done

echo "export status: $STATUS"

