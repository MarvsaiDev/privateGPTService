import asyncio
import os
from functools import partial
from typing import List

import openai
from privateGPT.util import load_yaml_env
from langchain.docstore.document import Document
import re
from prompt_res.list_prompts import get_format_definitions
from prompt_res.prompts import columns, columns_dlt, ExtractionPrompt
col_lists = get_format_definitions('columns')

if not load_yaml_env():
    print("Could not load .env file or it is empty. Please check if it exists and is readable.")

openai.api_base = os.environ['OPENAI_API_BASE']
openai.api_version = os.environ['OPENAI_API_VERSION']
openai.api_key = os.environ['OPENAI_API_KEY']
openai.api_type = "azure"
model_type = os.environ.get('MODEL_TYPE')
model_subtype = os.environ.get('MODEL_SUBTYPE', 'gpt-35-16k' )

# openai.api_base = "https://cucmcontrol.openai.azure.com/"
# openai.api_version = "2023-07-01-preview"
# openai.api_key = 'd20fc51ea79c4cceba78786a4be31871'

message_text = [{"role":"system","content":"You are an AI assistant that helps people find information."},{"role":"user","content":"hi how are you?"},{"role":"assistant","content":"Hello! As an AI assistant, I don't have feelings like humans do, but I'm always here to help you find information. How can I assist you today?"}]
unicode_space_pattern = re.compile(r'[\u00A0\u2000-\u200B\u202F\u205F\u3000]+')
def replace_sep_text(doc:Document, sep=';', oksep='|') -> Document:
    doc.page_content = doc.page_content.replace(sep, oksep)
    # Replace all Unicode space characters with ASCII space using compiled regex pattern
    ascii_string = unicode_space_pattern.sub(' ', doc.page_content)
    doc.page_content = ascii_string
    return doc
def _extract_page_number_meta(s: Document) -> int:
    # Use regex to find the page number in the string
    page = s.metadata.get('page', None)
    if isinstance(page, int) or (isinstance(page, str) and page.isdigit()):
        # If a page number is found, return it as an integer
        return int(page)+1
    else:
        # If no page number is found, return a large number to sort this item last
        return float('inf')
def sort_page_content(docs:List[Document]):
s    docs = sorted(docs, key=_extract_page_number_meta)
    list(map(replace_sep_text, docs))
    return ''.join([doc.page_content +'\n\n' for doc in docs ])

def query_valid_time(docs:List[Document], oneshot=None):
    content = sort_page_content(docs)
    result = question_openai(q=f'Extract "Time quote is valid for" from the following "{content}". Output using a ; sep csv list. Do include header.', oneshot=None)
    print(result)
    return result

def query_docs(docs:List[Document], oneshot=None):
    content = sort_page_content(docs)
    result = question_openai(q=f'Extract "Total Quote Amount; Quote Expiry date (Valid Until); Invoice Date" from the following "{content}". Output using a ; sep csv list. Do include header.', oneshot=None)
    print(result)
    return result
def question_openai(q, oneshot=None,temp=0.01, maxTok=2048,top_p=0.01):
    listMessages = [{"role": "system", "content": 'You extract structured information as a ; seperated CSV file from unstructured text.'+oneshot if oneshot else ''}]

    listMessages.append({"role": "user", "content": q})
    completion = openai.ChatCompletion.create(
      engine=model_subtype,
      messages = listMessages,
      temperature=temp,
      max_tokens=maxTok,
      top_p=top_p,
      frequency_penalty=0,
      presence_penalty=0,
      stop=None
    )
    print(completion.choices[0].message.content)
    return completion.choices[0].message.content


