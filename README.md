# Cafes for Nerds API

A REST API built with Flask and SQLAlchemy for finding work-friendly cafes.

📖 **Documentation:** https://documenter.getpostman.com/view/59805123/2sBYPv4tHZ

## Endpoints

| Method | Route | Purpose |
| --- | --- | --- |
| GET | `/random` | A random cafe |
| GET | `/all` | Every cafe, sorted by name |
| GET | `/search?loc=<area>` | Cafes in one area |
| POST | `/suggest` | Add a cafe (form data) |
| PATCH | `/update-price/<cafe_id>` | Update a cafe's coffee price |
| DELETE | `/report-closed/<cafe_id>?api-key=<key>` | Remove a closed cafe (API key required) |

## Run locally

```bash
pip install -r requirements.txt
```

Create a `.env` file with `VERIFIER=<your-api-key>`, then:

```bash
flask --app main run
```

The cafe database (`instance/cafes.db`) isn't included in this repo.