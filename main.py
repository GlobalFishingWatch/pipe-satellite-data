#! /usr/bin/env python
import sys
import logging

from pipe_satellite_data.process.sat_locations import main as run_satellite_data

logging.basicConfig(level=logging.INFO)

SUBCOMMANDS = {"satellite_data_daily": run_satellite_data}

if __name__ == "__main__":
    logging.info("Running %s", sys.argv)

    if len(sys.argv) < 2:
        logging.info(
            "No subcommand specified. Run pipeline [SUBCOMMAND], where subcommand is one of %s",
            SUBCOMMANDS.keys(),
        )
        exit(1)

    subcommand = sys.argv[1]
    subcommand_args = sys.argv[2:]

    SUBCOMMANDS[subcommand](subcommand_args)
