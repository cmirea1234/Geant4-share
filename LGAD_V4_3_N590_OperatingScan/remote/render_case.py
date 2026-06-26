#!/usr/bin/env python3
"""Render one isolated Sentaurus Device scan case (Python 3.6 compatible)."""

import argparse
from pathlib import Path
import re


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--template", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--temperature", required=True, type=int)
    parser.add_argument("--voltage", required=True, type=int)
    parser.add_argument("--prefix", required=True)
    args = parser.parse_args()

    text = Path(args.template).read_text(errors="replace")
    text = re.sub(r'Current\s*=\s*"[^"]+"',
                  'Current = "{}_IV"'.format(args.prefix), text)
    text = re.sub(r'Plot\s*=\s*"[^"]+"',
                  'Plot = "{}_des.tdr"'.format(args.prefix), text)
    text = re.sub(r'Output\s*=\s*"[^"]+"',
                  'Output = "{}_des.out"'.format(args.prefix), text)
    text = re.sub(r'Temperature\s*=\s*300',
                  'Temperature = {}'.format(args.temperature), text)
    text = re.sub(r'Number_Of_Threads\s*=\s*18',
                  'Number_Of_Threads=1', text)
    text = re.sub(r'Goal\s*\{\s*Name="anode"\s*Voltage=-590\s*\}',
                  'Goal{{Name="anode" Voltage=-{}}}'.format(args.voltage), text)

    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(text)
    print(output)


if __name__ == "__main__":
    main()

