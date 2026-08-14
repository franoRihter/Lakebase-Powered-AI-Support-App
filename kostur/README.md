# Databricks To-Do List App

A minimal Flask + Lakebase (managed Postgres) to-do list, structured to run
as a Databricks App.

## Files
- `app.py` – Flask app with CRUD routes (list, add, toggle done, delete)
- `templates/index.html` – single-page UI, no JS framework, just forms
- `requirements.txt` – flask + psycopg2-binary
- `app.yaml` – Databricks Apps deployment manifest (env vars pulled from secrets)

## Run locally

1. Create a Postgres database (or use a Lakebase instance) and note its
   host/port/db/user/password.
2. Export connection env vars:
   ```bash
   export PGHOST=your-lakebase-host
   export PGPORT=5432
   export PGDATABASE=your-db
   export PGUSER=your-user
   export PGPASSWORD=your-token-or-password
   export PGSSLMODE=require
   ```
3. Install deps and run:
   ```bash
   pip install -r requirements.txt
   python app.py
   ```
4. Visit `http://localhost:8000`. The `todos` table is created automatically
   on first run.

## Deploy as a Databricks App

1. In your Databricks workspace, go to **Apps** → **Create App** → choose a
   custom app and point it at this folder (or push it to a Git repo synced
   to your workspace).
2. Create secrets for the Lakebase connection details (`lakebase-host`,
   `lakebase-database`, `lakebase-user`, `lakebase-password`) referenced in
   `app.yaml`. If you're using OAuth token auth against Lakebase instead of
   a static password, generate the token via the Databricks SDK/CLI and
   store it as the `lakebase-password` secret (tokens expire, so you'd want
   a refresh job for anything beyond a demo).
3. Deploy — Databricks Apps will install `requirements.txt` and run the
   command in `app.yaml`.

## Notes / next steps
This is intentionally bare-bones. Natural extensions if you want to build
it out further:
- Auth (Databricks Apps can front this with workspace SSO)
- Due dates / priorities / tags as extra columns
- Swap the raw SQL for SQLAlchemy if the schema grows
- Token refresh logic if you're using OAuth against Lakebase rather than a
  static password
