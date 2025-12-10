# NUAM Project Structure

Clean and organized project structure after cleanup (December 9, 2025).

---

## 📁 Root Directory

```
Nuam-main/
├── 📄 manage.py                          # Django management script
├── 📄 requirements.txt                   # Python dependencies
├── 📄 docker-compose.yml                 # Docker orchestration
├── 📄 Dockerfile                         # Django container definition
├── 📄 startup.sh                         # Initialization script
├── 📄 create_superuser.py                # User creation utility
├── 📄 plantilla_carga_nuam_completa.xlsx # Excel upload template
│
├── 📚 Documentation/
│   ├── README.md                         # Main project documentation
│   ├── CHANGELOG.md                      # Version history and changes
│   ├── QUICK_REFERENCE.md                # Quick commands and URLs
│   └── DELETED_FILES_BACKUP.txt          # List of removed files
│
├── 🐳 Docker Configuration/
│   ├── docker-compose.yml
│   ├── Dockerfile
│   └── nginx/
│       ├── nginx.conf
│       └── conf.d/
│           └── nuam.conf                 # Reverse proxy config
│
├── 💾 Django Apps/
│   ├── accounts/                         # User authentication
│   │   ├── models.py
│   │   ├── views.py
│   │   ├── forms.py
│   │   ├── urls.py
│   │   ├── static/
│   │   │   ├── css/
│   │   │   │   └── main.css             # Main stylesheet
│   │   │   └── js/
│   │   │       ├── main.js               # Core JavaScript
│   │   │       └── currency-converter.js # Currency widget
│   │   ├── templates/
│   │   │   ├── base.html
│   │   │   ├── login.html
│   │   │   ├── home.html
│   │   │   └── accounts/
│   │   │       ├── registro.html
│   │   │       ├── nueva_carga.html
│   │   │       └── ... (other templates)
│   │   └── management/
│   │       └── commands/
│   │
│   ├── api/                              # REST API & business logic
│   │   ├── models.py                     # 5 main models
│   │   ├── views.py                      # API ViewSets
│   │   ├── serializers.py
│   │   ├── urls.py
│   │   ├── excel_handler.py              # Excel processing
│   │   ├── currency_converter.py         # Currency conversion
│   │   ├── kafka_producer.py             # Kafka integration
│   │   └── utils/
│   │
│   ├── kafka_app/                        # Kafka producers/consumers
│   │   ├── producers.py
│   │   ├── consumers.py
│   │   ├── monitoring.py                 # Prometheus metrics
│   │   ├── templates/
│   │   │   └── kafka/
│   │   │       └── dashboard.html
│   │   └── management/
│   │       └── commands/
│   │
│   └── nuam/                             # Django project settings
│       ├── settings.py                   # Main configuration
│       ├── urls.py                       # URL routing
│       ├── wsgi.py
│       ├── service_client.py             # Microservices client
│       ├── currency_client.py            # External API client
│       └── middleware/
│           └── logging_middleware.py
│
├── 🎨 Frontend Services/
│   └── services/
│       ├── currency-service/             # FastAPI currency API
│       │   ├── Dockerfile
│       │   ├── requirements.txt
│       │   └── app/
│       │       └── main.py
│       │
│       └── dashboard-frontend/           # React SPA
│           ├── package.json
│           ├── vite.config.js
│           ├── tailwind.config.js
│           ├── postcss.config.js
│           ├── index.html
│           └── src/
│               ├── main.jsx
│               ├── App.jsx
│               └── index.css
│
├── 📊 Logs/
│   ├── django.log                        # General Django logs
│   ├── api.log                           # API requests/responses
│   ├── kafka.log                         # Kafka events
│   ├── accounts.log                      # User actions
│   ├── carga_excel.log                   # Excel upload logs
│   ├── errors.log                        # Error logs
│   └── security.log                      # Security events
│
├── 📝 Documentation/
│   └── docs/
│       └── FLUJO_PRUEBAS_NUAM.txt        # Testing flow
│
└── 🗄️ Generated (by Django/Docker)/
    ├── staticfiles/                      # Collected static files
    │   ├── css/
    │   ├── js/
    │   ├── admin/
    │   └── ...
    ├── media/                            # User uploads
    └── venv/                             # Python virtual environment (local)
```

---

## 📊 File Count by Type

| Type | Count | Purpose |
|------|-------|---------|
| Python Files | ~50 | Application logic |
| Templates | ~15 | HTML pages |
| Static Files | 3 | CSS & JavaScript |
| Config Files | ~10 | Docker, Nginx, Django |
| Documentation | 4 | README, guides |
| Log Files | 7 | Application logs |
| **Total** | **~90** | Clean structure |

---

## 🎯 Essential Files Only

