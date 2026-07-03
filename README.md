# AskMe

Форум вопросов и ответов на Django.

## Стек

- Python
- Django
- PostgreSQL
- Nginx

## Реализовано

- публикация вопросов и ответов
- хранение данных в PostgreSQL
- раздача статических файлов через Nginx

## Запуск проекта

```bash
git clone <repo_url>
cd <project_dir>
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```
