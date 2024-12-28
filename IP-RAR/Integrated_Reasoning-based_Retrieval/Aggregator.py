import json

w_S = 5
w_M = 3
w_R = 1

S_sim_max = 1
M_max = 5
R_max = 10

def extract_pids_and_texts_from_item(item, source_type="matched_texts", source_file=""):
    if source_type == "matched_texts":
        return [(ctx.get("pid", ""), ctx.get("text", ""), source_file, None) for ctx in item.get("matched_texts", [])]
    elif source_type == "ctxs":
        return [(ctx.get("pid", ""), ctx.get("text", ""), source_file, ctx.get("score", 0.0)) for ctx in item.get("ctxs", [])]
    else:
        raise ValueError("Unknown source_type")

def calculate_score(block, total_blocks_in_document, max_similarity_score):
    if block["similarity_score"] is None:
        S_sim_i = 0.0
    else:
        S_sim_i = float(block["similarity_score"])
    
    M_i = len(block["sources"])
    R_i = total_blocks_in_document
    
    S_i = (w_S * (S_sim_i / max_similarity_score)) + (w_M * (M_i / M_max)) + (w_R * (R_i / R_max))
    
    return S_i

def load_json(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        return json.load(f)

file_sources = [
    ('', "matched_texts"), # Path to keyword_matching.py output JSON file
    ('', "ctxs"), # Path to retrieval on the text based on the query.
    ('', "ctxs"), # Path to retrieval on the abstract based on the query.
    ('', "ctxs"), # Path to retrieval on the text based on the virtual answer.
    ('', "ctxs") # Path to retrieval on the abstract based on the virtual answer.
]

json_data = [load_json(file_path) for file_path, _ in file_sources]

max_length = max(len(data) for data in json_data)

merged_results = []

for i in range(max_length):
    combined_entries = {}
    for (file_path, source_type), data in zip(file_sources, json_data):
        if i < len(data):
            entries = extract_pids_and_texts_from_item(data[i], source_type, file_path)
            for pid, text, source, score in entries:
                if pid not in combined_entries:
                    combined_entries[pid] = {}
                if text not in combined_entries[pid]:
                    combined_entries[pid][text] = {"sources": set(), "similarity_score": score}
                combined_entries[pid][text]["sources"].add(source)

    merged_item = []
    for pid, texts in combined_entries.items():
        text_list = []
        for text, details in texts.items():
            score = calculate_score(details, len(texts), S_sim_max)
            text_list.append({
                "text": text,
                "sources": list(details["sources"]),
                "score": score
            })
        merged_item.append({"pid": pid, "texts": text_list})
    merged_results.append(merged_item)

output_file = '' # Path to output file.
with open(output_file, 'w', encoding='utf-8') as f:
    json.dump(merged_results, f, ensure_ascii=False, indent=4)

print(f"Results saved to {output_file}")