**Configuration** (6 files):
- `docker-compose.yml` - Container orchestration
- `Dockerfile` - Django container
- `nginx/nginx.conf` - Web server config
- `nginx/conf.d/nuam.conf` - Reverse proxy rules
- `requirements.txt` - Python dependencies
- `nuam/settings.py` - Django settings

**Application Code** (3 main apps):
- `accounts/` - User management (15 files)
- `api/` - Business logic (20 files)
- `kafka_app/` - Event streaming (10 files)

**Frontend Assets** (3 files):
- `accounts/static/css/main.css`
- `accounts/static/js/main.js`
- `accounts/static/js/currency-converter.js`

**Documentation** (4 files):
- `README.md`
- `CHANGELOG.md`
- `QUICK_REFERENCE.md`
- `docs/FLUJO_PRUEBAS_NUAM.txt`

**Utilities** (4 files):
- `manage.py` - Django CLI
- `create_superuser.py` - User creation
- `startup.sh` - Init script
- `plantilla_carga_nuam_completa.xlsx` - Template

---

## 🗑️ Removed During Cleanup

**Unnecessary Files** (18 total):

1. **Old/Backup Files** (3):
   - docker-compose-old.yml
   - cert.pem, key.pem

2. **Test Scripts** (5):
   - test_api.py
   - test_kafka.py
   - mini_test_kafka.py
   - install_local_ssl.sh
   - run_https.py

3. **Redundant Docs** (4):
   - FIXES_APPLIED.md → Merged into CHANGELOG.md
   - CURRENCY_WIDGET_FIX.md → Merged into CHANGELOG.md
   - FRONTEND_MODERNIZATION.md → Merged into CHANGELOG.md
   - TESTING_GUIDE.md → Merged into CHANGELOG.md

4. **Temporary Files**:
   - services/dashboard-frontend/src/Artifact
   - All .DS_Store files
   - All __pycache__/ directories (~40)
   - All .pyc files

**Space Recovered**: ~65KB + ~500KB cache

---

## 📂 Directory Purposes

### `/accounts/`
User authentication, registration, profile management, and HTML templates.

### `/api/`
REST API, data models, serializers, Excel processing, currency conversion.

### `/kafka_app/`
Kafka producers, consumers, event processing, and monitoring dashboard.

### `/nuam/`
Django project settings, URL routing, middleware, and service clients.

### `/services/`
Microservices (FastAPI currency service, React dashboard).

### `/nginx/`
Nginx reverse proxy configuration.

### `/logs/`
Application logs (rotating files).

### `/staticfiles/`
Collected static files served by Nginx (auto-generated).

### `/docs/`
Extended documentation and testing flows.

---

## 🔄 Generated/Auto-Created

These directories are auto-generated and should not be committed to git:

- `staticfiles/` - Generated by `python manage.py collectstatic`
- `__pycache__/` - Python bytecode cache
- `*.pyc` - Compiled Python files
- `venv/` - Virtual environment
- `node_modules/` - NPM packages (in dashboard-frontend)
- `logs/*.log` - Log files (can be committed empty)
- `.DS_Store` - Mac system files

**Git Ignore**: These are already in `.gitignore`

---

## 📝 Documentation Files

### README.md
Main project documentation with:
- Project overview
- Installation instructions
- Architecture details
- API documentation

### CHANGELOG.md
Version history with:
- Features added
- Bugs fixed
- Performance improvements
- Breaking changes

### QUICK_REFERENCE.md
Quick reference for:
- Docker commands
- URL endpoints
- Common tasks
- Troubleshooting

### docs/FLUJO_PRUEBAS_NUAM.txt
Testing flow documentation with:
- Test scenarios
- Expected results
- Manual testing steps

---

## 🎯 Clean Project Benefits

✅ **Organized**: Clear structure, easy to navigate
✅ **Maintainable**: Only essential files, no clutter
✅ **Documented**: Comprehensive docs in one place
✅ **Production-Ready**: Clean deployment structure
✅ **Version Controlled**: Proper .gitignore setup
✅ **Efficient**: Fast searches, quick access

---

## 🚀 Next Steps

1. **Commit Clean State**:
   ```bash
   git add .
   git commit -m "Clean up project: remove unnecessary files and consolidate documentation"
   ```

2. **Update .gitignore** (if needed):
   ```
   # Python
   __pycache__/
   *.py[cod]
   *$py.class
   *.so
   venv/

   # Django
   *.log
   staticfiles/
   media/

   # System
   .DS_Store
   Thumbs.db

   # IDEs
   .vscode/
   .idea/
   *.swp
   ```

3. **Regular Maintenance**:
   - Keep documentation updated
   - Remove test files after use
   - Rotate log files regularly
   - Clean Python cache monthly

---

**Last Updated**: December 9, 2025
**Status**: Clean and Organized ✅
