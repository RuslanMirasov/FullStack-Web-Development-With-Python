# Шаг 7. Документация Sphinx — проверка

### 7.1. Открыть документацию

```bash
explorer.exe "docs\_build\html\index.html"
```

### 7.2. Пересобрать после изменения docstrings

```bash
source venv/Scripts/activate
sphinx-build -M html docs docs/_build
```
