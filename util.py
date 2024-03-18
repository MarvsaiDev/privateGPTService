from prompt_res.prompts import ExtractionPrompt
import logging as log

def get_query_request_obj(query:str, request):

    if 'carahsoft' in query:
        secondKey = 'Atlassian' if 'Atlassian' in query else ''
        if ' Entrust' in query:
            secondKey = 'Entrust'
        if 'Smartsheet' in query:
            secondKey = 'smartsheet'

        querydict = ExtractionPrompt['Cara', secondKey]
        request.query = querydict['prompt']

        request.meta = querydict

        return request
    if 'WESCO ' in query:
        querydict = ExtractionPrompt['default_plus']
        request.query = querydict['prompt']
        request.meta = querydict
    elif 'Carah' in request.query:
        secondKey = 'Atlassian' if 'Atlassian' in request.query else ''
        if ' Entrust' in request.query:
            secondKey = 'Entrust'

        querydict = ExtractionPrompt['Cara', secondKey]
        request.query = querydict['prompt']

        request.meta = querydict
    elif 'DLT' in request.query:
        querydict = ExtractionPrompt['DLT']
        request.meta = querydict
        request.query = querydict['prompt']
    elif 'QUO' in request.query:
        querydict = ExtractionPrompt['QUO']
        request.meta = querydict
        request.query = querydict['prompt']
    elif 'object' in request.query:
        query = ExtractionPrompt['Cara']
        request.query = query
    else:
        log.info('unknown format trying')
        ep = ExtractionPrompt
        querydict = ep['default']
        request.meta = querydict
        # request.query = querydict['prompt']
        querydict = ep.my_dict['default'].copy()


    return request