<h1>Scinamic Integration</h1>

Welcome! The Scinamic integration pulls from Scinamic API and loads into simpleschema version 1.2.1 which DI can map back to synaptic using a standard configuration.
 
One note is that you must manually create the scinamic_changelog table (it has a hash and a timestamp) 
this is what allows us to only pull the necessary data instead of doing a full reload.


Setup:

Create Virtual Environment

<code>
virtualenv -p `which python3` venv
source venv/bin/activate
pip install -e .
</code>

Copy example_config.py and fill in appropriate information (see confluence for SA usage)

<code>
cp example_config.py config.py
nano config.py
</code>

Install SimpleSchema v1.2.1

<code>
cd ~seurat/pro_serv/
git clone git@github.com:schrodinger/livedesign-simpleschema.git
cd livedesign-simpleschema
git checkout RELEASE_V1.2.x
git checkout -b scinamic # this just keep you from accedently making changes to simpleschema
pip install .
</code>

Create postgres simpleschema DB called scinamic

<code>
psql -h localhost -p 3247 -U postgres -c "CREATE DATABASE scinamic;CREATE USER simpleschema WITH PASSWORD 'simpleschema';" 
</code>

Create the SimpleSchema Tables

<code>
create_tables --user postgres --password <postgres_pw> scinamic
</code>

Connect to psql scinamic db
<code>psql -h localhost -p 3247 -U postgres -d scinamic</code>

Create the scinamic_audit table for scinamic (Unique to Scinamic)
<code>
create table scinamic_audit (id SERIAL NOT NULL PRIMARY KEY, 
				audit_id INTEGER, 
				datetime TIMESTAMPTZ NOT NULL DEFAULT NOW());
insert into scinamic_audit (audit_id) VALUES(0);
</code>

Create the Source in simpleschema
id | key | config_id | person | uploaded | processed | purged | partial_purge | project_id
<code>
insert into scinamic (id)
</code>
