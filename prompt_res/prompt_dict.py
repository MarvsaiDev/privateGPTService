PRICE_COL = 4
IGNORE_COL = 6 + 1

PRICE_COL_KEY = 'price_col'
DESCRIBE_COL_KEY = 'description_col'
IGNORE_COL_IDX_KEY = 'ignore_cols'
STR_COLS_KEY = 'string_cols'
TOTAL_PROMPT = 'total_prompt'
META_DATA = 'metas'

class ExtractionPrompt:

    def get_alt(self, mydic: dict, key: str) -> dict:
        match key:
            case 'Atlassian':
                rd = mydic.copy()
                rd.update({
                    'appendPrompt': ' Also include date as part of Description. If there is no "Subscription start" and "Subscription end date" mark them with None.'})
                rd['columns'] = rd['columns'].replace(' Subscription End Date', ' Subscription End Date; SEN')
                rd['prompt'] = mydic['prompt'].format(rd['columns']) + ' ' + \
                               rd['appendPrompt']
                return rd
            case 'Atlassian_NOSEN':
                rd = mydic.copy()
                rd['prompt'] = mydic['prompt'].format(rd['columns'])
                return rd
            case 'Entrust':
                rd = mydic.copy()
                rd.update({
                    'appendPrompt': ' Also include serial number as part of Description.'})
                rd['columns'] = rd['columns'].replace(' Subscription End Date', ' Subscription End Date; Serial: ')
                rd['prompt'] = mydic['prompt'].format(rd['columns']) + ' ' + \
                               rd['appendPrompt']
                return rd
            case 'smartsheet':
                rd = mydic.copy()
                base_prompt = mydic['prompt'].format(rd['columns'])
                rd['addedPrompt'] = f'Question: ignore single p character, '
                rd['prompt'] = base_prompt+'\n'
                return rd



            case 'raw':
                rd = mydic.copy()
                # rd['prompt'] = mydic['prompt'].format(mydic['columns'])
                return rd
            case _:
                rd = mydic.copy()
                rd['prompt'] = mydic['prompt'].format(mydic['columns'])
                return rd

    def __init__(self, **kwargs):
        self.my_dict = {
        }
        self.my_dict.update(kwargs)

    def to_dict(self):
        # result = {}
        # for attr in dir(self):
        #     if not attr.startswith("__"):
        #         result[attr] = getattr(self, attr)
        return self.my_dict
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



class ExtractTableDict(dict):
    ALLOWED_KEYS = ['columns', 'total_prompt', IGNORE_COL_IDX_KEY, PRICE_COL_KEY, STR_COLS_KEY, DESCRIBE_COL_KEY, META_DATA]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def __setitem__(self, key, value):
        match key:
            case 'prompt':
                if '{}' in value:
                    super().__setitem__(key, value)
                else:
                    raise ValueError("prompt must have a '{}' to indicate location of the columns we are interest in.")
            case k if k in self.ALLOWED_KEYS:
                super().__setitem__(key, value)
            case _:
                raise ValueError(f"Cannot modify key '{key}' directly.")

# Example usage:
carahasoft_dict = ExtractTableDict({
    'prompt': "Extract '{}' from the quote data above into a ; separated CSV file with newline as the row separator. Do not include a header.\n",
    'columns': 'columns'+'; '+'quote_expirey',
    IGNORE_COL_IDX_KEY: [],
    PRICE_COL_KEY: 4,
    STR_COLS_KEY: ['Serial: '],
    DESCRIBE_COL_KEY: 2,
    'total_prompt': f"Extract the Total Price; Time Period (if availble otherwise None) in ; separator csv list. Do include header."
})

# Modify the prompt (allowed)
carahasoft_dict['prompt'] = "New prompt{}"

# # Modify an invalid key (raises ValueError) todo add tests
# try:
#     carahasoft_dict['INVALID_KEY'] = "Invalid value"
# except ValueError as e:
#     print(e)
