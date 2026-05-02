# MoodTunes (backend + mock frontend)

## Run backend
```bash
python -m venv .venv
# Windows: .venv\Scripts\activate
source .venv/bin/activate

pip install -r requirements.txt
python app.py
```

Backend runs at: http://localhost:5000

### Test
```bash
curl http://localhost:5000/api/health
curl -X POST http://localhost:5000/api/emotion-from-text \
  -H "Content-Type: application/json" \
  -d '{"text":"I feel stressed and tired today","song_count":5}'
```

## Run mock frontend
In a second terminal from repo root:
```bash
python -m http.server 5500
```

Open:
http://127.0.0.1:5500/mock-frontend/index.html
