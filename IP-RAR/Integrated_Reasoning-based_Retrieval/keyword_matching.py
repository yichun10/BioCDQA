import json
import ahocorasick
from tqdm import tqdm
import random
results = []

def load_json_file(filename):
    with open(filename, 'r', encoding='utf-8') as file:
        return json.load(file)

def build_aho_corasick_trie(key_terms, key_terms_synonyms):
    A = ahocorasick.Automaton()
    term_to_key = {}  
    for term in key_terms:
        synonyms = key_terms_synonyms.get(term, [])
        all_terms = [term] + synonyms
        for t in all_terms:
            A.add_word(t, term)  
            term_to_key[t] = term  
    A.make_automaton()
    return A, term_to_key

def process_question(input_item, search_text, output_filename):
    key_terms = input_item['analysis']['key_terms']
    key_terms_synonyms = input_item['analysis']['key_terms synonyms']
    question = input_item['question']

    A, term_to_key = build_aho_corasick_trie(key_terms, key_terms_synonyms)

    key_term_matches = {term: {i: [] for i in range(len(key_terms), 0, -1)} for term in key_terms}

    # Step 1: Categorize matching blocks for each key_term
    for i, obj in enumerate(search_text):
        text = obj.get('content', "")
        if isinstance(text, str):
            matched_key_terms = set()  

            for end_index, matched_term in A.iter(text):
                matched_key_term = term_to_key[matched_term]
                matched_key_terms.add(matched_key_term)  

            if matched_key_terms:
                match_count = len(matched_key_terms)
                text_info = {
                    'text': text,
                    'location': i,
                    'matched_key_terms': list(matched_key_terms),
                    'matched_key_terms_count': match_count
                }
                
                
                for term in matched_key_terms:
                    key_term_matches[term][match_count].append(text_info)

    # Step 2: Select up to 10 blocks for each key_term
    final_matched_texts = []
    for term, match_dict in key_term_matches.items():
        selected_texts = []

        # Priority 1: Select 5 blocks with the most matched key_terms
        for match_count in sorted(match_dict.keys(), reverse=True):
            selected_texts.extend(match_dict[match_count][:5 - len(selected_texts)])
            if len(selected_texts) >= 5:
                break

        # Priority 2: Select 5 blocks with fewer matched key_terms
        if len(selected_texts) < 10:
            for match_count in sorted(match_dict.keys()):
                if match_count == max(match_dict.keys()):
                    continue  # Skip the most matched key_terms from Priority 1
                selected_texts.extend(match_dict[match_count][:10 - len(selected_texts)])
                if len(selected_texts) >= 10:
                    break

        selected_texts = selected_texts[:10]  # Ensure exactly 10 matches per term
        final_matched_texts.extend(selected_texts)

    # Step 3: Merge duplicate blocks across key_terms
    unique_matches = {json.dumps(item, sort_keys=True): item for item in final_matched_texts}
    final_matched_texts = list(unique_matches.values())

    # Step 4: Ensure a maximum of 20 blocks in the final results
    final_matched_texts = final_matched_texts[:20]

    if final_matched_texts:
        result = {
            'question': question,
            'key_terms': key_terms,
            'key_terms_synonyms': key_terms_synonyms,
            'matched_texts': final_matched_texts  
        }
        results.append(result)

        with open(output_filename, 'w') as outfile:
            json.dump(results, outfile, indent=4, ensure_ascii=False)
    
    return f"Saved results for question: {question}"

def find_matches(input_json, search_text, output_filename):
    with open(output_filename, 'w') as f:
        pass  
    
    for input_item in tqdm(input_json, desc="Processing questions"):
        process_question(input_item, search_text, output_filename)

    return f"Processing completed and saved results to {output_filename}"

input_json_file = 'question_analysis_output.json'  # Path to your input JSON file
search_text_file = 'all_text_chunks.json'  # Path to the text to search file

input_json = load_json_file(input_json_file)
search_text = load_json_file(search_text_file)
output_json_file = '' # Path to your output JSON file
find_matches(input_json, search_text, output_json_file)


