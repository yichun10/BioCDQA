# An LLM-based Transferable and Scalable Retrieval-Augmented Reasoning Framework for Deep Knowledge Mining in Biomedical Literature

## Introduction
Effective knowledge mining synthesizes extensive information into accurate, evidence-based insights, enabling deeper semantic understanding and cross-domain reasoning. Traditional methods often struggle with the complexity of biomedical knowledge, limiting their ability to establish meaningful connections and perform advanced reasoning. While Large Language Models (LLMs) offer significant improvements, they still face challenges in extracting and integrating the vast, diverse, and highly specialized biomedical literature. We present Integrated and Progressive Retrieval-Augmented Reasoning (IP-RAR), a novel LLM-based framework designed to advance biomedical knowledge mining and question answering by integrating sophisticated retrieval and reasoning mechanisms. IP-RAR begins with Integrated Reasoning-based Retrieval, enabling comprehensive exploration of large-scale biomedical literature, followed by Progressive Reasoning-based Generation, which refines relevant contexts to support precise knowledge generation. To evaluate this framework, we introduce the Biomedical Cross-Document Question Answering (BioCDQA) dataset, constructed from extensive knowledge graphs spanning thousands of biomedical publications. Compared to existing datasets, BioCDQA emphasizes multi-hop reasoning and latent knowledge discovery. Experimental results show that IP-RAR significantly outperforms previous methods on BioCDQA and other biomedical question answering benchmarks, achieving superior retrieval performance and knowledge question-answering accuracy. By combining advanced retrieval techniques with progressive reasoning, our work significantly advances biomedical knowledge mining. The IP-RAR framework addresses key challenges by enabling LLMs to extract, synthesize, and reason over complex biomedical insights. This approach not only reveals hidden patterns in biomedical data and literature, enhancing clinical decision-making, but also accelerates scientific discovery in biomedical research through comprehensive large-scale knowledge integration.

<img width="1123" alt="image" src="https://github.com/user-attachments/assets/3bb6a95b-88ba-491b-9817-7b50835c8f43" />
Fig. 1. Overview of the proposed framework for biomedical knowledge mining. (A) Biomedical knowledge sources, such as research papers and user queries, are processed through (B) 
A knowledge mining pipeline that leverages a LLM alongside the Integrated and Progressive Retrieval-Augmented Reasoning approach, designed to generate knowledge graph and precise answers. (C) The outputs enable diverse applications, including drug synergy/antagonism, drug repurposing, precision medicine, bottleneck analysis, research planning, and knowledge transfer.

## Framework of IP-RAR

