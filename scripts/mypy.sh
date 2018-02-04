#! /usr/bin/env bash

set -euo pipefail

main() {
    MYPYPATH="occ" mypy occ --ignore-missing-imports
}

main "$@"
