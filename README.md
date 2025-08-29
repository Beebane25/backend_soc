# Mini SOC Dashboard — Backend (Django REST API)

**Ringkasan singkat**
Repo ini berisi **backend** untuk proyek capstone *Mini SOC Dashboard* — sebuah **Django REST API** yang menyajikan data log keamanan (dummy → bisa dihubungkan ke agent nyata) untuk dikonsumsi oleh frontend (React/Next.js) yang dideploy terpisah. README ini ditulis khusus sebagai halaman GitHub untuk bagian *backend* (penjelasan, setup, dan deploy).

---

# Tujuan Proyek

* Menyediakan API yang menyajikan security logs (login fail/success, brute force, port scan, malware, dll.)
* Menyediakan endpoint statistik ringkas (summary) untuk dashboard (chart & card).
* Mudah di-deploy (Railway/Heroku/Render) dan mudah dikoneksikan ke frontend (Netlify/Vercel).
* Struktur rapi untuk presentasi capstone (dokumentasi + instruksi reproduce).

---

# Fitur Utama

* Model `Log` untuk menyimpan event keamanan (timestamp, event\_type, source\_ip, severity, description).
* CRUD API untuk logs (list, retrieve, create, update, delete) via Django REST Framework (DRF).
* Endpoint statistik: jumlah per tipe event (contoh: `/api/stats/`).
* Support browsable API (DRF) + handling static assets production (WhiteNoise).
* Seed script / fixtures untuk generate dummy data (untuk demo & presentasi).
* Instruksi deploy ke Railway/Heroku (Gunicorn + collectstatic + Whitenoise).

---

# Arsitektur (singkat)

```
User (Browser)  <--->  Frontend (React/Vercel)  <--fetch-->  Django REST API (Railway/Heroku)
                                                          |
                                                          +--> Database (Postgres / SQLite)
```

---

# Struktur Repo (direkomendasikan)

```
soc_backend/
├─ logs/                  # Django app untuk log
│  ├─ migrations/
│  ├─ models.py
│  ├─ serializers.py
│  ├─ views.py
│  └─ urls.py
├─ soc_backend/           # project settings
│  ├─ settings.py
│  ├─ urls.py
│  └─ wsgi.py
├─ requirements.txt
├─ Procfile               # (heroku) gunicorn soc_backend.wsgi:application
├─ runtime.txt            # (opsional) python-3.x
├─ manage.py
└─ README.md
```

---

# Model (contoh)

`logs/models.py`

```python
from django.db import models

class Log(models.Model):
    EVENT_TYPES = [
        ("LOGIN_FAIL", "Login Failed"),
        ("LOGIN_SUCCESS", "Login Success"),
        ("BRUTE_FORCE", "Brute Force Attempt"),
        ("PORT_SCAN", "Port Scan Detected"),
        ("MALWARE", "Malware Alert"),
    ]
    SEVERITY_LEVELS = [
        ("LOW", "Low"), ("MEDIUM", "Medium"),
        ("HIGH", "High"), ("CRITICAL", "Critical"),
    ]

    timestamp = models.DateTimeField(auto_now_add=True)
    event_type = models.CharField(max_length=50, choices=EVENT_TYPES)
    source_ip = models.GenericIPAddressField()
    severity = models.CharField(max_length=20, choices=SEVERITY_LEVELS)
    description = models.TextField()

    def __str__(self):
        return f"[{self.event_type}] {self.source_ip} - {self.severity}"
```

---

# Endpoint API (example)

* `GET /api/logs/` → list logs (paginated if diaktifkan)
* `POST /api/logs/` → buat log baru
* `GET /api/logs/{id}/` → detail log
* `PUT /api/logs/{id}/` / `PATCH` → update log
* `DELETE /api/logs/{id}/` → hapus log
* `GET /api/stats/` → ringkasan statistik (jumlah per event\_type/severity)

Contoh response `/api/stats/`:

```json
{
  "login_fail": 25,
  "brute_force": 4,
  "port_scan": 8,
  "malware": 2
}
```

---

# Setup Lokal (development)

1. Clone repo:

```bash
git clone <repo-url>
cd soc_backend
```

2. Buat virtualenv & install:

```bash
python -m venv venv
source venv/bin/activate   # Linux/macOS
# venv\Scripts\activate    # Windows
pip install -r requirements.txt
```

3. Update `soc_backend/settings.py`:

   * Tambahkan `rest_framework` dan `logs` ke `INSTALLED_APPS`.
   * Pastikan `ALLOWED_HOSTS = ["*"]` (sementara untuk testing) atau set domain.