![ourrag_2](https://github.com/user-attachments/assets/129f67e9-8306-42d5-9fc3-c72a3802075e)

Fig. 2. Framework of Integrated and Progressive Retrieval-Augmented Reasoning. (A) Integrated Reasoning-based Retrieval: The method processes the input question by extracting keywords and generating a virtual answer. Using a multi-level and multi-granularity retrieval strategy, it retrieves relevant text chunks from abstracts and full texts based on the question, keywords, and virtual answer, which are then ranked by an aggregator for relevance and context.
(B) Progressive Reasoning-based Generation: Explanations or self-reflection are used to filter out irrelevant text chunks and select the most relevant ones. These selected chunks are then used to generate individual answers based on the question. Finally, the question and these answers are integrated to produce a comprehensive, accurate final response.

## Biomedical Cross-Document Question Answering Dataset
Our dataset is specifically designed for reasoning-based question answering across multiple documents, consisting of tuples that include the following elements: question, question type, answer, source papers for the answer, and source sentences for the answer. Each tuple contains a natural language question that can be answered using one or more sentences extracted from the answer source papers. The answer source may involve one or more papers, and each answer is composed of several sentences that may originate from a single span or multiple spans across different source papers. The dataset comprises a total of 1,183 question-answer pairs, with a retrieval space of 68,428 papers and over 1.85 million document chunks, providing a rich resource for complex reasoning and retrieval tasks. The construction process is illustrated in Figure 3.
<img width="1123" alt="image" src="https://github.com/user-attachments/assets/36cc711a-0e59-4f53-a2b9-79d1256a2959" />

Fig. 3. Dataset Construction Workflow Diagram.
(A) Data Collection and Processing: The process begins by converting research papers from PDF to markdown (MD) format to facilitate content extraction.
(B) Structured Dataset Generation for Entity-level Knowledge Graph: An LLM is used to extract entities and relationships (Entity1, Relationship, Entity2), which are then standardized to construct an entity-level knowledge graph. This graph supports downstream tasks such as drug repurposing, drug interaction analysis for comorbid conditions, and gene-disease associations.
(C) Structured Dataset Generation for Document-level Knowledge Graph: Summarization is performed using an LLM to extract key aspects such as methods, datasets, and research directions. The resulting document-level knowledge graph facilitates tasks such as research strategic planning and research paper recommendations.
(D) Unstructured Dataset Generation for Multiple Documents: Integration of the entity-level and document-level knowledge graphs produces a comprehensive knowledge graph. This integrated graph enables connections across multiple documents and supports downstream tasks such as content-based factual questioning, research bottleneck analysis, knowledge transfer, trend analysis, and hotspot detection.

## Environments Setting
1、In a conda env with PyTorch / CUDA available clone and download this repository.

2、In the top-level directory run:
```bash
pip install -r requirements.txt
```

## Usage
### Data preparation
1、You can obtain the BioCDQA.json from the BioCDQA dataset folder, which is a dataset containing 1183 question-answer pairs. 

2、You can access the 68,428 biomedical papers within the retrieval space through the [all_document.json](https://drive.google.com/file/d/1Q-Va4mfdgJt7x3Y5QiXtoCbtalDbvqZI/view?usp=sharing), where you can download the full text of each paper and view its metadata, including title, abstract, key_topics, publication details, and urls.

3、You should download the text and convert it into either Markdown or TXT format. We use [Marker]((https://github.com/VikParuchuri/marker.git)) to convert the text into Markdown format. 

4、Split the text into appropriately sized chunks (e.g., complete sentences with 500–1000 tokens per chunk) and save the chunks as all_text_chunks.tsv.
```
tsv_data['id'].append(idx)
tsv_data['text'].append(item['content'])
tsv_data['title'].append(item['pid'])
```
5、The abstract does not need to be downloaded or split. It can be directly obtained from the metadata in all_document.json and converted into all_abstract_chunks.tsv.

### Integrated Reasoning-based Retrieval
#### Download Retrieval Model
We use [Contriever-MSMARCO](https://huggingface.co/facebook/contriever-msmarco) as our retrieval component.

#### Question analysis
Use the LLM to generate keywords and a virtual answer based on the query.
```
cd IP-RAR/Integrated_Reasoning-based_Retrieval
python question_analysis.py
```

#### Generate embeddings for your own data
Generate the embeddings for the full-text.
```
cd IP-RAR/Integrated_Reasoning-based_Retrieval/retrieval_lm
python generate_passage_embeddings.py \
    --model_name_or_path contriever-msmarco \
    --output_dir YOUR_OUTPUT_DIR \
    --passages all_text_chunks.tsv
```

Similarly, generate the embeddings for the abstract.


```
cd IP-RAR/Integrated_Reasoning-based_Retrieval/retrieval_lm
python generate_passage_embeddings.py \
    --model_name_or_path contriever-msmarco \
    --output_dir YOUR_OUTPUT_DIR \
    --passages all_abstract_chunks.tsv
```

#### Multi-Level and Multi-Granularity Retrieval

Perform retrieval on the text based on the query.
```
cd IP-RAR/Integrated_Reasoning-based_Retrieval/retrieval_lm
python passage_retrieval.py \
    --model_name_or_path contriever-msmarco\
    --passages all_text_chunks.tsv \
    --passages_embeddings passages_00_text_ms \
    --query BioCDQA.json  \
    --output_dir YOUR_OUTPUT_FILE \
    --n_docs 20
```
Perform retrieval on the abstract based on the query.
```
python passage_retrieval.py \
    --model_name_or_path contriever-msmarco\
    --passages all_abstract_chunks.tsv \
    --passages_embeddings passages_00_abstract_ms \
    --query BioCDQA.json  \
    --output_dir YOUR_OUTPUT_FILE \
    --n_docs 10
```
Perform retrieval on the text based on the virtual answer.
```
python passage_retrieval_virtual_answer.py \
    --model_name_or_path contriever-msmarco\
    --passages all_text_chunks.tsv \
    --passages_embeddings passages_00_text_ms \
    --query question_analysis_output.json
    --output_dir YOUR_OUTPUT_FILE \
    --n_docs 10
```
Perform retrieval on the text based on the virtual answer.
```
python passage_retrieval_virtual_answer.py \
    --model_name_or_path contriever-msmarco\
    --passages all_abstract_chunks.tsv \
    --passages_embeddings passages_00_abstract_ms \
    --query question_analysis_output.json  \
    --output_dir YOUR_OUTPUT_FILE \
    --n_docs 10
```

Perform keyword matching based on the text.
```
cd IP-RAR/Integrated_Reasoning-based_Retrieval
python keyword_matching.py
```

#### Aggregator
```
cd IP-RAR/Integrated_Reasoning-based_Retrieval
python Aggregator.py
```

### Progressive Reasoning-based Generation
Use the LLM to perform multi-stage validation on the results obtained from the Aggregator and generate the final answer.
```
cd IP-RAR/Progressive_Reasoning-based_Generation
python Generation.py
```


### Evaluation
#### Document Retrieval Performance Evaluation
We employ Mean Precision, Mean Recall, and Mean F-measure to assess the proportion of relevant documents retrieved and the balance between precision and recall. The implementation can be found in Evaluation/Document_Retrieval.py.
#### Answer Accuracy Evaluation
We utilize GPT-4-based evaluators to score answers on a five-point scale, ensuring semantic accuracy, precision, and relevance, particularly for summary-type questions. The implementation can be found in Evaluation/Answer_Accuracy.py.

## Knowledge Graph
The knowledge graph can serve as a valuable resource for researchers, facilitating knowledge discovery, identifying trends, and exploring relationships between biomedical entities and research methods. The knowledge graph comprises 94,962 nodes and 290,403 relationships. You can download the [knowledge graph](https://drive.google.com/file/d/1x5alzBbdigoBI9j2ZX64cLU_Uad_xqfl/view?usp=sharing).

## License

The repository is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.


