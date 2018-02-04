#! /usr/bin/env bash

set -euo pipefail

main() {
    PYTHONPATH="occ" pylint occ --errors-only
}

main "$@"
