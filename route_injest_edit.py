
def load_single(path):
    docs = load_single_document(path)
    r=query_docs(docs)
    # explanation = query_valid_time(docs)
    # print(explanation)
    return r


examples = [
    {
        "name": "Example request a valid uri",
        "summary": "This is an example data you can expect.",
        "description": "Detailed description of Example 1.",
    },
    {
        "name": "Example 2",
        "summary": "Another example summary.",
        "description": "Detailed description of Example 2.",
    },
    # Add more examples as needed
]


@router.post("/get_total_uri/", response_model=ResponseTotal, response_model_exclude_none=True, summary="Get a list of Totals and Quote Valid Date in json format", description="Use a post to this endpoint with a json request as showin the examples on the right.")
async def file_url(filename: SharedFile):


    if not os.path.exists(filename.file_path):
        raise HTTPException(status_code=400,detail="URL file not accessisble. Was the url encoded correctly?")
    r=load_single(filename.file_path)
    empty_json = {'total': -1, 'quote_expiry': None, 'issue_date': None,
                  'error': 'Either the file has no total quote info or it is unrecognized. In later case please report to salman@acc.net. Could not find the expected columns: ', 'details': r}

    try:
        df = pd.read_csv(StringIO(r), sep=';')
    # question_openai(f'In this list which index is Total Price and Which one is expirey {r}')
        missing_cols = []
        if len(df.columns)==3:
            df.columns = ['total', 'quote_expiry', 'issue_date']
            df['quote_expiry'] = pd.to_datetime(df['quote_expiry'])
            try:
                df['issue_date'] = pd.to_datetime(df['issue_date'])
            except Exception as e:
                missing_cols.append('issue_date')
            df['quote_expiry'] = (df['quote_expiry']).dt.strftime('%Y-%m-%d')
            df['issue_date'] = (df['issue_date']).dt.strftime('%Y-%m-%d')
        else:
            log.warning('error ')
            raise HTTPException(status_code=400, detail=empty_json)
        r=df.to_json(orient='records')
        return json.loads(r)[0]
    except Exception as e:
        log.error(str(e))
        empty_json['error']+=str(e)
        raise HTTPException(status_code=424, detail=empty_json)


