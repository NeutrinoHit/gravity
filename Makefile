.DEFAULT_GOAL := help

QUARTO ?= quarto
PYTHON ?= $(shell pyenv which python 2>/dev/null || command -v python3)
BOOK_DIR := ru/book
BOOK_FILE := gravity-for-experimentalists
MAP_ROOT ?= ../neutrinohit-map
BOOK_RENDER_FLAGS :=
ifeq ($(GITHUB_ACTIONS),true)
# CI prepares TeX packages before rendering; report actual LaTeX errors directly.
BOOK_RENDER_FLAGS += -M latex-auto-install:false
endif

.PHONY: help check-env ci-setup sync-shared check-shared book-media site book \
	book-html book-pdf book-epub clean clean-site clean-book

help: ## Показать цели сборки
	@printf '%s\n' 'Доступные цели:'
	@awk 'BEGIN {FS = ":.*## "}; /^[a-zA-Z0-9_.-]+:.*## / {printf "  %-18s %s\n", $$1, $$2}' $(MAKEFILE_LIST)

check-env: ## Проверить Quarto и Python
	@command -v "$(QUARTO)" >/dev/null 2>&1 || { echo "Не найден quarto: $(QUARTO)"; exit 1; }
	@if ! command -v "$(PYTHON)" >/dev/null 2>&1 && [ ! -x "$(PYTHON)" ]; then \
	  echo "Не найден Python: $(PYTHON)"; exit 1; \
	fi

ci-setup: ## Подготовить TeX для PDF-книги (GitHub Actions или локально)
	@if [ "$(GITHUB_ACTIONS)" = true ]; then \
	  $(QUARTO) install tinytex --no-prompt && \
	  sh scripts/setup_book_tex.sh; \
	elif command -v lualatex >/dev/null 2>&1; then \
	  echo 'LuaLaTeX already installed.'; \
	else \
	  $(QUARTO) install tinytex --no-prompt; \
	fi

sync-shared: check-env ## Обновить общие RevealJS- и книжные ресурсы из neutrinohit-map
	MAP_ROOT="$(MAP_ROOT)" $(PYTHON) scripts/sync_shared_assets.py

check-shared: check-env ## Сравнить локальные общие ресурсы с neutrinohit-map
	MAP_ROOT="$(MAP_ROOT)" $(PYTHON) scripts/sync_shared_assets.py --check

book-media: check-env ## Обновить QR-коды и постеры анимаций книги из каталога neutrinohit-map
	$(PYTHON) $(MAP_ROOT)/scripts/generate_qrcode.py --book gravity \
	  --out-dir $(BOOK_DIR)/assets/qr --fmt png --size 1000 --selfcheck
	mkdir -p $(BOOK_DIR)/assets/animations
	for poster in $(MAP_ROOT)/assets/book-animations/gravity/[0-9][0-9][0-9][0-9].jpg; do \
	  cp "$$poster" $(BOOK_DIR)/assets/animations/; \
	done

site: check-env ## Собрать сайт, курс лекций и книгу (HTML, PDF, EPUB) в _site
	rm -rf _site
	$(QUARTO) render
	$(QUARTO) render $(BOOK_DIR) $(BOOK_RENDER_FLAGS)
	find _site -type f -name '*.qmd' -delete
	rm -rf _site/ru/slides/assets/radial-signals/__pycache__
	rm -f _site/ru/slides/assets/radial-signals/generate_figures.py
	test -s _site/index.html
	test -s _site/ru/course.html
	test -s _site/ru/book/index.html
	test -s _site/ru/book/$(BOOK_FILE).pdf
	test -s _site/ru/book/$(BOOK_FILE).epub

book: check-env ## Собрать книгу во всех форматах
	$(QUARTO) render $(BOOK_DIR) $(BOOK_RENDER_FLAGS)

book-html: check-env ## Собрать HTML-книгу
	$(QUARTO) render $(BOOK_DIR) --to html $(BOOK_RENDER_FLAGS)

book-pdf: check-env ## Собрать PDF-книгу
	$(QUARTO) render $(BOOK_DIR) --to pdf $(BOOK_RENDER_FLAGS)

book-epub: check-env ## Собрать EPUB-книгу
	$(QUARTO) render $(BOOK_DIR) --to epub $(BOOK_RENDER_FLAGS)

clean: clean-site clean-book ## Удалить воспроизводимые результаты сборки

clean-site: ## Очистить общий сайт
	rm -rf _site .quarto

clean-book: ## Очистить локальные кэши книги
	rm -rf $(BOOK_DIR)/_book $(BOOK_DIR)/.quarto
