.DEFAULT_GOAL := help

QUARTO ?= quarto
PYTHON ?= $(shell pyenv which python 2>/dev/null || command -v python3)
BOOK_DIR := ru/book

.PHONY: help check-env sync-shared site book book-html book-pdf book-epub \
	clean clean-site clean-book

help: ## Показать цели сборки
	@printf '%s\n' 'Доступные цели:'
	@awk 'BEGIN {FS = ":.*## "}; /^[a-zA-Z0-9_.-]+:.*## / {printf "  %-18s %s\n", $$1, $$2}' $(MAKEFILE_LIST)

check-env: ## Проверить Quarto и Python
	@command -v "$(QUARTO)" >/dev/null 2>&1 || { echo "Не найден quarto: $(QUARTO)"; exit 1; }
	@if ! command -v "$(PYTHON)" >/dev/null 2>&1 && [ ! -x "$(PYTHON)" ]; then \
	  echo "Не найден Python: $(PYTHON)"; exit 1; \
	fi

sync-shared: check-env ## Обновить общие RevealJS- и книжные ресурсы
	$(PYTHON) scripts/sync_shared_assets.py

site: check-env ## Собрать сайт, курс лекций и HTML-книгу в _site
	rm -rf _site
	$(QUARTO) render
	$(QUARTO) render $(BOOK_DIR) --to html
	find _site -type f -name '*.qmd' -delete
	rm -rf _site/ru/slides/assets/radial-signals/__pycache__
	rm -f _site/ru/slides/assets/radial-signals/generate_figures.py
	test -s _site/index.html
	test -s _site/ru/course.html
	test -s _site/ru/book/index.html

book: check-env ## Собрать книгу во всех форматах
	$(QUARTO) render $(BOOK_DIR)

book-html: check-env ## Собрать HTML-книгу
	$(QUARTO) render $(BOOK_DIR) --to html

book-pdf: check-env ## Собрать PDF-книгу
	$(QUARTO) render $(BOOK_DIR) --to pdf

book-epub: check-env ## Собрать EPUB-книгу
	$(QUARTO) render $(BOOK_DIR) --to epub

clean: clean-site clean-book ## Удалить воспроизводимые результаты сборки

clean-site: ## Очистить общий сайт
	rm -rf _site .quarto

clean-book: ## Очистить локальные кэши книги
	rm -rf $(BOOK_DIR)/_book $(BOOK_DIR)/.quarto
