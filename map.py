"""
This is a description of how the api values relate back to simple schema
"""

from config import *
from api import *
from simpleschema.models import *
from simpleschema.schemas import SimpleSchema
from rdkit import Chem

def compound_map(scinamic_compounds):
    '''
    The etl process for getting compounds into SS
    SS Compound Fields:
                            id            ---> LD PK
                            customer_key  ---> Scinamic PK
                            archived      ---> active?
                            rowhash       ---> N/A
                            created_at    ---> creation_date
                            modified_at   ---> N/A
                            mol_file      ---> N/A
                            corporate_id  ---> id
                            person        ---> creation_user
                            molhash
                            canonical_smiles---> smiles
                            source_id       ---> N/A Optional...

    scinamic_compounds is a class object defined in api.py
    ss_session is the simpleschema session already opened

    Here we will also Map back to the compound project
    Take in list of compounds (1K at a time)
    '''
    # if compund exists get it from SS and update it
    # get dictionary of scinamic projects to refer to later
    logger.info('logging next batch of %s compounds'%len(scinamic_compounds))
    # get the sci projects for mapping
    s = Scinamic_Session(SCINAMIC_API_CONFIG)
    sci_projects = Scinamic_Projects(s)
    sci_projects.get_all_data()
    for sci_cmpd in scinamic_compounds:
        # update if it exists
        try:
            ld_cmpd = Compound.get(customer_key=sci_cmpd['pk'])
            ld_cmpd.corporate_id = sci_cmpd['id']
            ld_cmpd.canonical_smiles = sci_cmpd['smiles']
            try:
                ld_cmpd.mol_file = Chem.MolToMolBlock(Chem.MolFromSmiles(ld_cmpd.canonical_smiles))
            except:
                logger.error("error creating molfile")
            ld_cmpd.created_at = sci_cmpd['creation_date']
            ld_cmpd.person = sci_cmpd['creation_user']
            ld_cmpd.archived = not sci_cmpd['active']
            ld_cmpd.save()
            go = True
        except:
            # create new ones if needed
            try:
                molfile = Chem.MolToMolBlock(Chem.MolFromSmiles(sci_cmpd['smiles']))
            except:
                molfile = ''
            try:
                Compound.register(
                            corporate_id = sci_cmpd['id'], 
                            customer_key=sci_cmpd['pk'],
                            canonical_smiles = sci_cmpd['smiles'],
                            mol_file = molfile, 
                            created_at = sci_cmpd['creation_date'],
                            person = sci_cmpd['creation_user'],
                            archived = not sci_cmpd['active']
                            )
                ld_cmpd = Compound.get(customer_key=sci_cmpd['pk'])
                go = True
            except:
                logger.error('error processing:\n'+str(sci_cmpd)+'\n')
        # ACL to projects (breaks if project = None)
        if 'projects' in sci_cmpd and go == True:
            sci_cmpd['projects'] =[i.strip() for i in sci_cmpd['projects'].split(',')]
            for p in sci_cmpd['projects']:
                # get the scinamic projects key
                try:
                    sci_proj_key = int(sci_projects.name[p]['pk'])
                except:
                    logger.error('No sci_projects for %s'%str(p))
                # look it up in our Config table
                try:
                    ld_proj_names = SCINAMIC_PROJECTS_CONFIG[sci_proj_key]
                except:
                    ld_proj_names = None
                    # Project not in the config. Add it if you want it.

                # if project in Config
                if ld_proj_names:
                    for i in ld_proj_names:
                        # get id of current project
                        ld_proj_pk = Project.get(key = i).id
                        CompoundProject.register(compound_id = ld_cmpd.id, project_id = ld_proj_pk)
            if SCINAMIC_PROJECTS_CONFIG['GLOBAL']:
                for i in SCINAMIC_PROJECTS_CONFIG['GLOBAL']:
                    ld_proj_pk = Project.get(key = i).id
                    CompoundProject.register(compound_id = ld_cmpd.id, project_id = ld_proj_pk)

