import pandas as pd
import matplotlib as plt
import numpy as np
import psycopg2

import fn_sql
import fn_doi2bib
import fn_insert
import fn_getfile as fngf


#---PAPER-FUNCTIONS-------------------------------------------
def paper(doi,cite_tag,db_connection):
    dfndb = db_connection['dbobject']
    QUERY = '''
        SELECT *
        FROM paper
        WHERE paper.doi = '%s';
        ''' %doi
    df = pd.read_sql(QUERY,dfndb)
    matches = df.shape[0]

    if matches == 1:
        print('Entry exists in database, returning paper_id')
        paper_id = df['paper_id'][0]

    elif matches == 0:
        #Get doi info
        bib = fn_doi2bib.doi2citation_entry(doi)
        paper_tag = cite_tag
        year = bib['Year']
        title = bib['Title']
        authors = bib['Authors']
        url = bib['URL']

        #Insert into db
        QUERY = '''
            INSERT INTO paper("doi", "paper_tag", "year", "title", "authors", "url") 
            VALUES(%s, %s, %s, %s, %s, %s);
            '''
        PARAM = (doi, paper_tag, year, title, authors[0], url)
#         print('PRINTING PARAM')
#         print(PARAM) ######$$$$$
#         print('DONE PRINTING PARAM')
        fn_sql.postgres_query(QUERY, PARAM, db_connection)

        #Get paper_id
        QUERY = '''
            SELECT *
            FROM paper
            WHERE paper.doi = '%s';
            ''' %doi
        df = pd.read_sql(QUERY,dfndb)
        paper_id = df['paper_id'][0]
#         paper_id = df['paper_id'] ####
#         print(paper_id)###

    else:
        print('Error: Duplicate entries found')
        paper_id = np.NaN
        
    return paper_id

#---NEW-MATERIAL-FUNCTION----------------------------
def new_material_col(new_mat_str,db_connection):
    QUERY = '''
            ALTER TABLE material 
            ADD COLUMN %s numeric DEFAULT 0;
            ''' %new_mat_str
    PARAM = ()
    fn_sql.postgres_query(QUERY, PARAM, db_connection)
    
    
#---MATERIAL-FUNCTION    ----------------------------
def material(name,note,components,ratio,component_class,db_connection):
    dfndb = db_connection['dbobject']
    
    #Account for electrolyte salt for normalizing ratios:
    if component_class == 'electrolyte':
        salts_list = ['lipf6','litfsi','lifsi','liclo4','libob'] ##################update salts list
        salts_matched = list(set(components).intersection(salts_list)) #return list of matched strings
        salt_index = []

        for i in range(0,len(salts_matched)):
            ind = components.index(salts_matched[i])
            salt_index.append(ind) #get list of locations of matched strings

        ratio_nosalt = np.array(ratio)
        ratio = np.array(ratio)

        ratio_nosalt[salt_index]=0 #change salt ratios to 0 temporary
        ratio_nosalt = np.divide(ratio_nosalt,sum(ratio_nosalt)) #normalize solvents

        ratio_nosalt[salt_index] = ratio[salt_index] #bring back 1 for salts
        ratio = ratio_nosalt #set as ratio
    else:
        ratio = np.divide(ratio,sum(ratio)) #non electrolytes just normalize
        
    #insert if does not exist
    for i in range(0,len(components)):
        single_comp = components[i]
        new_material_col(single_comp,db_connection) #DOES THIS WORK IN THE FN FILE? ******************
    
    #get pandas table with all existing ratios of those components
    components = ", ".join(components) #split component list into a single string for SQL query
    def get_match_index(components,component_class,dfndb):
        QUERY = '''
                SELECT %s
                FROM material
                WHERE material.class = '%s';
                ''' %(components,component_class)
        df = pd.read_sql(QUERY,dfndb)

        ratios_in_DB = df.to_numpy() #get all component ratios

        id_match = -1

        if len(ratios_in_DB) == 0: #catch situation when table is empty
            id_index = -1
        else:
            for i in range(0,len(ratios_in_DB)):
                DBratio = ratios_in_DB[i]
                comparison = DBratio == ratio
                match_bool = comparison.all()
                if match_bool:
                    id_match = i #index of the match
        return id_match
    

    id_match = get_match_index(components,component_class,dfndb)
    if id_match>-1: #if there is a match
        print('Exisiting ratio in database at material_id')
        QUERY = '''
            SELECT material_id, %s
            FROM material
            WHERE material.class = '%s';
            ''' %(components,component_class)
        df = pd.read_sql(QUERY,dfndb)      
        
        material_id = df['material_id'][id_match]   
        
        #get df with single entry
        QUERY = '''
            SELECT material_id, %s
            FROM material
            WHERE material.material_id = '%s';
            ''' %(components,material_id)
        df_out = pd.read_sql(QUERY,dfndb)     
    else:
        print('Inserting into database') 
        ratio_str = ",".join(map(str,ratio)) #insert into db first
        QUERY= '''
             INSERT INTO material(name,class,note,%s) 
             VALUES('%s', '%s', '%s', %s)
             '''%(components,name,component_class,note,ratio_str)
        PARAM = ()
        fn_sql.postgres_query(QUERY, PARAM, db_connection)
        id_match = get_match_index(components,component_class,dfndb) #get index of current match
        QUERY = '''
            SELECT material_id, %s
            FROM material
            WHERE material.class = '%s';
            ''' %(components,component_class)
        df = pd.read_sql(QUERY,dfndb) 
#         print(id_match)
        material_id = df['material_id'][id_match] #get material_id of entry
        print(material_id)
        #get df with single entry
        QUERY = '''
            SELECT material_id, %s
            FROM material
            WHERE material.material_id = '%s';
            ''' %(components,material_id)
        df_out = pd.read_sql(QUERY,dfndb)        
        
        


    
    return df_out, material_id

#---PARAMETER-FUNCTION ----------------------------
def make_blob(path):
    blob = open(path, 'rb').read()
    blob = psycopg2.Binary(blob)
    
    return blob

#---INSERT DATA ----------------------------

def data(datadict,db_connection):
    keys = str(datadict.keys())
    keys = keys.replace('dict_keys([','')
    keys = keys.replace('])','')
    keys = keys.replace('\'','\"')
    keys = keys.replace(' ','') #Create a single string of dict keys separated by double quote marks " " for SQL string

    QUERY= '''
    INSERT INTO data(%s) 
    VALUES();
    ''' %keys

    key_array = keys.replace('\"','')
    key_array = key_array.split(',') #Separate each "key" into a list
    n_keys = len(key_array) #Get number of keys in dict
    value_string = '%s, '
    value_string = value_string*n_keys
    value_string = value_string[0:-2] #Make %s string for values to be entered

    QUERY = QUERY.replace('()','('+value_string+')')

    param_value = ()
    for i in range(0,n_keys):
        add_value = (datadict[key_array[i]],)
        param_value = param_value + add_value 
    PARAM = param_value
    
    fn_sql.postgres_query(QUERY, PARAM, db_connection)
        

        
        
#---INSERT PARAMETER_METHOD ----------------------------

def data_method(data_id,method_id,db_connection):
        QUERY= '''
                INSERT INTO data_method(data_id,method_id) 
                VALUES(%s, %s);
                '''
        PARAM = (data_id,method_id)
        fn_sql.postgres_query(QUERY, PARAM, db_connection)