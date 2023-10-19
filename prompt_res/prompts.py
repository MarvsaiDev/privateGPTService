
columns = 'PART_NO, Description, Extended Price, Subscription Term, User Count (Qty) '
columns_dlt = columns.replace('PART_NO', 'MFG_Part_No')
ExtractionPrompt = dict(Cara=f"Extract {columns}' from the following into a ; separated csv file with \n as newline.",
                        DLT=f"Extract {columns_dlt}' from the following into a ; separated csv file with \n as newline.",)
