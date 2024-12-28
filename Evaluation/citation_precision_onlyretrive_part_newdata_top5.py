import json

def calculate_citation_precision_recall(jsonA, jsonB):

    total_precision = 0
    total_recall = 0
    num_questions = len(jsonA)

    for i in range(num_questions):
        true_citations = set(jsonA[i].get("documents_pid", [])) # Get the true citations by extracting "documents_pid"
        retrieved_docs = []
        for entry in jsonB[i]:
            pid = entry.get("pid", "")
            retrieved_docs.append({"pid": pid})

        predicted_citations = {d['pid'] for d in retrieved_docs} # Get the predicted citations by extracting "pid"

        correct_citations = true_citations.intersection(predicted_citations) 

        if len(predicted_citations) == 0:
            precision = 0.0
        else:
            precision = len(correct_citations) / len(predicted_citations)

        if len(true_citations) == 0:
            recall = 0.0
        else:
            recall = len(correct_citations) / len(true_citations)


        total_precision += precision
        total_recall += recall

    avg_precision = total_precision / num_questions if num_questions > 0 else 0
    avg_recall = total_recall / num_questions if num_questions > 0 else 0
    avg_f1_score=2*(avg_precision*avg_recall)/(avg_recall+avg_precision)

    return avg_precision, avg_recall, avg_f1_score


def load_json_file(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        return json.load(f)

jsonA_file = '' # Path to the BioCDQA.json file
jsonB_file = '' # Path to the model_retrieval_output.json file
jsonA_data = load_json_file(jsonA_file)
jsonB_data = load_json_file(jsonB_file)


precision, recall, f1_score = calculate_citation_precision_recall(jsonA_data, jsonB_data)

print(f"Precision: {precision:.4f}")
print(f"Recall: {recall:.4f}")
print(f"F1 Score: {f1_score:.4f}")


