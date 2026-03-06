# Generic processor provider for pygeoapi plugins

Questo repository contiene una **web application Flask** che implementa
un servizio generico di esecuzione utilizzato come **servizio di
elaborazione esterno** per i plugin presenti nel progetto:

https://github.com/francescoingv/ingv-pygeoapi-process-plugins

Il servizio permette di ricevere richieste di esecuzione tramite API
HTTP, invocare un codice applicativo tramite riga di comando e
restituire lo stato dell'esecuzione e i risultati.

Il progetto è pensato come componente backend per l’esecuzione di processi
remoti e utilizza un sistema esterno (PostgreSQL) per registrare
le informazioni relative alle esecuzioni.

------------------------------------------------------------------------

## Overview

Il servizio è progettato per essere utilizzato insieme ai plugin **INGV
pygeoapi process plugins**, che implementano processi compatibili con lo
standard **OGC API - Processes**.

In questa architettura:

-   **pygeoapi** espone i processi tramite API standard
-   i **plugin pygeoapi** gestiscono le richieste di esecuzione
-   questo servizio esegue il codice applicativo richiesto

L'esecuzione dei codici avviene quindi in un servizio separato,
permettendo:

-   isolamento degli ambienti di esecuzione
-   gestione indipendente delle dipendenze
-   maggiore flessibilità nel deployment

------------------------------------------------------------------------

## Flusso di esecuzione

Il servizio espone endpoint HTTP utilizzati dai plugin di pygeoapi.

Flusso semplificato:

1.  il plugin pygeoapi riceve una richiesta di esecuzione
2.  il plugin invia una richiesta HTTP a questo servizio
3.  il servizio invoca il codice applicativo configurato sulla macchina locale
4.  il codice viene eseguito e il servizio raccoglie l'esito dell'esecuzione
5.  il servizio restituisce il risultato al plugin
6.  i risultati possono essere recuperati tramite le API esposte da pygeoapi

------------------------------------------------------------------------

## Configurazione

La configurazione del servizio avviene tramite due file principali.

### `application.ini`

Definisce i parametri dell'applicazione e il comando da eseguire.

Parametri principali:

-   `max_allowed_parameter_len`\
    lunghezza massima del nome di un parametro

-   `max_allowed_request_body_size`\
    dimensione massima della richiesta HTTP

-   `id_service`\
    identificativo del servizio

-   `command_line`\
    comando utilizzato per eseguire il codice applicativo

-   `suppress_stdout`\
    indica se lo standard output del processo deve essere soppresso

-   `file_root_directory`\
    directory utilizzata per file di input e output

### `database.ini`

Definisce i parametri di connessione al database PostgreSQL utilizzato
per gestire le richieste e lo stato dei job.

Esempio:

``` ini
[postgresql]
host=127.0.0.1
port=5433
database=ogc_api
user=ogc_api_user
password=user
```

### Schema del database

Il servizio richiede la presenza di uno schema PostgreSQL per
memorizzare le richieste di esecuzione e lo stato dei job.

Lo schema è fornito nel file:

``` text
postgresql_schema.backup.sql
```

Prima di avviare il servizio è necessario creare il database e
importare lo schema. Ad esempio:

```bash
psql -U ogc_api_user -d ogc_api -f postgresql_schema.backup.sql
```

Lo schema crea le tabelle principali utilizzate dal servizio:

- `request`
- `request_parameter`

La tabella `request` memorizza le informazioni relative ai job
ricevuti ed al loro stato di esecuzione.

La tabella `request_parameter` memorizza i parametri associati
a ciascuna richiesta.

L'utente configurato nel file `database.ini` deve avere i permessi
di accesso alle tabelle e alle sequenze definite nello schema.

### File di configurazione

Le principali configurazioni del servizio sono definite nei file:

- `va_simple_provider/application.ini`
- `va_simple_provider/database.ini`
- `va_simple_provider/logging.cfg`

Prima di avviare il servizio verificare in particolare i parametri di
connessione al database definiti nel file `database.ini`.

## Codici di elaborazione

Il sistema è progettato per eseguire codici applicativi esterni
definiti tramite il parametro `command_line` nel file di configurazione
`application.ini`.

I codici di elaborazione non fanno parte di questo repository
e possono essere installati e configurati indipendentemente
dal servizio.

------------------------------------------------------------------------

## API del servizio

### Esecuzione di un job

```text
POST /execute
```

Il body della richiesta deve contenere un oggetto JSON con i parametri
di esecuzione.

### Informazioni su un job

```text
GET /job_info/<job_id>
```

Restituisce lo stato dell'esecuzione e le informazioni sul job.

------------------------------------------------------------------------

## Struttura del progetto

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

## Deploy con Docker

Il repository è progettato per essere deployato tramite container
Docker.

Il `Dockerfile` incluso:

-   installa l'applicazione Flask
-   configura i parametri dell'applicazione
-   installa le dipendenze Python
-   avvia il servizio HTTP

Il servizio viene esposto sulla porta:

```text
5000
```

------------------------------------------------------------------------

## Requirements

Dipendenze principali:

-   Python ≥ 3.12
-   Flask
-   PostgreSQL
-   psycopg2
-   virtualenv / venv-run

Le dipendenze Python sono definite nel file `requirements.txt`.

------------------------------------------------------------------------

## Relazione con altri progetti

Questo progetto implementa il **servizio di elaborazione esterno**
utilizzato dai plugin definiti nel repository:

https://github.com/francescoingv/ingv-pygeoapi-process-plugins

I plugin pygeoapi inviano richieste HTTP a questo servizio per eseguire
i codici applicativi associati ai processi.

## Related software

Questo repository implementa il servizio di esecuzione utilizzato
dai plugin definiti nel progetto:

https://github.com/francescoingv/ingv-pygeoapi-process-plugins

I plugin pygeoapi ricevono le richieste di esecuzione tramite
le API OGC API - Processes e inoltrano la richiesta a questo servizio,
che invoca il codice applicativo configurato.

------------------------------------------------------------------------

## Citation

Se utilizzi questo software in un lavoro scientifico, ti preghiamo di
citarlo come segue:

Martinelli, F. (2026). Generic processor provider for external execution services used by INGV pygeoapi process plugins.

Il DOI verrà aggiunto dopo la pubblicazione su Zenodo.

------------------------------------------------------------------------

## License

Questo progetto è distribuito sotto licenza **MIT**.

Vedere il file `LICENSE` per maggiori dettagli.

------------------------------------------------------------------------

## Authors

Francesco Martinelli\
Istituto Nazionale di Geofisica e Vulcanologia (INGV)\
Pisa, Italy