#
async def most_similar_heading(columns_in_pdf, cols =  col_lists):
    generated_strings = ''
    for j, col in enumerate(cols):
        generated_strings+=(f"{j + 1}. {col}\n")
    r = asyncio.run(question_openai(f'''which number {generated_strings} is most simlar to this list "{columns_in_pdf}". Return a single digit only. "'''))
    print(generated_strings)
    print(r)
    if str(r[0]).isdigit():
        return cols[int(r[0])]
    else:
        return columns_in_pdf

    # r = asyncio.run(question_openai('''Extract the main table headers starting from product code as a comma separated list
    # "Page 1 of 2
    # Email:
    # Prepared By:
    # Expiration Date:
    # Effective Date:
    # Quote Number:
    # VisionOSS
    # BUDGETARY QUOTATION
    # Prepared For:
    # TBD
    # EK2-3086-2-Budgetary
    # February 12, 2024
    # February 29, 2024
    # Elizabeth Kallay
    # elizabeth.kallay@voss-solutions.com
    # Products and Services Quoted
    # Product
    # Line Description
    # Price
    # Base
    # Term
    # Unit Price
    # Discount
    # Unit Disc. Price
    # Quantity
    # Months
    # Offered Price
    # 1 VOSS-AUTOMATE
    # VOSS Automate Software License
    # Subscription. The License
    # supports multi-vendor solutions
    # however excludes the VOSS
    # Automate Hybrid model.
    # PUPM 2024-03-01 -
    # 2025-02-28
    # 2.84
    # 74.30%
    # 0.7300
    # 71000
    # 12
    # 621,960.00
    # Notes: PUPM (Per-User-Per-Month), PTPM (Per-uniT-Per-Month), PU (Per-User),
    # PT (Per-uniT), PD (Per-Day), PH (Per-Hour), FIX (Fixed-Fee)
    # Total
    # USD 621,960.00
    # Payment Terms
    # License subscription and maintenance support fees are payable in advance.
    # Professional and Training Services fees are payable upon order.
    # Payment term: 30 days from VisionOSS invoice.
    # Terms & Conditions
    # All software licenses, maintenance support services and professional services purchased under this quotation are
    # governed by the terms and conditions of the VisionOSS Master Service Agreement available for download at
    # https://www.voss-solutions.com/media/file/misc/VOSS_EULA_SLA_Services_Terms.pdf.
    #  "
    # '''))

