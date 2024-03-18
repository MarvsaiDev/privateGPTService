from prompt_res.prompt_dict import *

columns = 'Line No #; PART NO; Description; Qty; Quote Price (unit); Extended Price; Subscription Start Date; Subscription End Date'
columns_dlt = 'Item No #; DLT Part No; MFG_Part_No; Description; User Count (QTY); Unit Price; Extended Price; Subscription Start Date; Subscription End Date'
columns_voss = 'Product Part No; Description; Quantity; Unit Price; Offered Price; Months; Term; Expiration Date'
columns_default = 'PART_NO #; Description; QTY; Quote Price; Extended Cost; Valid Date'
quo = 'Part Number, Contract, TransType, Product Description, Qty, List Price, Quote Price, Extended Price, Subscription Duration (PoP)'
quote_expirey = 'Quote Expires date'
carahasoft_dict = ExtractTableDict({
    'prompt': "Extract '{}' from the quote data above into a ; separated CSV file with newline as the row separator. Do not include a header.\n",
    'columns': columns+'; '+quote_expirey,
    IGNORE_COL_IDX_KEY: [],
    PRICE_COL_KEY: 4,
    STR_COLS_KEY: ['Serial: '],
    DESCRIBE_COL_KEY: 2,
    'total_prompt': f"Extract the Total Price; Time Period (if availble otherwise None) in ; separator csv list. Do include header."
})

dlt_dict = {
    'prompt': "Extract '{}' from the data above into a ; separated csv file with \n as newline.  Do not include header.\n",
    'columns': columns_dlt,
    IGNORE_COL_IDX_KEY: [1],
    PRICE_COL_KEY: 5,
    DESCRIBE_COL_KEY: 2,
    'total_prompt': None
}

default_dict = {
    'prompt': "Extract {} from the quote above into a ; separated csv file with \n as newline.  Do not include header.\n",
    'columns': columns_default,
    IGNORE_COL_IDX_KEY: [],
    PRICE_COL_KEY: 3,
    DESCRIBE_COL_KEY: 1,
    'total_prompt': None
}

