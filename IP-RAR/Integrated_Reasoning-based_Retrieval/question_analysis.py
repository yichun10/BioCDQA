import re
import json
import os
from tqdm import tqdm
import openai

os.environ["OPENAI_API_TYPE"] = "azure"
os.environ["OPENAI_API_VERSION"] = ""
os.environ["OPENAI_API_BASE"] = ""
os.environ["OPENAI_API_KEY"] =  ""


# openai.api_type = "azure"
# openai.api_version = ""
# openai.api_base = ""
# openai.api_key =  ""


with open('BioCDQA.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

results_list = []

for item in tqdm(data):
    question = item['question']

    system_prompts = """
    Based on the given question, help me identify the keywords in the question.
    Keywords: These are the entities, subjects, or objects related to the question. For example, in the question 'What is the genetic cause of Freidreich's ataxia?', the key term is 'Freidreich's ataxia.'
    Generate related synonyms based on keywords to expand the query vocabulary.
    Additionally, based on the question, generate a plausible virtual answer that could hypothetically address the question, even if it is not grounded in actual data.
    Please provide the response in the following JSON format:
    {
        "key_terms": ["key_term_1","key_term_2"],
        "key_terms synonyms": {
            "key_term_1": ["",""],
            "key_term_2": ["",""]
        },
        "virtual_answer": "Your generated virtual answer here."
    }
    """

    try:
        response = openai.ChatCompletion.create(
            engine="gpt-4o-mini",
            response_format={
                "type": "json_object"
            },
            messages=[
                {"role": "system", "content": system_prompts},
                {"role": "user", "content": f"\nThe question is: " + f"{question}"}
            ],
            temperature=0.5,
            max_tokens=800,
            top_p=0.95,
            frequency_penalty=0,
            presence_penalty=0
        )

        result = response['choices'][0]['message']['content']

        try:
            result_json = json.loads(result)
        except json.JSONDecodeError:
            cleaned_json_string = re.sub(r'^```json|```$', '', result.strip())
            result_json = json.loads(cleaned_json_string)

    except Exception as e:
        result_json = {
            "key_terms": ["key_term_1","key_term_2"],
            "key_terms synonyms": {
                "key_term_1": ["",""],
                "key_term_2": ["",""]
            },
            "virtual_answer": "Your generated virtual answer here."
        }

    output_item = {
        "question": question,
        "analysis": result_json
    }

    results_list.append(output_item)

with open('question_analysis_output.json', 'w', encoding='utf-8') as outfile:
    json.dump(results_list, outfile, indent=4, ensure_ascii=False) 