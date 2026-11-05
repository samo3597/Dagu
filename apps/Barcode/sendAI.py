import variables as var
import logger as log
import json
from typing import List
from google import genai
from google.genai import types
from pydantic import BaseModel, Field

log.setup_logging()
logger = log.get_logger(__name__)

genai_api_key = var.get_env("GENAI_API_KEY")
genai_model = var.get_env("GENAI_MODEL", default='gemini-3.5-flash-lite')

# ---------------------------------------------------------------------------
# 1. Schema-ների սահմանում Single Item-ի և Batch-ի համար
# ---------------------------------------------------------------------------
class NormalizedProduct(BaseModel):
    Barcode: str = Field(description="Մուտքային ID-ն՝ տվյալները նույնականացնելու համար")
    name: str = Field(description="Ստանդարտացված լրիվ անվանումը strictly ըստ Pattern-ի")
    category: str = Field(description="Ստանդարտացված կատեգորիան")
    tax_code: int = Field(description="ԱՏԳ ԱԱ 4-նիշ կոդը")
    is_weighted: bool = Field(description="true եթե կշռովի է, false եթե հատով")
    is_tax: bool = Field(description="true ԱԱՀ-ով հարկվող ապրանք է")
    basic_unit: str = Field(description="Ապրանքի բազային չափման միավորը")
    Basic_coefficient: float = Field(description="Ապրանքի բազային չափման միավորի արժեքը")


class ProductBatchResponse(BaseModel):
    items: List[NormalizedProduct]


# ---------------------------------------------------------------------------
# 2. Strong System Prompt (Կանոններ + Naming Patterns + Few-Shot Examples)
# ---------------------------------------------------------------------------
SYSTEM_INSTRUCTIONS = """
Դուք ապրանքագետ եք: Ձեր խնդիրն է ստանդարտացնել ապրանքների տվյալները:

!!! ԽՍՏԱԳՈՒՅՆՍ ԱՐԳԵԼՎՈՒՄ Է ՀԱԼՈՒՑԻՆԱՑԻԱՆ. ԱՎԵԼԱՑՆԵԼ ՄԻԱՅՆ ԱՅՆ ՏՎՅԱԼՆԵՐԸ, ՈՐՈՆՔ ԿԱՆ ՄՈՒՏՔԱՅԻՆ ՏՎՅԱԼՆԵՐՈՒՄ !!!

ԱՆՎԱՆՄԱՆ ՁԵՎԱԿԵՐՊՄԱՆ ԿԱՆՈՆՆԵՐԸ (NAMING PATTERNS):
1. Ծխախոտային արտադրանք՝
   Pattern: [Ապրանքատեսակ հայերեն] [ԲՐԵՆԴ ՕՐԻԳԻՆԱԼ] [Ենթատեսակ/Համ]
   Օրինակ՝ "Տաքացվող ծխախոտի գլանակներ TEREA Silver", "Ծխախոտ MARLBORO Gold"

2. Սննդամթերք / Ըմպելիքներ՝
   Pattern: [Ապրանքատեսակ հայերեն] [ԲՐԵՆԴ] [Համ/Տեսակ] [Ծավալ/Քաշ]
   Օրինակ՝ "Հյութ SANTAL Ալոճի 1Լ", "Գարեջուր HEINEKEN Շիշ 0.5Լ"

3. Կենցաղային քիմիա / Խնամք՝
   Pattern: [Ապրանքատեսակ հայերեն] [ԲՐԵՆԴ] [Տեսակ] [Ծավալ/Քաշ]
   Օրինակ՝ "Շամպուն PANTENE Pro-V Վերականգնող 400մլ"

ԸՆԴՀԱՆՈՒՐ ԿԱՆՈՆՆԵՐ:
- Բրենդի անունը և ենթատեսակները գրել ՕՐԻԳԻՆԱԼ լեզվով (լատինատառ/ռուսատառ, եթե այդպես է բրենդը)։
- Հայերեն գրել ՄԻԱՅՆ ապրանքատեսակը (օրինակ՝ Շամպուն, Հյութ, Ծխախոտ, Կարագ)։
- tax_code: Ընտրել ամենաճիշտ 4-նիշ ՀՍՏԱԿ կոդը (տաքացվող ծխախոտ՝ 2404, սովորական ծխախոտ՝ 2402, հյութեր՝ 2009, գարեջուր՝ 2203):
- is_tax։ Նշվում է ԱԱՀ-ով հարվող ապրանքների վրա (տաքացվող ծխախոտ՝ true, սովորական ծխախոտ՝ false, հյութեր՝ true, գարեջուր՝ true): 
- basic_unit ու Basic_coefficient։ Եթե ապրանքը բազային միավորով է, դաշտերը թողնում ենք դատարկ։ Օրինակ` 400մլ ծավալով ապրանքի basic_unit։ Լիտր  Basic_coefficient։ 0.4, բայց 1000մլ ծավալով կամ 1000գ քաշով ապրանքի basic_unit-ը ու Basic_coefficient-ը թողնում ենք դատարկ

ՕՐԻՆԱԿՆԵՐ (FEW-SHOT EXAMPLES):
Input: {"Barcode": "1", "name": ["Ծխախոտ TEREA Silver", "TEREA SILVER"], "tax_code": [2404, 2402]}
Output: {"Barcode": "1", "name": "Տաքացվող ծխախոտի գլանակներ TEREA Silver", "tax_code": 2404, "category": "Ծխախոտային արտադրանք", "is_weighted": false, "basic_unit": "", "Basic_coefficient": 0}

Input: {"Barcode": "2", "name": ["Հյութ Սանտալ 0.7լ Խնձոր", "Santal apple 750մլ"], "tax_code": [2009]}
Output: {"Barcode": "2", "name": "Հյութ SANTAL Խնձոր 0.7Լ", "tax_code": 2009, "category": "Ըմպելիքներ", "is_weighted": false, "basic_unit": "լիտր", "Basic_coefficient": 0.75}
"""

# ---------------------------------------------------------------------------
# 3. Մշակման ֆունկցիա (Batch Processing Function)
# ---------------------------------------------------------------------------
client = genai.Client(api_key=genai_api_key)


def process_product_batch(batch_items: list) -> List[NormalizedProduct]:
    prompt = f"Մշակիր հետևյալ ապրանքների խումբը:\n{json.dumps(batch_items, ensure_ascii=False)}"

    try:
        response = client.models.generate_content(
            model=genai_model,
            contents=prompt,
            config=types.GenerateContentConfig(
                system_instruction=SYSTEM_INSTRUCTIONS,
                response_mime_type="application/json",
                response_schema=ProductBatchResponse,
                temperature=0.0,  # Strict / Deterministic արդյունքի համար
            ),
        )

        parsed_res = ProductBatchResponse.model_validate_json(response.text)
        return parsed_res.items
    except genai.errors.ServerError as e:
        logger.error(f"Server error while processing batch: {e}")
        raise e
    except Exception as e:
        logger.error(f"Error processing batch: {e}")
        raise e


def process_product():
    with open('files/Step1.json', 'r') as f:
        logger.info("Read Step1.py")
        data = json.load(f)

    logger.info("Starting process_product_batch")
    NormalizedProducts = process_product_batch(data)
    data_AI = [i.model_dump() for i in NormalizedProducts]
    logger.info("End process_product_batch")
    
    with open('files/Step2.json', 'w') as f:
        logger.info("Writing Step2.py")
        json.dump(data_AI, f)

def main():
    logger.info("Starting main")
    process_product()
    logger.info("End main")


if __name__=='__main__':
    main()