4. Migrasi & buat superuser:

```bash
python manage.py makemigrations
python manage.py migrate
python manage.py createsuperuser
```

5. Jalankan server:

```bash
python manage.py runserver
# akses http://127.0.0.1:8000/api/logs/
```

---

# Seed Data (dummy)

Contoh script cepat (manage shell):

```bash
python manage.py shell
```

```python
from logs.models import Log
from faker import Faker
import random
fake = Faker()
events = ["LOGIN_FAIL","LOGIN_SUCCESS","BRUTE_FORCE","PORT_SCAN","MALWARE"]
sevs = ["LOW","MEDIUM","HIGH","CRITICAL"]

for _ in range(100):
    Log.objects.create(
        event_type=random.choice(events),
        source_ip=fake.ipv4(),
        severity=random.choice(sevs),
        description=fake.sentence()
    )
```

Atau gunakan `fixtures/` dan `loaddata`.

---

# Production readiness & Deploy notes

## 1. Requirements

`requirements.txt` minimal:

```
Django>=4.2
djangorestframework
gunicorn
whitenoise
psycopg2-binary   # bila pakai Postgres
Faker             # (opsional, untuk seed)
```

## 2. Static files (DRF browsable UI & static)

* Tambahkan di `settings.py`:

```python
import os
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')

MIDDLEWARE = [
  'django.middleware.security.SecurityMiddleware',
  'whitenoise.middleware.WhiteNoiseMiddleware',
  # ...
]

STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'
```

* Jalankan sebelum deploy (lokal atau di proses build):

```bash
python manage.py collectstatic --noinput
```

WhiteNoise akan serve static assets (DRF css/js) di production.

> Alternatif: jika tidak butuh browsable API UI, nonaktifkan renderer HTML agar hanya JSON:

```python
REST_FRAMEWORK = {
  'DEFAULT_RENDERER_CLASSES': ('rest_framework.renderers.JSONRenderer',)
}
```

## 3. Gunicorn / Start command

Procfile / Railway start command:

```
web: gunicorn soc_backend.wsgi
```

## 4. Environment variables (contoh)

* `SECRET_KEY` (JANGAN commit)
* `DEBUG=False` (production)
* `DATABASE_URL` (Railway/Heroku provide)
* `ALLOWED_HOSTS` (domain)

Gunakan `.env` untuk development (jangan commit).

---

# Deploy cepat ke Railway / Heroku

1. Push repo ke GitHub.
2. Buat project di Railway/Heroku → hubungkan repo.
3. Set Environment Variables (SECRET\_KEY, DEBUG, DATABASE\_URL).
4. Pastikan `requirements.txt`, `Procfile` (Heroku) atau start command (Railway) ada.
5. Pastikan `python manage.py collectstatic --noinput` dijalankan pada proses build/deploy (Railway dapat menjalankan per build command atau gunakan `heroku-postbuild` script).
6. Setelah deploy, ambil base URL API → sisipkan ke frontend `.env` (contoh: `NEXT_PUBLIC_API_URL=https://your-api.up.railway.app/api`).

---

# Testing & Debugging

* Gunakan `curl` atau Postman:

```bash
curl https://your-api.up.railway.app/api/logs/
```

* Cek error static (404 `/static/rest_framework/...`) → berarti `collectstatic`/WhiteNoise belum ter-setup.
* Jika ada `ModuleNotFoundError` di deploy logs → pastikan package ada di `requirements.txt`.

---

# Keamanan & Praktik Baik

* Jangan commit `SECRET_KEY`, `.env`, atau kredensial DB.
* Pakai HTTPS di production.
* Batasi `ALLOWED_HOSTS`.
* Implementasikan autentikasi & RBAC jika akan dipakai klien nyata (JWT / token / Django auth).
* Rate-limiting / monitoring jika API akan menerima log secara real-time.

---

# Integrasi dengan Frontend (Catatan singkat)

* Frontend (React/Next.js) akan memanggil endpoint API di `https://<API_BASE>/api/logs/` dan `.../api/stats/`.
* Pastikan CORS diset (`django-cors-headers`) jika frontend di domain berbeda:

```bash
pip install django-cors-headers
```

dan di `settings.py`:

```python
INSTALLED_APPS += ['corsheaders']
MIDDLEWARE = ['corsheaders.middleware.CorsMiddleware', ...]
CORS_ALLOWED_ORIGINS = [
  "https://your-frontend.vercel.app",
]
```
# Hasil Backend dari SOC Dashboard
🚀 [Buka Backend Mini SOC Dashboard](https://web-production-a113d.up.railway.app/api/)