# for after compounds have been added
def assay_map(results):
        '''
        study and project are short lists so they can be looped through quickly for saving my time I will do that for now.
        we would want to improve if 100+ studies and projects though

        assumes all results are "new" or need to be added, be sure to delete the compound observations table if doing
        a full reload
        '''
        # sci_analysis = Scinamic_Analysis(results.session)
        # only handles 1K analysis as of now...can improve when needed.
        # sci_analysis.get_all_data()
        # bring results into simple schema
        logger.info('logging next batch of %s results'%len(results))
        for i in results:
            try:
                if i['project']!= 'NONE':
                    compound= Compound.get(corporate_id=i['compound'])
                    # register assay if it does not already exist (Note this is where pivoting happens)
                    if i["study"] in PIVOT_CONDITIONS:
                        # pivot = True
                        assay_key = i["study"]
                        for piv in PIVOT_CONDITIONS[i["study"]]:
                            assay_key += "%s%s"%(PIVOT_DELIMITER,i[piv])
                    else:
                        # pivot = False
                        assay_key = i["study"]

                    try:
                        assay = Assay.get(key=assay_key)
                    except:
                        Assay.register(key=assay_key)
                        assay = Assay.get(key=assay_key)

                    # handle value operator
                    if 'value_operator' in i:
                        value_operator = i['value_operator']
                    else:
                        value_operator = None
                    # handle the timepoint unit
                    if 'timepoint_unit' in i:
                        unit = i['timepoint_unit']
                    if 'value_unit' in i:
                        unit = i['value_unit']
                    else:
                        unit = None
                    # check if observation already exists
                    try:
                        co = CompoundObservation.get(customer_key=i['pk'])
                        co.compound = compound
                        co.assay = assay
                        co.endpoint = i['value_type']
                        if 'value_numeric' in i:
                            co.num_value = float(i['value_numeric'])
                        else:
                            co.text_value = i['value_text']
                        co.unit = unit
                        co.value_operator = value_operator
                        co.save()
                    except:
                        if 'value_numeric' in i:
                            co = CompoundObservation.register(compound = compound,
                                                            customer_key = i['pk'],
                                                            assay = assay,
                                                            endpoint = i['value_type'],
                                                            num_value = float(i['value_numeric']),
                                                            unit = unit,
                                                            value_operator = value_operator
                                                            )
                        else:
                            co = CompoundObservation.register(compound = compound,
                                                            customer_key = ['pk'],
                                                            assay = assay,
                                                            endpoint = i['value_type'],
                                                            text_value = i['value_text'],
                                                            unit = unit,
                                                            value_operator = value_operator
                                                            )
                    # handle the project ACLs
                    if ',' in i['project']:
                        ps = i['project'].split(',')
                        for p in ps + SCINAMIC_PROJECTS_CONFIG['GLOBAL']:
                            try:
                                CompoundObservationProject.register(compound_observation=co,
                                        project=Project.get(key=p))
                            except:
                                # already registered (or project not in config)
                                logger.info('CompoundObservation for %s already in project %s or project not in config.py', i['compound'],i['project'])
                    else:
                        try:
                            CompoundObservationProject.register(compound_observation=co,
                                        project=Project.get(key=i['project']))
                        except:
                            # already registered (or project not in config)
                            logger.info('CompoundObservation for %s already in project %s or project not in config.py', i['compound'],i['project'])
                        for i in SCINAMIC_PROJECTS_CONFIG['GLOBAL']:
                            try:
                                CompoundObservationProject.register(compound_observation=co,
                                        project=Project.get(key=i))
                            except:
                                logger.info('Already in global observation project: %s',i['compound'])

                    # Map Curves
                    if 'resultcurve' in i:
                        # this will just add the endpoint we image service will have.
                        # there is a seperate function to load curves because they are SLOW to render
                        try:
                            rc = CompoundObservation.register(compound = compound,
                                                            assay = assay,
                                                            endpoint = 'ResultCurve',
                                                            text_value ='<img style="width: 100%; height: 100%;" src="{}/livedesign/images/scinamic/curves/{}">'.format(BASE_URL, i['resultcurve'])
                                                            )
                        # handle the project ACLs
                            if ',' in i['project']:
                                ps = i['project'].split(',')
                                for p in ps + SCINAMIC_PROJECTS_CONFIG['GLOBAL']:
                                    CompoundObservationProject.register(compound_observation=rc,
                                            project=Project.get(key=p))
                            else:
                                CompoundObservationProject.register(compound_observation=rc,
                                            project=Project.get(key=i['project']))
                                for i in SCINAMIC_PROJECTS_CONFIG['GLOBAL']:
                                    CompoundObservationProject.register(compound_observation=co,
                                        project=Project.get(key=i))
                        except:
                            logger.error('Result Curve Error for: ',str(i))
            except:
                logger.error('Did not pass first Result try/except loop:\n%s',str(i))
def audit_map(scinamic_audit_class):
    '''
    Here we will go through the changes made from last audit key up to now and update the ss record.
    We will make entity specific decions here. {'GenomicExperiment', 'PlasmidType', 'GenomicSample', 'CompoundBatch'}

    testing from: 
    '''
    # Additionally entity type matters, so we can use a dict to make a decision tree easier
    def record_info_by_entity(my_audit_list, audit_type, batch_size = 1000):
        d = {}
        record_pks = [i['record'] for i in scinamic_audit_class.audits if i['type']==audit_type]
        record_pks = [record_pks[i:i + 1000] for i in range(0, len(record_pks), 1000)]
        for i in record_pks:
            # get records in batch of 1K
            records = scinamic_audit_class.session.get_records(i).data
            for j in records:
                if j['entity'] not in d:
                    d[j['entity']] = [j]
                else:
                    d[j['entity']].append(j)
        return d
    new = record_info_by_entity(scinamic_audit_class, 'N')
    update = record_info_by_entity(scinamic_audit_class, 'U')
    delete = record_info_by_entity(scinamic_audit_class, 'D')
    # handle compounds test (new and update compound checked out)
    if 'Compound' in new:
        logger.info('New compounds detected: %s'%str(new['Compound']))
        compound_map(new['Compound'])
    if 'Compound' in update:
        logger.info('Updated compounds detected: %s'%str(update['Compound']))
        compound_map(update['Compound'])
    if 'Compound' in delete:
        logger.error('Deletion Function for Compounds In Progress')

    # handle results (new and update checked out)
    if 'Result' in new:
        logger.info('New compounds detected: %s'%str(new['Result']))
        assay_map(new['Result'])
    if 'Result' in update:
        logger.info('New compounds detected: %s'%str(new['Result']))
        assay_map(update['Result'])
    if 'Result' in delete:
        logger.error('Deletion Function for Results In Progress')
    # compound batch next
    logger.info('Dictionaries below are just the info from API calls, not the actual changes made to SS...')
    logger.info('New Entries Dictionary: %s', str(new))
    logger.info('Updated Entries Dictionary: %s', str(update))
    logger.info('Deleted Dictionary: %s', str(delete))
    if 'Compound' in new:
        logger.info('Expected New Compounds: %i',str(new['Compound']))
