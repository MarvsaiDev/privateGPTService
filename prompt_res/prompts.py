PRICE_COL = 4
IGNORE_COL = 6 + 1

PRICE_COL_KEY = 'price_col'
DESCRIBE_COL_KEY = 'description_col'
IGNORE_COL_IDX_KEY = 'ignore_cols'
TOTAL_PROMPT = 'total_prompt'
columns = 'Line No #; PART NO; Description; Qty; Quote Price (unit); Extended Price; Subscription Start Date; Subscription End Date'
columns_dlt = 'Item No #; DLT Part No; MFG_Part_No; Description; User Count (QTY); Unit Price; Extended Price; Subscription Start Date; Subscription End Date'

columns_default = 'PART_NO #, Description, QTY, Quote Price, Extended Cost, Valid Date'
quo = 'Part Number, Contract, TransType, Product Description, Qty, List Price, Quote Price, Extended Price, Subscription Duration (PoP)'

carahasoft_dict = {
    'prompt': "Extract {} from the quote data above into a ; separated csv file with \n as newline.  Do not include header.",
    'columns': columns,
    IGNORE_COL_IDX_KEY: [],
    PRICE_COL_KEY: 4,
    DESCRIBE_COL_KEY: 2,
    'total_prompt': f"Extract the Total Price, Time Period (if availble otherwise None) in ; separator csv list. Do include header."
}
dlt_dict = {
    'prompt': "Extract {} from the data above into a ; separated csv file with \n as newline.  Do not include header.",
    'columns': columns_dlt,
    IGNORE_COL_IDX_KEY: [1],
    PRICE_COL_KEY: 5,
    DESCRIBE_COL_KEY: 2,
    'total_prompt': None
}
default_dict = {
    'prompt': "Extract {} from the quote above into a ; separated csv file with \n as newline.  Do not include header.",
    'columns': columns_default,
    IGNORE_COL_IDX_KEY: [],
    PRICE_COL_KEY: 3,
    DESCRIBE_COL_KEY: 1,
    'total_prompt': None
}

quo_dict = {
    'prompt': f"Extract {quo} from the data above into a ; separated csv file with \n as newline.  Do not include header.",
    'columns': quo,
    IGNORE_COL_IDX_KEY: [1, 2, 5],
    PRICE_COL_KEY: 6,
    DESCRIBE_COL_KEY: 3,
    'reset_total': 1,
    'total_prompt': f"Extract the Total Price, Time Period (if available otherwise None) in ; separator csv list. Do include header."
}

appspace_cols = 'PART_NO #, Detail, Quantity, Unit Price (per month), Contract Total, Renewal Term'


class ExtractionPrompt:

    def get_alt(self, mydic: dict, key: str) -> dict:
        match key:
            case 'Atlassian':
                rd = mydic.copy()
                rd.update({
                    'appendPrompt': ' Also include SEN-xxxxxxxx and date as part of Description. If there is no "Subscription start" and "Subscription end date" mark them with None.'})
                rd['columns'] = rd['columns'].replace(' Subscription End Date', ' Subscription End Date; SEN;')
                rd['prompt'] = mydic['prompt'].format(rd['columns']) + ' ' + \
                               rd['appendPrompt']
                return rd
            case 'Entrust':
                rd = mydic.copy()
                rd.update({
                    'appendPrompt': ' Also include : serial number as part of Description. If there is no "Subscription start" and "Subscription end date" mark them with None.'})
                rd['columns'] = rd['columns'].replace(' Subscription End Date', ' Subscription End Date; Serial:')
                rd['prompt'] = mydic['prompt'].format(rd['columns']) + ' ' + \
                               rd['appendPrompt']
                return rd
            case 'raw':
                rd = mydic.copy()
                # rd['prompt'] = mydic['prompt'].format(mydic['columns'])
                return rd
            case _:
                rd = mydic.copy()
                rd['prompt'] = mydic['prompt'].format(mydic['columns'])
                return rd

    def __init__(self, Cara, DLT, default, **kwargs):
        self.my_dict = {
            'Cara': Cara,
            'DLT': DLT,
            'default': default
        }
        self.my_dict.update(kwargs)

    def __getitem__(self, keys):
        if isinstance(keys, tuple):
            key1, key2 = keys
            altdict = self.get_alt(self.my_dict[key1], key2)
            return altdict

        else:
            return self.get_alt(self.my_dict[keys], '')

    def __setitem__(self, key, value):
        self.my_dict[key] = value

    def __delitem__(self, key):
        del self.my_dict[key]


ExtractionPrompt = ExtractionPrompt(Cara=carahasoft_dict,
                                    DLT=dlt_dict, QUO=quo_dict, default_plus=default_dict,default=default_dict, raw=default_dict)
test = 'Extract Item No, PART_NO (MFG), Description, User Count (Qty), Quote Price (unit), Subscription Start Date, Subscription End Date from the data above into a ; separated csv file with   as newline. Do not include header'

trainingText = """        'QUOTE NO:\n10/30/2023\n41495096\nCONFIDENTIAL\n5\nRSU-SMPLE\nRemote Support Concurrent User Cloud, Annual\nBeyondTrust Corporation - RSU-CLOUD\nStart Date: 12/01/2024\nEnd Date: 11/30/2025\n$2,170.36\n10\n$21,703.60\nOM\nOPTION YEAR 1 SUBTOTAL:\n$21,703.60\nOPTION YEAR 2\n'        
        Question: Extract Item No, PART_NO, Description, User Count (Qty), Quote Price (unit), Subscription Start Date, Subscription End Date  from the data above into a ; separated csv file with \n  newline.  Do not include header.
        5;RSU-SMPLE;Remote Support Concurrent User Cloud Annual;10;2170.36;12/01/2024;11/30/2025\n"""