p = ExtractionPrompt['default']
shot = f'''{p['prompt']}\n \'QUOTATION\nDate:\n02/19/2024\nQuote #:\nQ00BXPP8\nCustomer:\n268195\n2301 Patriot Blvd.  Glenview,  IL 60026\nSEWP RFQ 292203\nCustomer\nADVANCED COMPUTER CONCEPTS\n7927 JONES BRANCH DR STE 600 N\nMCLEAN, VA 22102\nPhone: --\nFax: --\nAnixter Inc. (a WESCO Company)\nSend Purchase Orders to Anixter Inc.\nLine\nQuantity\nPart Number and Description\nUM\nUnit Price\nExtended Price\n1\n1\n496242\nBRADY CORP BMP51\nBMP51 MOBILE PRINTER W/LI-ION BAT PACK,AC ADAP/BAT\nCHARGER\nLead Time: in stock\nShipping Location: CHICAGO,IL (102)\nEA\n381.32\n381.32\n2\n2\nNon-Stock\nBRADY CORP M4C-500-422\nAGGRESSIVE ADHESIVE MULTI-PURPOSE POLYESTER\nLABELSWITH RIBBON FOR BMP4\nBMP51, M511 PRINTERS - 0.5"\nLead Time: in stock with vendor\nPart Availability: ***replacement for MC-500-422\nShipping Location: CHICAGO,IL (102)\nEA\n31.69\n63.38\n3\n2\nNon-Stock\nBRADY CORP M4C-1000-422\nAGGRESSIVE ADHESIVE MULTI-PURPOSE POLYESTER\nLABELSWITH RIBBON FOR BMP4\nBMP51, M511 PRINTERS - 1"\nLead Time: in stock with vendor\nPart Availability: ***replacement for MC1-1000-422\nShipping Location: CHICAGO,IL (102)\nEA\n50.01\n100.02\n4\n4\n10403521\nBRADY CORP M4-143-427\nCARTRIDGE OF 200 LABELS 1.25" X 1" WHITE\nLead Time: in stock with vendor\nShipping Location: CHICAGO,IL (102)\nEA\n44.60\n178.40\nPage 1 of 3\nquote-en-US Version 2.5.1\nBY ACCEPTING THIS QUOTE, YOU AGREE THAT THE TERMS AND CONDITIONS OF SALE PUBLISHED AT WWW.ANIXTER.COM/TERMSANDCONDITIONS ARE EXPRESSLY INCORPORATED INTO AND\nSHALL GOVERN THIS TRANSACTION.\nWesco may charge you storage and transportation fees if you do not take possession or accept delivery of the above products within ninety (90) days or agreed upon terms from such\nproducts being available for delivery or pick-up
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


gpt3_call = partial(question_openai, oneshot = shot, temp=0.05, maxTok=2048, top_p=0.1)

if __name__ == '__main__':

    print(p)



    r = gpt3_call(f'{p["prompt"]} \n \'QUOTATION\nDate:\n02/19/2024\nQuote #:\nQ00BXPP8\nCustomer:\n268195\n2301 Patriot Blvd.  Glenview,  IL 60026\nSEWP RFQ 292203\nAnixter Inc. (a WESCO Company)\nSend Purchase Orders to Anixter Inc.\nLine\nQuantity\nPart Number and Description\nUM\nUnit Price\nExtended Price\n5\n2\nNon-Stock\nBRADY CORP M4-60-428\nMETALIZED SOLVENT RESISTANT MATTE GRAY POLYESTER\nLABELS WITH RIBBON FOR\nBMP41 BMP51 M511 PRINTERS - 2"\nX 1"\nLead Time: in stock with vendor\nShipping Location: CHICAGO,IL (102)\nEA\n61.31\n122.62\n6\n4\n10390185\nBRADY CORP M4-51-427\n2.50"WX1.00"H SELF-LAMINATING;VINYL LABEL FOR BMP51\n110; LABEL CARTRIDGE WHIT\nLead Time: in stock\nShipping Location: CHICAGO,IL (102)\nEA\n42.98\n171.92\n7\n1\n423353-PK\nPLATINUM 105-X20\nEZ-RJ45 SHIELDED CONNECTOR 100/PK\nLead Time: in stock\nShipping Location: CHICAGO,IL (102)\nPK\n129.90\n129.90\n8\n3\n977478\nCS-COMMSCO 760237046\nDISCRETE DISTRIBUTION MODULE PANEL, SL, STP, 1U, 24\nPORT CPP-SDDM-SL-1U-24\nLead Time: 2-3 weeks ARO\nShipping Location: CHICAGO,IL (102)\nEA\n54.94\n164.82\n9\n50\n10097560\nCS-UNIPRIS 760238139\nUNIPRISE SLX MODULAR RJ45 JACKCAT 6 SHIELDED W/OUT\nDUST CVR USL600-SHLD, BLK\nLead Time: in stock\nShipping Location: CHICAGO,IL (102)\nEA\n9.94\n497.00\n10\n500\n10183539\nBELDEN 6500FE 010U500\nBELD 6500FE-010U500 CABLE, SECURITY/COMMERCIAL\nAUDIO; 2C; 300V; BLACK\nLead Time: 45 days ARO if no stock\nPart Availability: 1000ft in stock with Belden\nShipping Location: CHICAGO,IL (102)\nFT\n0.17\n86.35\nPage 2 of 3\nquote-en-US Version 2.5.1\nBY ACCEPTING THIS QUOTE, YOU AGREE THAT THE TERMS AND CONDITIONS OF SALE PUBLISHED AT WWW.ANIXTER.COM/TERMSANDCONDITIONS ARE EXPRESSLY INCORPORATED INTO AND\nSHALL GOVERN THIS TRANSACTION.\nWesco may charge you storage and transportation fees if you do not take possession or accept delivery of the above products within ninety (90) days or agreed upon terms from such\nproducts being available for delivery or pick-up\'\n\n A:\n')
    print('Response:\n'+r)