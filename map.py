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
    '''
    # if compund exists get it from SS and update it
    # get dictionary of scinamic projects to refer to later
    sci_projects = Scinamic_Projects(scinamic_compounds.session)
    sci_projects.get_all_data()

    for sci_cmpd in scinamic_compounds.data:
        # update if it exists
        try:
            ld_cmpd = Compound.get(customer_key=sci_cmpd['pk'])
            ld_cmpd.corporate_id = sci_cmpd['id']
            ld_cmpd.canonical_smiles = sci_cmpd['smiles']
            try:
                ld_cmpd.mol_file = Chem.MolToMolBlock(Chem.MolFromSmiles(ld_cmpd.canonical_smiles))
            except:
                print("error creating molfile loading")
            ld_cmpd.created_at = sci_cmpd['creation_date']
            ld_cmpd.person = sci_cmpd['creation_user']
            ld_cmpd.archived = not sci_cmpd['active']
            ld_cmpd.save()
        except:
            # create new ones if needed

            try:
                molfile = Chem.MolToMolBlock(Chem.MolFromSmiles(sci_cmpd['smiles']))
            except:
                print("error creating molfile")
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
        # Check that project exists in SS
        # ld_projects = Project.select().execute()
        # ld_project_names = [p.__dict__['__data__']['key'] for p in ld_projects]
        # Breaks if project None
        if 'projects' in sci_cmpd:
            sci_cmpd['projects'] =[i.strip() for i in sci_cmpd['projects'].split(',')]
            for p in sci_cmpd['projects']:
                # get the scinamic projects key
                sci_proj_key = int(sci_projects.name[p]['pk'])

                # look it up in our Config table
                try:
                    ld_proj_name = SCINAMIC_PROJECTS_CONFIG[sci_proj_key]
                except:
                    ld_proj_name = None
                    # Project not in the config. Add it if you want it.

                # if project in Config
                if ld_proj_name:
                    # get id of current project
                    ld_proj_pk = Project.get(customer_key = sci_proj_key).id
                    # ask if it is in compoundproject
#                    query = CompoundProject.select().where(CompoundProject.compound_id==ld_cmpd.id, CompoundProject.project_id == ld_proj_pk).execute()
                    # if compound not registered already to the project put it in
                    CompoundProject.register(compound_id = ld_cmpd.id, project_id = ld_proj_pk)


# for after compounds have been added
def assay_map(results):
        '''
        study and project are short lists so they can be looped through quickly for saving my time I will do that for now.
        we would want to improve if 100+ studies and projects though

        assumes all results are "new" or need to be added, be sure to delete the compound observations table if doing
        a full reload
        '''
        sci_analysis = Scinamic_Analysis(results.session)
        sci_analysis.get_all_data()
        # bring results into simple schema
        for i in results.data:
            try:
                if i['project']!= 'NONE':
                    compound= Compound.get(corporate_id=i['compound'])

                    # register assay if it does not already exist (Note this is where pivoting happens)
                    if i["study"] in PIVOT_CONDITIONS:
                        # pivot = True
                        assay_key = i["study"]
                        for piv in PIVOT_CONDITIONS[i["study"]]:
                            assay_key += " %s"%i[piv]
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
                        value_operator = ''
                    # handle the timepoint unit
                    if 'timepoint_unit' in i:
                        unit = i['timepoint_unit']
                    else:
                        unit = i['value_unit']

                    if 'value_numeric' in i:
                        co = CompoundObservation.register(compound = compound, 
                                                            assay = assay, 
                                                            endpoint = i['value_type'], 
                                                            num_value = i['value_numeric'],
                                                            unit = unit,
                                                            value_operator = value_operator
                                                            )
                    else:
                        co = CompoundObservation.register(compound = compound, 
                                                            assay = assay, 
                                                            endpoint = i['value_type'], 
                                                            num_text = i['value_text'],
                                                            unit = unit,
                                                            value_operator = value_operator
                                                            )
                        # lastly handle the project ACLs
                    if ',' in i['project']:
                        ps = i['project'].split(',')
                        for p in ps:
                            CompoundObservationProject.register(compound_observation=co, 
                                        project=Project.get(key=p))
                    else:
                        CompoundObservationProject.register(compound_observation=co, 
                                        project=Project.get(key=i['project']))

            except:
               x=0

