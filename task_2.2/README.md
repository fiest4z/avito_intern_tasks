# UI-тесты платформы модерации объявлений

## Стек

- Playwright + TypeScript
- Браузер: Chromium

## Быстрый старт

```bash
npm install
npx playwright install chromium
npx playwright test
```

## Структура

```
tests/
  price-filter.spec.ts   # TC-1: Фильтр «Диапазон цен»
  price-sort.spec.ts     # TC-2: Сортировка «По цене»
  category-filter.spec.ts# TC-3: Фильтр «Категория»
  urgent-toggle.spec.ts  # TC-4: Тогл «Только срочные»
  stats-timer.spec.ts    # TC-5: Таймер обновления статистики
  mobile-theme.spec.ts   # TC-6: Переключение темы (мобильная версия)
```

## Результаты

-   10 тестов проходят   — функциональность работает корректно
-   3 теста падают   — обнаружены баги (описаны в [BUGS.md](BUGS.md))

Тест-кейсы описаны в [TESTCASES.md](TESTCASES.md).
