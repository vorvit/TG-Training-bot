## Telegram-бот для расчёта нормы воды, калорий и трекинга активности.
Бот написан на aiogram-3.17.0.<br>Данные записываются в базу данных, используется библиотека aiosqlite-0.20.0.<br>Для расчётов в формулах используется температура наружного воздуха, получаемая по API openweathermap.org.<br>Для получения калорийности продуктов выполняются запросы на API trackapi.nutritionix.com, используется библиотека aiohttp-3.11.11.<br>Реализован перевод текста запроса пользователя с русского на английский язык, при помощи библиотеки translate-3.6.1.<br>Заполненный профиль пользователя сохраняется в базе данных и при повторном входе загружается из неё.<br>Данные логирования калорий и воды обнуляются каждый день.<br>При вызове команды /check_progress выводится отчёт о полученных калориях и воде, а также информация о дневных нормах. Также строятся графики с информацией о прогрессе.<br>
### Команда /set_profile

![Команда /set_profile](content/1_set_profile.gif)

### Редактирование нормы пользователем

![Команда edit_norm](content/2_edit_norm.gif)

### Команда /show_profile

![Команда /show_profile](content/3_show_profile.gif)

### Команда /log_water

![Команда /log_water](content/4_log_water.gif)

### Команда /log_food

![Команда /log_food](content/5_log_food.gif)

### Команда /log_workout

![Команда /log_workout](content/6_log_workout.gif)

### Команда /check_progress

![Команда /check_progress](content/7_check_progress.gif)

### Пересчёт прогресса

![Команда /check_progress](content/8_check_progress2.gif)

### Пересчёт прогресса в профиле

![Команда /show_profile](content/9_show_profile2.gif)

### Редактирование профиля

![Команда /edit_profile](content/10_edit_profile.gif)

### Запуск бота на render.com

![Deploy](content/Deploy.png)

### Работа бота на render.com

![Work](content/Logs.png)
