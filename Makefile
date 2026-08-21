.PHONY: site

site:
	quarto render
	find _site -type f -name '*.qmd' -delete
	rm -rf _site/ru/slides/assets/radial-signals/__pycache__
	rm -f _site/ru/slides/assets/radial-signals/generate_figures.py
