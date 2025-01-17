import json
import os
import openai
import time
from tqdm import tqdm

os.environ["OPENAI_API_TYPE"] = "azure"
os.environ["OPENAI_API_VERSION"] = ""
os.environ["OPENAI_API_BASE"] = ""
os.environ["OPENAI_API_KEY"] =  ""
# openai.api_type = "azure"
# openai.api_version = ""
# openai.api_base = ""
# openai.api_key =  ""

similarities = []
with open('', 'r') as file: # Path to the model_generation_output.json file
    test_datas = json.load(file)

with open('', 'r') as file: # Path to the BioCDQA.json file
    data = json.load(file)

results = []  
for record, ceping_data in tqdm(zip(test_datas, data)):
    answer = ceping_data['ideal_answer']
    sentence1 = ""

    if isinstance(answer, list):
        sentence1 = " ".join(answer)
    elif isinstance(answer, str):
        sentence1 = answer
    else:
        print("mistake")

    sentence2 = record['final_answer']
    question = ceping_data['question']
    try:
        prompt = f"""
        The question is: {question}
        The standard answer is: {sentence1}
        The answer generated by the LLM is: {sentence2}

        You need to score the answers generated by the LLM based on the question and the standard answer. Use a scale from 0 to 5, where:

        5 points: The LLM’s answer fully addresses the question, covers all core elements of the standard answer, and conveys the same meaning without any irrelevant information.

        4 points: The LLM’s answer addresses the question well, covers most core elements of the standard answer, but has minor deviations, omissions, or includes a small amount of irrelevant information.

        3 points: The LLM’s answer addresses the question but has significant deviations or omissions from the core elements of the standard answer. It also contains noticeable irrelevant information that affects clarity.

        2 Points: The LLM’s answer partially addresses the question but has major deviations or omissions from the core elements of the standard answer, or includes a substantial amount of irrelevant information.

        1 Point: The LLM’s answer barely addresses the question and has severe deviations or omissions from the core elements of the standard answer, or includes a large amount of misleading or irrelevant information.

        0 points: The LLM’s answer fails to address the question or conveys a meaning completely opposite to the standard answer. It may also be entirely irrelevant or incomprehensible.

        Note: Only the numerical part of the score needs to be output.

        """ 
        response = openai.ChatCompletion.create(
            engine="gpt-4o",
            # response_format={"type": "json_object"},
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": f"{prompt}"}
            ],
            temperature=0,
            max_tokens=100,
            top_p=0.95,
            frequency_penalty=0,
            presence_penalty=0
        )
        sentence = response['choices'][0]['message']['content']
        value = int(sentence)
        similarities.append(value)
        results.append({
            "sentence1": sentence1,
            "sentence2": sentence2,
            "value": value
        })

    except Exception as e:
        print(e)
        similarities.append(0)

average_similarity = sum(similarities) / len(similarities)
print("GPT4 Average Similarity:", average_similarity)


with open('gpt4o_score_output.json', 'w') as file:
    json.dump(results, file, indent=4)

