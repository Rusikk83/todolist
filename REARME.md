Проект todolist.

Описание: Планировщик задач пользователей доступен через WEB-интерфейс и телеграмм-бота.

Стек: python 3.10, Django, PostgresSQL

Как запустить: 
1) Скопировать в репозиторий на GitHub
2) Внести в secrets репозитория значения для переменных в файле _ci.env 
3) Внести в secrets репозитория значения переменных в файле action.yml с учетными данные сервера
4) Выполнить push в репозиторий. Actions запустится автоматически и выполнит развертывание и запуск docker контейнеров с приложением

Реализованные функции:
- Регистрация пользователей
- Регистрация/изменение пользователей через ВК
- Создание/изменений категорий целей
- Создание/изменение целей
- Изменение статуса целей
- Создание/изменение комментариев целей
- Шаринг доски
- Просмотр и создание целей через телеграмм-бота