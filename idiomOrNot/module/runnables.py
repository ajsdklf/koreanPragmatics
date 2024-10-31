from openai import OpenAI
from pydantic import BaseModel, Field
from typing import List

client = OpenAI()

class PragmaticMeaning(BaseModel):
    idiom: str = Field(description="The idiom being explained")
    pragmatic_meaning: str = Field(description="The pragmatic meaning of the idiom")
    caution: str = Field(description="Caution about using the idiom, e.g., potential offensiveness")
    examples: List[str] = Field(description="3 examples of idiomatic usage - Must be careful to not offend caution you provided")

    class Config:
        extra = "forbid"

class Scenario_Generated(BaseModel):
    is_right: bool = Field(description="Whether the idiom is used correctly in the conversation")
    overall_context: str = Field(description="Overall context of the conversation")
    idiom: str = Field(description="The idiom being used")
    conversation_including_idiom: List[str] = Field(description="7-sentence conversation with the idiom in the 7th sentence")
    explanation: str = Field(description="Explanation of correct or incorrect idiom usage")
    other_expressions: List[str] = Field(description="3 alternative expressions with similar meaning")
    follow_up_conversation: List[str] = Field(description="5-sentence follow-up conversation - Conversation right after the idiom usage")
    
    class Config:
        extra = "forbid"

PRAGMATIC_EXTRACTOR_SYSTEM_PROMPT = """
Analyze the given idiom and provide:
1. The idiom itself
2. Its pragmatic meaning - has to inclde the context to use the idiom properly 
3. Usage caution (if any)
4. 3 examples of correct usage - Must be careful to not offend caution you provided
Respond in JSON format matching the PragmaticMeaning model.

Think step by step to ensure that you have correctly understood and analyzed the idiom.
"""

SCENARIO_GENERATOR_PROMPT = """
Create a scenario for the idiom "{idiom}". The usage should be {is_appropriate}. If you are generating a scenario for incorrect usage, you must take into account the pragmatic meaning and caution of the following:
<pragmatic_meaning>
{pragmatic_meaning}
</pragmatic_meaning>
<caution>
{caution}
</caution>

Your answer must include: 
---
1. Whether the usage is correct (is_right)
2. Overall context - This should not include if the idiom is used correctly or incorrectly
3. The idiom
4. 7-sentence conversation (idiom in 6th or 7th)
5. Explanation of usage
6. 3 alternative expressions
7. 5-sentence follow-up conversation - Conversation right after the idiom usage. This must show what was wrong with the idiom usage if it was used incorrectly.
Ensure all elements are present and properly formatted.
---
"""

EXTRACTOR_INSTRUCTION = """
You will be given the scenario which shows the idiomatic use of an idiom. Your task is to extract the following informations from the given scenario:
1. is_right (boolean)
2. overall_context
3. idiom
4. conversation_including_idiom (7 sentences) - Conversation including the idiom usage in the 6th or 7th sentence
5. explanation
6. other_expressions (3 alternatives)
7. follow_up_conversation (5 sentences) - Conversation right after the idiom usage
Respond in JSON format matching the Scenario_Generated model.

Think step by step to ensure that you have extracted all the informations correctly.
"""

def extract_pragmatic_meaning(idiom: str) -> PragmaticMeaning:
    extraction_response = client.beta.chat.completions.parse(
        model="gpt-4o-2024-08-06",
        messages=[
            {"role": "system", "content": PRAGMATIC_EXTRACTOR_SYSTEM_PROMPT},
            {"role": "user", "content": idiom}
        ],
        response_format=PragmaticMeaning
    )
    return extraction_response.choices[0].message.parsed

def generate_scenario(pragmatic_meaning: PragmaticMeaning, is_appropriate: bool) -> Scenario_Generated:
    scenario_response = client.chat.completions.create(
        model='o1-mini',
        messages=[
            {"role": "user", 'content': SCENARIO_GENERATOR_PROMPT.format(
                idiom=pragmatic_meaning.idiom,
                is_appropriate='correct' if is_appropriate else 'incorrect',
                pragmatic_meaning=pragmatic_meaning.pragmatic_meaning,
                caution=pragmatic_meaning.caution
            )}
        ],
    )
    scenario_response = scenario_response.choices[0].message.content

    formatted_scenario_response = client.beta.chat.completions.parse(
        model="gpt-4o-2024-08-06",
        messages=[
            {"role": "system", "content": EXTRACTOR_INSTRUCTION},
            {"role": "user", "content": scenario_response}
        ],
        response_format=Scenario_Generated
    ).choices[0].message.parsed

    return formatted_scenario_response

def generate_idiom_scenario(idiom: str, is_appropriate: bool) -> Scenario_Generated:
    pragmatic_meaning = extract_pragmatic_meaning(idiom)
    scenario = generate_scenario(pragmatic_meaning, is_appropriate)
    return scenario


def generate_audio(text: str, output_file_path: str, voice: str):
    audio_response = client.audio.speech.create(
        model="tts-1-hd",
        voice=voice,
        input=text
    )
    
    audio_response.stream_to_file(output_file_path)
    