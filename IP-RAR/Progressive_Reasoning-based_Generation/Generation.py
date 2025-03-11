import json
import re
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import List, Dict
from openai import OpenAI
from tqdm import tqdm
import os

client = OpenAI(api_key="<DeepSeek API Key>", base_url="https://api.deepseek.com")

def load_json(file_path: str) -> List:
    with open(file_path, 'r') as file:
        return json.load(file)

def can_answer_question(context: str, question: str) -> bool:
    prompt = f"Context:\n{context}\n\nQuestion: {question}\n\nIf the text excerpt allows the question to be correctly answered as specified, respond with 'yes'. Otherwise, respond 'no'."
    response = client.chat.completions.create(
        model="deepseek-chat",
        messages=[
            {"role": "system", "content": "Evaluate if the context can answer the question."},
            {"role": "user", "content": prompt},
        ],
        stream=False
    )
    result = response.choices[0].message.content.lower()
    return result == "yes"

def evaluate_support_level(context: str, question: str, answer: str) -> int:
    prompt = f"Context:\n{context}\n\nQuestion: {question}\n\nAnswer: {answer}\n\nScore the relevance of each text block, question, and answer. The most relevant one is scored 100 points, while those that are completely unrelated or have completely opposite meanings are scored 0 points. Other scores may be deducted at discretion. Just need to output the final score."
    response = client.chat.completions.create(
        model="deepseek-chat",
        messages=[
            {"role": "system", "content": "Rate the support level for the answer."},
            {"role": "user", "content": prompt},
        ],
        stream=False
    )
    content = response.choices[0].message.content

    match = re.search(r'\d+', content)
    support_score = int(match.group()) if match else 0
    return support_score

def generate_answer(context: str, question: str) -> str:
    prompt = f"Context:\n{context}\n\nQuestion: {question}\n\nAnswer:"
    response = client.chat.completions.create(
        model="deepseek-chat",
        messages=[
            {"role": "system", "content": "You need to answer question based on the context."},
            {"role": "user", "content": prompt},
        ],
        stream=False
    )
    return response.choices[0].message.content

def generate_final_answer(final_answers: str, question: str) -> str:
    prompt = f"Multiple Answers:\n{final_answers}\n\nQuestion: {question}\n\nYou need to integrate multiple answers to respond to the question. Please answer concisely in one or two sentences."
    response = client.chat.completions.create(
        model="deepseek-reasoner",
        messages=[
            {"role": "system", "content": "You need to answer concisely by integrating multiple answers."},
            {"role": "user", "content": prompt},
        ],
        stream=False
    )
    return response.choices[0].message.content

def multi_stage_selection(score_entry: List[Dict], analysis_entry: Dict) -> Dict:
    question = analysis_entry["question"]
    all_texts = sorted([text for item in score_entry for text in item["texts"]], key=lambda x: x['score'], reverse=True)

    selected_texts = []
    for text_entry in all_texts:
        context = text_entry["text"]
        if can_answer_question(context, question):
            selected_texts.append(text_entry)
        if len(selected_texts) >= 10:
            break

    if not selected_texts:
        selected_texts = all_texts[:5]

    support_scores = []
    for entry in selected_texts:
        individual_answer = generate_answer(entry["text"], question)
        support_score = evaluate_support_level(entry["text"], question, individual_answer)
        
        support_scores.append({
            "text": entry["text"],
            "individual_answer": individual_answer,
            "original_score": entry["score"],
            "support_score": support_score
        })

    top_support_texts = sorted([text for text in support_scores if text["support_score"] > 50], 
                               key=lambda x: x["support_score"], 
                               reverse=True)[:5]

    final_context = "\n\n".join([entry["text"] for entry in top_support_texts])
    final_answers = " ".join([entry["individual_answer"] for entry in top_support_texts])
    final_answer = generate_final_answer(final_answers, question)

    return {
        "question": question,
        "answer": final_answer,
        "final_context": final_context,
        "top_individual_answers": final_answers,
        "selected_texts": [{"text": entry["text"], "score": entry["score"]} for entry in selected_texts],
        "support_scores": support_scores,
        "top_support_texts": [{"text": entry["text"], "individual_answer": entry["individual_answer"], "support_score": entry["support_score"]} for entry in top_support_texts]
    }

def process_entry(index: int, score_entry: Dict, analysis_entry: Dict) -> Dict:
    result = multi_stage_selection(score_entry, analysis_entry)
    result["index"] = index
    return result

def main(score_data_path: str, output_file_path: str):
    score_data = load_json(score_data_path)


    results = [None] * len(score_data)

    with ThreadPoolExecutor(max_workers=32) as executor:
        futures = {executor.submit(process_entry, i, score_data[i]): i for i in range(len(score_data))}

        for future in tqdm(as_completed(futures), total=len(score_data), desc="Processing entries"):
            result = future.result()
            index = result["index"]
            results[index] = {
                "question": result["question"],
                "answer": result["answer"],
                "final_context": result["final_context"],
                "top_individual_answers": result["top_individual_answers"],
                "selected_texts": result["selected_texts"],
                "support_scores": result["support_scores"],
                "top_support_texts": result["top_support_texts"]
            }

    with open(output_file_path, 'w') as output_file:
        json.dump(results, output_file, indent=4, ensure_ascii=False)
    print(f"Results saved to {output_file_path}")


score_json_path = '/path/to/aggregator_output.json'
output_json_path = '/path/to/output_results.json'

main(score_json_path, output_json_path)
