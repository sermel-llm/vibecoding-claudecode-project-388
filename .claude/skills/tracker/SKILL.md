---
name: tracker
description: Обходит список отслеживаемых товаров, собирает таблицу цен за один прогон и сохраняет её в репозиторий tracker-data. Используй, когда пользователь просит запустить трекер, проверить или обновить цены по списку. Для одной ссылки используй extract-price, а не этот скилл. Позже сюда добавятся сравнение прогонов и уведомления в Telegram.
---

# Tracker

## Список отслеживаемых товаров
1. Crucial CT16G56C46S5
- https://www.nix.ru/autocatalog/memory_modules_Crucial/Crucial-CT16G56C46S5-DDR5-SODIMM-16Gb-PC5-44800-CL46-for-NoteBook_814467.html
- https://www.regard.ru/product/681414/operativnaia-pamiat-16gb-ddr5-5600mhz-crucial-so-dimm-ct16g56c46s5
- https://www.regard.ru/product/766721/operativnaia-pamiat-16gb-ddr5-5600mhz-crucial-so-dimm-ct16g56c46s5-oem
- https://www.kns.ru/product/operativnaya-pamyat-crucial-crucial/
- https://www.oldi.ru/catalog/element/02125551/
- https://www.xcom-shop.ru/crucial_ct16g56c46s5_1139098.html

2. Samsung MZ-VAP1T0BW
- https://www.nix.ru/autocatalog/ssd_samsung/SSD-1-Tb-M2-2280-M-Samsung-9100-PRO-MZ-VAP1T0BW-RTL_891351.html
- https://www.regard.ru/product/737812/nakopitel-ssd-1tb-samsung-9100-pro-mz-vap1t0bw
- https://www.kns.ru/product/ssd-disk-samsung-9100-pro-1tb-mz-vap1t0bw/
- https://www.oldi.ru/catalog/element/02152967/
- https://www.xcom-shop.ru/samsung_9100_pro_1199207.html


## Шаги
1. Запомни дату и время начала прогона по московскому времени (UTC+3).
2. Для каждой ссылки из списка по порядку вызови скилл `extract-price` (через инструмент Skill) — отдельный вызов на каждую ссылку.
   - Не пиши скрипты и не извлекай цены сам, даже если это кажется быстрее: логика извлечения должна оставаться только в `extract-price`, чтобы его улучшения сразу работали в трекере.
   - Если для ссылки пришёл `{"error": ...}`, не останавливайся — запиши ошибку и переходи к следующей ссылке.
3. Когда все ссылки обработаны, собери результаты в одну таблицу.
4. Сохрани прогон в репозиторий через MCP-сервер `github`:
   - репозиторий: `sermel-llm/tracker-data`, ветка `main`;
   - путь: корень репозитория, имя файла `ГГГГ-ММ-ДД.json` по дате начала прогона (например, `2026-11-10.json`);
   - если файл за эту дату уже есть — перезапиши его новым прогоном (предыдущая версия останется в истории коммитов);
   - сообщение коммита: `Run ГГГГ-ММ-ДД ЧЧ:ММ: N links, M errors`;
   - содержимое — JSON такого вида:
     ```json
     {
       "date": "2026-11-10 11:37",
       "rows": [
         {"item": "Crucial CT16G56C46S5", "url": "https://...", "regular_price": 33564, "sale_price": null, "has_credit": true, "error": null}
       ]
     }
     ```
   - в `rows` — строки таблицы в том же порядке; у строки без ошибки `"error": null`, у строки с ошибкой `regular_price`, `sale_price` и `has_credit` — `null`, в `error` — причина.
   - только прямые двойные кавычки `"`, числа без кавычек.
   - Не клонируй репозиторий и не используй git или gh в терминале — только инструмент MCP-сервера `github` для создания или обновления файла.
5. Если сохранить не удалось — всё равно покажи таблицу и сообщи причину ошибки сохранения.

## Выход
Таблица — одна строка на каждую ссылку из списка, в том же порядке:

| date | item | url | regular_price | sale_price | has_credit | error |
|---|---|---|---|---|---|---|
| 2026-11-10 14:30 | Crucial CT16G56C46S5 | https://www.nix.ru/... | 33564 | null | true | |
| 2026-11-10 14:30 | Crucial CT16G56C46S5 | https://www.kns.ru/... | 35987 | 34528 | false | |
| 2026-11-10 14:30 | Samsung MZ-VAP1T0BW | https://www.oldi.ru/... | | | | страница с капчей |

- `date` — дата и время начала прогона в формате `ГГГГ-ММ-ДД ЧЧ:ММ`, одинаковые для всех строк.
- `item` — название товара из заголовка группы в списке, к которой относится ссылка.
- Значения цен бери из ответа `extract-price` без изменений.
- Если была ошибка — поля цен пустые, в `error` краткая причина.
- Количество строк всегда равно количеству ссылок в списке.
- После таблицы — одна строка итога: сколько ссылок обработано и сколько с ошибкой.
- После строки итога — ссылка на сохранённый файл в tracker-data или причина, почему сохранить не удалось.
