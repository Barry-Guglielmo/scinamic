<h1>Scinamic Integration</h1>

Welcome! The Scinamic integration pulls from Scinamic API and loads into SimpleSchema version 1.2.1+ which DI can map back to synaptic using a standard configuration.

The initial configuration is to run every 15 minutes. For 7K compounds it takes roughly 20 minutes to do a FULL load of the compounds and assay data.

The audit functionality is under construction so this will currently do a full scinamic db drop and load each time it is run.

One note is that you must manually create the scinamic_changelog table (it has the last audit pk and a timestamp). This is what allows us to audit and only pull the necessary data instead of doing a full reload.

Currently this code is used on chef based servers. We will adapt as necessary for k8s.

<h2>Setup:</h2>

- Create Virtual Environment

```bash
virtualenv -p `which python3` venv
source venv/bin/activate
pip install -e .
```

- Copy example_config.py and fill in appropriate information (see confluence for SA usage)

```bash
cp example_config.py config.py
nano config.py
```

<h2>Install and Configure SimpleSchema v1.2.1 (Chef)</h2>

- Install SS

```bash
cd ~seurat/pro_serv/
git clone git@github.com:schrodinger/livedesign-simpleschema.git
cd livedesign-simpleschema
git checkout RELEASE_V1.2.x
git checkout -b scinamic # this just keep you from accedently making changes to simpleschema
pip install .
```

- Create postgres simpleschema DB called scinamic

```bash
psql -h localhost -p 3247 -U postgres -c "CREATE DATABASE scinamic;CREATE USER simpleschema WITH PASSWORD 'simpleschema';"
```

- Create the SimpleSchema Tables

```bash
create_tables --user postgres --password <postgres_pw> scinamic
```

- Connect to psql scinamic db
```bash
psql -h localhost -p 3247 -U postgres -d scinamic
```

- Create the scinamic_audit table for scinamic (Unique to Scinamic)
```bash
create table scinamic_audit (id SERIAL NOT NULL PRIMARY KEY, 
				audit_id INTEGER, 
				datetime TIMESTAMPTZ NOT NULL DEFAULT NOW());
insert into scinamic_audit (audit_id) VALUES(0);
```

- Create the Source in simpleschema

```bash
insert into scinamic (id)
```

<details>
<summary>This a drop down</summary>
This is the drop down text.
</details>
