
# Delivery Tracker vFinal18 (Modular)

This is a modular FastAPI implementation for Delivery Tracker (vFinal18).
- SQLite for local development (file: `delivery_tracker.db`)
- Manual sample data loader: `python main/sample_data.py`
- Start server: `uvicorn main.main:app --reload --port 8000`
- Swagger: http://127.0.0.1:8000/docs

Structure:
```
main/          - core app (main.py, database, models, schemas, crud, sample_data)
routers/       - one router per entity/table
requirements.txt, Dockerfile, docker-compose.yml, README.md
```

Notes:
- API grouping in Swagger is per-table and minimal (short summaries).
- Archive endpoints exist for tables with `EntityStatus`.
