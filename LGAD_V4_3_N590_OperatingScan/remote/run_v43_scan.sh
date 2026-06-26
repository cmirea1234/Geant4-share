#!/usr/bin/env bash
set -euo pipefail

ROOT="${1:-/home/partical/TCAD/OvO/LGAD_V4_3_N590_OperatingScan}"
TEMPLATE="$ROOT/00_input/pp590_des_template.cmd"
GRID="$ROOT/00_input/n23_590_fps.tdr"
STATUS="$ROOT/02_status/scan_status.tsv"

TEMPERATURES=(253 300)
VOLTAGES=(450 470 490 510 530 550 570 590 610)

mkdir -p "$ROOT/01_cases" "$ROOT/02_status"
printf 'temperature_K\tbias_V\tstatus\ttdr\tlog\n' > "$STATUS"

for temperature in "${TEMPERATURES[@]}"; do
  for voltage in "${VOLTAGES[@]}"; do
    tag="T${temperature}_V${voltage}"
    case_dir="$ROOT/01_cases/$tag"
    prefix="n590_${tag}"
    mkdir -p "$case_dir"
    cp -p "$GRID" "$case_dir/n23_590_fps.tdr"

    python3 "$ROOT/03_scripts/render_case.py" \
      --template "$TEMPLATE" \
      --output "$case_dir/${prefix}_des.cmd" \
      --temperature "$temperature" \
      --voltage "$voltage" \
      --prefix "$prefix"

    if [[ -s "$case_dir/${prefix}_des.tdr" ]] && \
       grep -q 'simulation finished' "$case_dir/${prefix}_des.out_des.log" 2>/dev/null; then
      printf '%s\t%s\treused\t%s\t%s\n' \
        "$temperature" "$voltage" \
        "$case_dir/${prefix}_des.tdr" "$case_dir/${prefix}_des.out_des.log" \
        >> "$STATUS"
      continue
    fi

    if (
      cd "$case_dir"
      sdevice "${prefix}_des.cmd" > "${prefix}_stdout.log" 2>&1
    ); then
      command_state="zero_exit"
    else
      command_state="nonzero_exit"
    fi

    if [[ -s "$case_dir/${prefix}_des.tdr" ]] && \
       grep -q 'simulation finished' "$case_dir/${prefix}_des.out_des.log"; then
      state="complete"
    else
      state="failed_${command_state}"
    fi
    printf '%s\t%s\t%s\t%s\t%s\n' \
      "$temperature" "$voltage" "$state" \
      "$case_dir/${prefix}_des.tdr" "$case_dir/${prefix}_des.out_des.log" \
      >> "$STATUS"
  done
done

echo "scan status: $STATUS"
