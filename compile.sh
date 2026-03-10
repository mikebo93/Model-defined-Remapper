#!/bin/bash
# Compile MICRO 2026 paper (main.tex)
# Usage: ./compile.sh [clean]

set -e

MAIN="main"

if [ "$1" = "clean" ]; then
    echo "Cleaning build artifacts..."
    rm -f ${MAIN}.aux ${MAIN}.bbl ${MAIN}.blg ${MAIN}.log ${MAIN}.out \
          ${MAIN}.pdf ${MAIN}.fls ${MAIN}.fdb_latexmk ${MAIN}.synctex.gz \
          ${MAIN}.toc ${MAIN}.lof ${MAIN}.lot
    echo "Done."
    exit 0
fi

echo "=== Compiling ${MAIN}.tex ==="

# First pass
pdflatex -interaction=nonstopmode ${MAIN}.tex

# Bibliography
bibtex ${MAIN}

# Second + third pass (resolve references)
pdflatex -interaction=nonstopmode ${MAIN}.tex
pdflatex -interaction=nonstopmode ${MAIN}.tex

echo ""
echo "=== Build complete: ${MAIN}.pdf ==="
