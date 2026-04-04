#!/bin/bash
cd "$(dirname "$0")"

pdflatex -interaction=nonstopmode main.tex
bibtex main
pdflatex -interaction=nonstopmode main.tex
pdflatex -interaction=nonstopmode main.tex

echo ""
echo "Done. Output: main.pdf"
