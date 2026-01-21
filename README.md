 
 ```markdown
# Generic Processor Provider

Generic Processor Provider è un servizio Python basato su Flask, progettato
per fornire un provider di processing generico da integrare con **pygeoapi**
nell’ambito di architetture **OGC API – Processes**.

Il progetto è pensato come componente backend per l’esecuzione di processi
remoti e  utilizza un sistema esterno (PostgreSQL) per registrare
elementi dell'esecuzione.
```

---

## 🚀 Funzionalità

- Provider di processing compatibile con **ingv pygeoapi process plugin**
- API REST basata su Flask
- Integrazione con PostgreSQL tramite `psycopg2`
- Logging configurabile
- Struttura modulare per l’estensione dei processi

---

## 📁 Struttura del progetto

```text
generic-processor-provider/
├── requirements.txt
├── postgresql_schema.backup.sql
├── va_simple_provider/
│   ├── __init__.py
│   ├── application.ini
│   ├── database.ini
│   ├── logging.cfg
│   ├── views.py
│   ├── db_utils.py
│   ├── custom_exceptions.py
│   └── controllers/
│       └── code_handler.py
└── README.md
```

---

## 🧩 Requisiti

- Python >= 3.11
- PostgreSQL
- virtualenv / venv-run

---

## 🔧 Configurazione

Le principali configurazioni sono definite nei file:

- `va_simple_provider/application.ini`
- `va_simple_provider/database.ini`
- `va_simple_provider/logging.cfg`

Verificare i parametri di connessione al database prima dell’avvio del servizio.

---


