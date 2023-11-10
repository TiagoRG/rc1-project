.PHONY: all compile clean

all: compile clean

compile: main.tex bibliography.bib
	-pdflatex -interaction=nonstopmode main
	-biber main
	-pdflatex -interaction=nonstopmode main
	-pdflatex -interaction=nonstopmode main
	-mv main.pdf ../report.pdf

clean:
	-rm -f *.aux *.blg *.bbl *.toc *.log *.lof *.lot *.log.xml *.bcf *.out *.run.xml *.gz
