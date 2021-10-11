def write():
    samplesdict = {
    "OCV curves for cathodes with higher than 50% nickel content" :  '''
        SELECT DISTINCT data.data_id, parameter.name as parameter_name, material.name as material_name, paper.paper_tag,data.raw_data, parameter.units_output, data.temp_range
        FROM data
        JOIN paper ON paper.paper_id = data.paper_id
        JOIN material ON material.material_id = data.material_id
        JOIN parameter ON parameter.parameter_id = data.parameter_id
        WHERE parameter.name = 'half cell ocv'
        AND material.ni > 0.5
        ''',
    "See all parameters available in LiionDB": '''
        SELECT * FROM parameter
        ''',
    "Li diffusivities in graphite that are valid at 10 °C": '''
        SELECT DISTINCT data.data_id,parameter.name as parameter_name, material.name as material_name, paper.paper_tag, paper.doi, data.temp_range
        FROM data
        JOIN paper ON paper.paper_id = data.paper_id
        JOIN material ON material.material_id = data.material_id
        JOIN parameter ON parameter.parameter_id = data.parameter_id
        WHERE parameter.name = 'diffusion coefficient'
        AND material.class = 'negative'
        AND material.gr = 1
        AND 283 BETWEEN lower(data.temp_range) AND upper(data.temp_range)
        ''',
    "See all separator porosities": '''
        SELECT DISTINCT data.data_id,parameter.name as parameter_name material.name as material_name paper.paper_tag,data.raw_data
        FROM data
        JOIN paper ON paper.paper_id = data.paper_id
        JOIN material ON material.material_id = data.material_id
        JOIN parameter ON parameter.parameter_id = data.parameter_id
        WHERE parameter.name = 'porosity'
        AND material.class = 'separator'
        ''',
    "All papers that publish parameters on LFP": '''
        SELECT DISTINCT paper.paper_tag, paper.title, paper.doi
        FROM paper
        JOIN data ON data.paper_id = paper.paper_id
        JOIN material ON data.material_id = material.material_id
        WHERE material.note = 'LiFePO4'
        ''',
    "Parameters that have been measured with EIS": '''
        SELECT DISTINCT parameter.name
        FROM parameter
        JOIN data ON data.parameter_id = parameter.parameter_id
        JOIN data_method ON data.data_id = data_method.data_id
        JOIN method ON data_method.method_id = method.method_id
        WHERE  method.name = 'EIS'
        ''',

    "See the Doyle 1996 paper parameters": '''
        SELECT DISTINCT data.data_id,parameter.name as parameter_name material.name as material_name paper.paper_tag,data.raw_data, parameter.units_output, data.notes
        FROM data
        JOIN paper ON paper.paper_id = data.paper_id
        JOIN material ON material.material_id = data.material_id
        JOIN parameter ON parameter.parameter_id = data.parameter_id
        WHERE paper.paper_tag = 'Doyle1996'
        ''',

    # "Full electrolyte parameterizations": '''
    #     SELECT DISTINCT material.name as material_name, paper.paper_tag, parameter.name as param_name
    #     FROM material
    #     JOIN data ON data.material_id = material.material_id
    #     JOIN paper ON data.paper_id = paper.paper_id
    #     JOIN parameter ON data.parameter_id = parameter.parameter_id
    #     WHERE material.class = 'electrolyte'
    #     AND parameter.name IN ('ionic conductivity','diffusion coefficient','transference number','thermodynamic factor')
    #     LIMIT 5
    #     '''
    
        }
    return samplesdict