default_dict_stock = {
    'prompt': "Extract '{}' from the quote above into a ; separated csv file with \n as newline.  Do not include header.\n",
    'columns':  'Line No; Stock No; Part_Number #; Description; QTY; Quote Price; Extended Cost; Valid Date',
    IGNORE_COL_IDX_KEY: [1],
    PRICE_COL_KEY: 5,
    DESCRIBE_COL_KEY: 3,
    'total_prompt': None,
    'oneshot':'''\'QUOTATION\nDate:\n02/19/2024\nQuote #:\nQ00BXPP8\nCustomer:\n268195\n2301 Patriot Blvd.  Glenview,  IL 60026\nSEWP RFQ 292203\nCustomer\nADVANCED COMPUTER CONCEPTS\n7927 JONES BRANCH DR STE 600 N\nMCLEAN, VA 22102\nPhone: --\nFax: --\nAnixter Inc. (a WESCO Company)\nSend Purchase Orders to Anixter Inc.\nLine\nQuantity\nPart Number and Description\nUM\nUnit Price\nExtended Price\n1\n1\n496242\nBRADY CORP BMP51\nBMP51 MOBILE PRINTER W/LI-ION BAT PACK,AC ADAP/BAT\nCHARGER\nLead Time: in stock\nShipping Location: CHICAGO,IL (102)\nEA\n381.32\n381.32\n2\n2\nNon-Stock\nBRADY CORP M4C-500-422\nAGGRESSIVE ADHESIVE MULTI-PURPOSE POLYESTER\nLABELSWITH RIBBON FOR BMP4\nBMP51, M511 PRINTERS - 0.5"\nLead Time: in stock with vendor\nPart Availability: ***replacement for MC-500-422\nShipping Location: CHICAGO,IL (102)\nEA\n31.69\n63.38\n3\n2\nNon-Stock\nBRADY CORP M4C-1000-422\nAGGRESSIVE ADHESIVE MULTI-PURPOSE POLYESTER\nLABELSWITH RIBBON FOR BMP4\nBMP51, M511 PRINTERS - 1"\nLead Time: in stock with vendor\nPart Availability: ***replacement for MC1-1000-422\nShipping Location: CHICAGO,IL (102)\nEA\n50.01\n100.02\n4\n4\n10403521\nBRADY CORP M4-143-427\nCARTRIDGE OF 200 LABELS 1.25" X 1" WHITE\nLead Time: in stock with vendor\nShipping Location: CHICAGO,IL (102)\nEA\n44.60\n178.40\nPage 1 of 3\nquote-en-US Version 2.5.1\nBY ACCEPTING THIS QUOTE, YOU AGREE THAT THE TERMS AND CONDITIONS OF SALE PUBLISHED AT WWW.ANIXTER.COM/TERMSANDCONDITIONS ARE EXPRESSLY INCORPORATED INTO AND\nSHALL GOVERN THIS TRANSACTION.\nWesco may charge you storage and transportation fees if you do not take possession or accept delivery of the above products within ninety (90) days or agreed upon terms from such\nproducts being available for delivery or pick-up
\nQUOTATION\nDate:\n02/19/2024\nQuote #:\nQ00BXPP8\nCustomer:\n268195\n2301 Patriot Blvd.  Glenview,  IL 60026\nSEWP RFQ 292203\nAnixter Inc. (a WESCO Company)\nSend Purchase Orders to Anixter Inc.\nLine\nQuantity\nPart Number and Description\nUM\nUnit Price\nExtended Price\n5\n2\nNon-Stock\nBRADY CORP M4-60-428\nMETALIZED SOLVENT RESISTANT MATTE GRAY POLYESTER\nLABELS WITH RIBBON FOR\nBMP41 BMP51 M511 PRINTERS - 2"\nX 1"\nLead Time: in stock with vendor\nShipping Location: CHICAGO,IL (102)\nEA\n61.31\n122.62\n6\n4\n10390185\nBRADY CORP M4-51-427\n2.50"WX1.00"H SELF-LAMINATING|VINYL LABEL FOR BMP51\n110| LABEL CARTRIDGE WHIT\nLead Time: in stock\nShipping Location: CHICAGO,IL (102)\nEA\n42.98\n171.92\n7\n1\n423353-PK\nPLATINUM 105920\nEZ-RJ45 SHIELDED CONNECTOR 100/PK\nLead Time: in stock\nShipping Location: CHICAGO,IL (102)\nPK\n129.90\n129.90\n8\n3\n977478\nCS-COMMSCO 760237046\nDISCRETE DISTRIBUTION MODULE PANEL, SL, STP, 1U, 24\nPORT CPP-SDDM-SL-1U-24\nLead Time: 2-3 weeks ARO\nShipping Location: CHICAGO,IL (102)\nEA\n54.94\n164.82\n9\n50\n10097560\nCS-UNIPRIS 760238139\nUNIPRISE SLX MODULAR RJ45 JACKCAT 6 SHIELDED W/OUT\nDUST CVR USL600-SHLD, BLK\nLead Time: in stock\nShipping Location: CHICAGO,IL (102)\nEA\n9.94\n497.00\n10\n500\n10183539\nBELDEN 6500FE 010U500\nBELD 6500FE-010U500 CABLE, SECURITY/COMMERCIAL\nAUDIO| 2C| 300V| BLACK\nLead Time: 45 days ARO if no stock\nPart Availability: 1000ft in stock with Belden\nShipping Location: CHICAGO,IL (102)\nFT\n0.17\n86.35\nPage 2 of 3\nquote-en-US Version 2.5.1\nBY ACCEPTING THIS QUOTE, YOU AGREE THAT THE TERMS AND CONDITIONS OF SALE PUBLISHED AT WWW.ANIXTER.COM/TERMSANDCONDITIONS ARE EXPRESSLY INCORPORATED INTO AND\nSHALL GOVERN THIS TRANSACTION.\nWesco may charge you storage and transportation fees if you do not take possession or accept delivery of the above products within ninety (90) days or agreed upon terms from such\nproducts being available for delivery or pick-up\n
\'

A:
1;496242;BMP51;"BRADY CORP BMP51 BMP51 MOBILE PRINTER W/LI-ION BAT PACK;AC ADAP/BAT CHARGER";1;$381.32;$381.32;02/19/2024
2;Non-Stock;M4C-500-422;"BRADY CORP M4C-500-422 AGGRESSIVE ADHESIVE MULTI-PURPOSE POLYESTER LABELSWITH RIBBON FOR BMP4 BMP51; M511 PRINTERS - 0.5""";2;$31.69;$63.38;02/19/2024
3;Non-Stock;M4C-1000-422;"BRADY CORP M4C-1000-422 AGGRESSIVE ADHESIVE MULTI-PURPOSE POLYESTER LABELSWITH RIBBON FOR BMP4 BMP51; M511 PRINTERS - 1""";2;$50.01;$100.02;02/19/2024
4;10403521;M4-143-427;BRADY CORP M4-143-427 CARTRIDGE OF 200 LABELS 1.25" X 1" WHITE;4;$44.60;$178.40;02/19/2024
5;Non-Stock;M4-60-428;"BRADY CORP M4-60-428 METALIZED SOLVENT RESISTANT MATTE GRAY POLYESTER LABELS WITH RIBBON FOR BMP41 BMP51 M511 PRINTERS - 2"" X 1""";2;$61.31;$122.62;02/19/2024
6;10390185;M4-51-427;"BRADY CORP M4-51-427 2.50""WX1.00""H SELF-LAMINATING|VINYL LABEL FOR BMP51 110| LABEL CARTRIDGE WHIT";4;$42.98;$171.92;02/19/2024
7;423353-PK;105920;PLATINUM 105920 EZ-RJ45 SHIELDED CONNECTOR 100/PK;1;$129.90;$129.90;02/19/2024
8;977478;760237046;"CS-COMMSCO 760237046 DISCRETE DISTRIBUTION MODULE PANEL; SL; STP; 1U; 24 PORT CPP-SDDM-SL-1U-24";3;$54.94;$164.82;02/19/2024
9;10097560;760238139;"CS-UNIPRIS 760238139 UNIPRISE SLX MODULAR RJ45 JACKCAT 6 SHIELDED W/OUT DUST CVR USL600-SHLD; BLK";50;$9.94;$497.00;02/19/2024
10;10183539;6500FE 010U500;"BELDEN 6500FE 010U500 BELD 6500FE-010U500 CABLE; SECURITY/COMMERCIAL AUDIO| 2C| 300V| BLACK";500;$0.17;$86.35;02/19/2024
'''
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
col_lists  = [columns, columns_voss, columns_default, columns_dlt, quo, default_dict_stock['columns']]
appspace_cols = 'PART_NO #, Detail, Quantity, Unit Price (per month), Contract Total, Renewal Term'


ExtractionPrompt = ExtractionPrompt(Cara=carahasoft_dict,
                                    DLT=dlt_dict, QUO=quo_dict, default=default_dict, raw=default_dict, default_plus=default_dict_stock)
test = 'Extract Item No, PART_NO (MFG), Description, User Count (Qty), Quote Price (unit), Subscription Start Date, Subscription End Date from the data above into a ; separated csv file with   as newline. Do not include header'

trainingText = """        'QUOTE NO:\n10/30/2023\n41495096\nCONFIDENTIAL\n5\nRSU-SMPLE\nRemote Support Concurrent User Cloud, Annual\nBeyondTrust Corporation - RSU-CLOUD\nStart Date: 12/01/2024\nEnd Date: 11/30/2025\n$2,170.36\n10\n$21,703.60\nOM\nOPTION YEAR 1 SUBTOTAL:\n$21,703.60\nOPTION YEAR 2\n'        
        Question: Extract Item No, PART_NO, Description, User Count (Qty), Quote Price (unit), Subscription Start Date, Subscription End Date  from the data above into a ; separated csv file with \n  newline.  Do not include header.
        5;RSU-SMPLE;Remote Support Concurrent User Cloud Annual;10;2170.36;12/01/2024;11/30/2025\n"""



