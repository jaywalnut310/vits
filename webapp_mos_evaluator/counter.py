#!/usr/bin/env python3
"""
compute_averages.py

Reads files in a folder (JSON, NDJSON, or CSV), extracts records with a 'sampleId'
and numeric metrics: intelligibility, artifacts, overall, naturalness, prosody.

If a sampleId appears multiple times (within or across files), the script
first averages the metrics for that sampleId, then computes the final average
for each metric across unique sampleIds.

Usage:
    python compute_averages.py /path/to/folder --out averages.json
"""

import argparse
import csv
import json
from collections import defaultdict
from pathlib import Path
from statistics import mean
from typing import Dict, Iterable, List, Optional

METRICS = ["intelligibility", "artifacts", "overall", "naturalness", "prosody"]
SAMPLE_KEY = "sampleId"  # adjust if your files use a different field name


def try_parse_json(text: str):
    return json.loads(text)


def normalize_record(rec: Dict) -> Optional[Dict]:
    """
    From an input record (dict), return a normalized dict that contains:
      - sampleId
      - numeric values for the metrics (if present)
    If no sampleId present, return None.
    """
    # Try common keys for sample id
    sid = rec.get(SAMPLE_KEY) or rec.get("sample_id") or rec.get("id")
    if sid is None:
        return None

    out = {"sampleId": sid}
    has_any_metric = False
    for m in METRICS:
        # allow keys with different cases
        val = None
        if m in rec:
            val = rec[m]
        else:
            for k in rec["scores"].keys():
                if k.lower() == m.lower():
                    val = rec["scores"][k]
                    break
        if val is None or val == "":
            # missing metric for this record -> skip including it
            continue
        # try to convert to float
        try:
            out[m] = float(val)
            has_any_metric = True
        except Exception:
            # if value cannot be converted, ignore it
            continue

    # If record contains no metrics, we still might want to keep sampleId? Skip it.
    if not has_any_metric:
        return None
    return out


def parse_file(path: Path) -> Iterable[Dict]:
    text = path.read_text(encoding="utf-8")
    # Try JSON (list or dict)
    try:
        data = try_parse_json(text)
        if isinstance(data, dict):
            # possible shapes:
            #  - a single record with sampleId & metrics
            #  - a dict with a key that contains a list of records, e.g., {"results": [...]}
            # try to find a list inside
            found_list = False
            for v in data.values():
                if isinstance(v, list) and v and isinstance(v[0], dict):
                    found_list = True
                    for rec in v:
                        yield rec
                    break
            if not found_list:
                yield data
        elif isinstance(data, list):
            for rec in data:
                yield rec
        else:
            # unexpected JSON shape, skip
            return
        return
    except Exception:
        # Not a plain JSON file; try NDJSON (line-separated JSON)
        pass

    # Try NDJSON
    try:
        for rec in parse_ndjson_lines(text):
            yield rec
        return
    except Exception:
        pass

    # Try CSV
    try:
        for rec in parse_csv(path):
            yield rec
        return
    except Exception:
        pass

    # If we get here, unreadable file type; silently skip
    return


def collect_records(folder: Path) -> Dict[str, List[Dict]]:
    files = list(folder.iterdir())
    samples = defaultdict(list)  # sampleId -> list of normalized records
    print(f"Total evaluators: {len(files)}")
    for f in files:
        if f.is_dir():
            continue
        # only try a set of reasonable extensions (you can expand these)
        if f.suffix.lower() not in {".json", ".ndjson", ".csv", ".txt"}:
            # still try to parse if not recognized? skip for speed.
            continue
        for raw in parse_file(f):
            nr = normalize_record(raw)
            if nr is None:
                continue
            sid = nr["sampleId"]
            # keep only metrics keys (not parse artifacts)
            samples[sid].append({k: v for k, v in nr.items() if k in METRICS})
    return samples


def compute_averages(samples: Dict[str, List[Dict]]):
    # First, compute per-sample averages (if sample has multiple records)
    per_sample_avg = {}
    for sid, recs in samples.items():
        # for each metric, collect available values across recs
        metric_vals = {m: [] for m in METRICS}
        for r in recs:
            for m in METRICS:
                if m in r:
                    metric_vals[m].append(r[m])
        # compute means for metrics that have at least one value
        averaged = {}
        for m, vals in metric_vals.items():
            if vals:
                averaged[m] = mean(vals)
        if averaged:
            per_sample_avg[sid] = averaged

    # Now compute overall averages across unique sampleIds (only samples that had any metric)
    overall = {}
    for m in METRICS:
        vals = []
        for sid, avg_dict in per_sample_avg.items():
            if m in avg_dict:
                vals.append(avg_dict[m])
        if vals:
            overall[m] = mean(vals)
        else:
            overall[m] = None  # no data for this metric

    return {
        "per_sample": per_sample_avg,
        "overall": overall,
        "num_unique_samples": len(per_sample_avg),
    }


def main():

    folder = Path("/mnt/localshare/vits_analysis/")
    if not folder.exists() or not folder.is_dir():
        raise SystemExit(f"Folder {folder} does not exist or is not a directory")

    samples = collect_records(folder)
    if not samples:
        raise SystemExit("No valid records found in the provided folder.")

    results = compute_averages(samples)

    # Print summary
    print("Number of unique samples found:", results["num_unique_samples"])
    print("Overall averages across unique sampleIds:")
    for m in METRICS:
        v = results["overall"].get(m)
        if v is None:
            print(f"  {m}: (no data)")
        else:
            print(f"  {m}: {v:.4f}")


if __name__ == "__main__":
    main()
