# 1. POST /api/tasks/ — Создать задачу
curl -s -X POST http://localhost:8000/api/tasks/ \
  -H "Content-Type: application/json" \
  -d '{"title":"New task","description":"Some description","status":"new","deadline":"2026-06-10T12:00:00Z"}' | python3 -m json.tool

# 2. GET /api/tasks/ — Список всех задач
curl -s http://localhost:8000/api/tasks/ | python3 -m json.tool

# 3a. GET /api/tasks/{id}/ — Конкретная задача (существует)
curl -s http://localhost:8000/api/tasks/1/ | python3 -m json.tool

# 3b. GET /api/tasks/{id}/ — Конкретная задача (не существует → 404)
curl -s http://localhost:8000/api/tasks/999/ | python3 -m json.tool

# 4. GET /api/tasks/stats/ — Статистика
curl -s http://localhost:8000/api/tasks/stats/ | python3 -m json.tool

# 5. Валидация — пустой title (→ 400)
curl -s -X POST http://localhost:8000/api/tasks/ \
  -H "Content-Type: application/json" \
  -d '{"title":"","description":"bad","status":"new","deadline":"2026-06-10T12:00:00Z"}' | python3 -m json.tool