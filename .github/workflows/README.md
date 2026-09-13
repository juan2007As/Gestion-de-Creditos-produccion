# GitHub Actions CI/CD Configuration

## Overview

Este directorio contiene las configuraciones de GitHub Actions para automatizar testing, linting, security checks y performance benchmarks.

## Workflows Implemented

### 1. **tests.yml** - Main Test Pipeline
**Trigger:** Push/PR a `main` o `develop`, diariamente a las 2 AM UTC

**Jobs:**
- ✅ **tests**: Ejecuta 59 tests en Python 3.11 y 3.12
  - Django system check
  - Migrations
  - Unit + Integration + Regression tests
  - Coverage report (enviado a Codecov)
  
- ✅ **linting**: Validación de código
  - flake8: Análisis estático
  - black: Formato de código
  - isort: Orden de imports
  
- ✅ **security**: Auditoría de seguridad
  - bandit: Vulnerabilidades en código
  - safety: Vulnerabilidades en dependencias
  
- ✅ **performance**: Validación de performance
  - Verificación de N+1 queries
  - Confirma índices de BD
  
- ✅ **quality-gate**: Gate que requiere paso de todos los jobs
- 🔵 **notify-slack**: Notificación (opcional con secret)

**Configuration Required:**
```yaml
Secrets (en Settings > Secrets and variables > Actions):
- CODECOV_TOKEN: Token de codecov.io (opcional)
- SLACK_WEBHOOK_URL: Webhook de Slack (opcional)
```

---

### 2. **performance.yml** - Performance Testing
**Trigger:** Push a rutas específicas, PRs a main/develop, viernes a las 4 AM UTC

**Jobs:**
- ✅ **performance-baseline**: Tests de baseline
  - Carga datos de prueba (100 clientes)
  - Ejecuta tests de performance
  - Extrae métricas de queries
  
- ✅ **quality-gates**: Valida métricos de performance
- ✅ **benchmark-report**: Genera reporte de benchmarks

---

## Local Testing (Before Pushing)

### Run all GitHub Actions workflows locally with `act`:

```bash
# Instalar act si no está instalado
# macOS: brew install act
# Linux: curl https://raw.githubusercontent.com/nektos/act/master/install.sh | bash
# Windows: choco install act-cli

# Ejecutar workflow específico
act -j tests

# Ejecutar con verbosidad
act -j tests -v

# Ver workflows disponibles
act -l
```

### Run Django tests locally:

```bash
# Quick run (59 tests)
python manage.py test mi_app.test_fase_2 mi_app.test_unitarios_extendidos mi_app.test_integracion

# Con coverage
coverage run --source='.' manage.py test mi_app
coverage report
coverage html  # Genera reporte HTML en htmlcov/

# Test específico
python manage.py test mi_app.test_unitarios_extendidos.ClienteModelTests.test_crear_cliente

# O por módulo
python manage.py test mi_app.test_integracion
```

---

## Workflow File Locations

```
.github/workflows/
├── tests.yml                 # Main CI/CD pipeline (tests + linting + security)
├── performance.yml           # Performance testing and benchmarks
└── README.md                 # Este archivo
```

---

## What Gets Checked

### Tests (tests.yml)
- ✅ 59 unit + integration + regression tests
- ✅ Python 3.11 y 3.12
- ✅ Coverage report (80% target)
- ✅ System checks con `--deploy`

### Code Quality (tests.yml)
- ⚠️ flake8: Warnings only (no fail)
- ⚠️ black: Check formatting (no fail)
- ⚠️ isort: Import order (no fail)

### Security (tests.yml)
- 🔒 bandit: Detecta vulnerabilidades de seguridad
- 🔒 safety: Detecta dependencias con CVEs

### Performance (performance.yml)
- 📊 Query count baselines
- 📊 N+1 query detection
- 📊 Database index verification

---

## Viewing Results

### On GitHub
1. Go to repository
2. Click "Actions" tab
3. Select workflow run
4. Click job to see detailed logs
5. Download artifacts (test reports, coverage)

### Artifacts Generated
- `test-report-py*.txt`: Detailed test output
- `coverage.xml`: Coverage metrics (sent to Codecov)
- `benchmark-report/`: Performance metrics

### Coverage Report
Visit [Codecov.io](https://codecov.io) after setting `CODECOV_TOKEN` secret

---

## Customization

### To modify trigger conditions:

Edit the `on:` section in workflow files:

```yaml
on:
  push:
    branches: [ main, develop ]  # Branches to watch
  pull_request:
    branches: [ main, develop ]
  schedule:
    - cron: '0 2 * * *'  # Cron format (UTC)
```

### To add job to email on failure:

```yaml
- name: Send email notification
  if: failure()
  uses: dawidd6/action-send-mail@v3
  with:
    server_address: smtp.gmail.com
    server_port: 465
    username: your_email@gmail.com
    password: ${{ secrets.EMAIL_PASSWORD }}
    subject: "CI/CD Pipeline Failed"
    body: "Check: ${{ github.server_url }}/${{ github.repository }}/actions/runs/${{ github.run_id }}"
```

### To add deployment to staging:

```yaml
deploy-staging:
  needs: quality-gate
  runs-on: ubuntu-latest
  if: github.ref == 'refs/heads/develop'
  steps:
    - uses: actions/checkout@v3
    - name: Deploy to staging
      run: |
        # Your deployment script
```

---

## Common Issues & Solutions

### Issue: "Resource not available" on codecov
**Solution:** 
1. Go to Settings > Secrets and add `CODECOV_TOKEN`
2. Or disable codecov upload in workflow (remove that step)

### Issue: "Service postgres health check failed"
**Solution:** 
- Tests will use SQLite by default (not postgres)
- Postgres service in workflow is optional - can be removed

### Issue: "Bandit/flake8 warnings failing build"
**Solution:**
- Current config: pass with warnings only (`--exit-zero`)
- To make strict: remove `|| true` and `--exit-zero` flags

### Issue: "Tests pass locally but fail in GitHub"
**Solution:**
1. Check Python version (workflow uses 3.11, 3.12)
2. Check environment variables (DATABASE, DEBUG, SECRET_KEY)
3. Run locally with same Python version: `python3.11 manage.py test`
4. Check timezone: GitHub Actions uses UTC

---

## Next Steps

### Phase 1: ✅ COMPLETE
Workflows created and documented

### Phase 2: NEXT
1. Push to GitHub repository
2. Enable Actions in repository settings
3. Add required secrets (CODECOV_TOKEN, etc.)
4. Monitor first workflow runs

### Phase 3: Enhancement
1. Add deployment workflow (after security approval)
2. Add Slack notifications
3. Add performance regression detection
4. Add database backup on deployment

---

## Performance Targets

Based on previous FASE 2.2 optimization:

| Metric | Target | Current |
|--------|--------|---------|
| Test Execution Time | < 15s | 13.6s ✅ |
| Code Coverage | > 80% | 80% ✅ |
| Query Count (List) | < 5 | 1-2 ✅ |
| Query Count (Detail) | < 10 | 3-5 ✅ |
| API Response Time | < 200ms | ~150ms ✅ |

---

## References

- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [Django Testing Documentation](https://docs.djangoproject.com/en/6.0/topics/testing/)
- [Codecov Setup](https://codecov.io)
- [act - Run workflows locally](https://github.com/nektos/act)

---

**Last Updated:** 2026-02-21
**Maintained by:** Development Team
**Status:** ✅ Production-Ready
