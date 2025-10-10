# skimming_detection/cli.py

import argparse
import sys
from .io_utils import read_catalog, read_config, write_lookup
from .pipeline import run_pipeline
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s %(levelname)s %(module)s %(message)s',
    handlers=[
        logging.FileHandler("audit.log"),
        logging.StreamHandler()
    ]
)

def run_cli(args_dict=None):
    """
    Run the CLI either from command line or programmatically.
    Pass args_dict as a dictionary of arguments (same keys as CLI).
    """
    logging.info("CLI invoked with arguments: %s", args_dict)
    ap = argparse.ArgumentParser()
    ap.add_argument("--catalog", required=True)
    ap.add_argument("--config", default="")
    ap.add_argument("--har-dir", default="")
    ap.add_argument("--rum", default="")
    ap.add_argument("--out", default="risk_scores.csv")
    ap.add_argument("--with-explanations", action="store_true")

    if args_dict is not None:
        # Build a list of CLI-style arguments from the dict
        cli_args = []
        for k, v in args_dict.items():
            if isinstance(v, bool):
                if v:
                    cli_args.append(f"--{k.replace('_','-')}")
            elif v:
                cli_args.extend([f"--{k.replace('_','-')}", str(v)])
        args = ap.parse_args(cli_args)
    else:
        args = ap.parse_args()

    merchants = read_catalog(args.catalog)
    cfg = read_config(args.config)
    if args.har_dir: cfg.har_dir = args.har_dir
    if args.rum: cfg.rum_path = args.rum
    with_expl = bool(args.with_explanations)

    rows = run_pipeline(merchants, cfg, with_expl)
    if not rows:
        print("No merchants processed.", file=sys.stderr)
        sys.exit(2)
    write_lookup(args.out, rows)
    print(f"Wrote {args.out} with {len(rows)} rows.")
    for r in rows[:20]:
        print(",".join(map(str, r)))
    return rows


def main():
    run_cli()

if __name__ == "__main__":
    main()

