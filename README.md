# gravity

Материалы будущего курса NeutrinoHit по гравитации и общей теории
относительности.

Планируемый адрес сайта:

```text
https://neutrinohit.github.io/gravity/
```

## Структура

- `index.qmd` — стабильная домашняя страница курса;
- `ru/slides/` — русские HTML-слайды;
- `ru/slides/assets/<lecture-slug>/` — код, рисунки и крупные фрагменты
  конкретной лекции;
- `shared/` — локальные копии общей темы и RevealJS-компонентов NeutrinoHit;
- `analytics/` — общий include аналитики.

Новые лекции добавляются как `ru/slides/<NN_slug>.qmd`. Общие параметры
RevealJS задаются один раз в `ru/slides/_metadata.yml`; в самой лекции должны
оставаться только её метаданные и содержание.

## Сборка

```bash
quarto render
```

Перегенерировать численные рисунки первой лекции:

```bash
python -m pip install -r requirements.txt
python ru/slides/assets/radial-signals/generate_figures.py
```

Обновить общие RevealJS-ресурсы из соседнего `neutrinohit-map`:

```bash
python scripts/sync_shared_assets.py
```
