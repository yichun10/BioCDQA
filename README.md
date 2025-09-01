# A Retrieval-Augmented Knowledge Mining Method with Deep Thinking LLMs for Biomedical Research and Clinical Support

## Introduction
Knowledge graphs and large language models (LLMs) serve as key tools for biomedical knowledge integration and reasoning, facilitating the structured organization of literature and the discovery of deep semantic relationships. However, existing methods still face challenges in knowledge mining and cross-document reasoning: knowledge graph construction is constrained by complex terminology, data heterogeneity, and rapid knowledge evolution, while LLMs exhibit limitations in retrieval and reasoning, making it difficult to efficiently uncover deep cross-document associations and reasoning pathways.
To address these issues, we propose a pipeline that first utilizes LLMs to construct a biomedical knowledge graph from large-scale literature and then builds a cross-document question-answering dataset (BioCDQA) based on this graph to evaluate latent knowledge retrieval and multi-hop reasoning capabilities. Subsequently, we introduce Integrated and Progressive Retrieval-Augmented Reasoning (IP-RAR) to further enhance retrieval accuracy and knowledge reasoning.
IP-RAR maximizes information recall via Integrated Reasoning-based Retrieval and refines extracted knowledge through Progressive Reasoning-based Generation, which harnesses self-reflection to achieve deep thinking and enable precise contextual understanding.
Experiments show that IP-RAR improves document retrieval F1 by 20\% and answer generation accuracy by 25\% over existing methods. This framework helps doctors efficiently integrate treatment evidence for personalized medication plans and enables researchers to analyze advancements and research gaps, accelerating scientific discovery and decision-making.

<img width="1123" alt="image" src="https://github.com/user-attachments/assets/3bb6a95b-88ba-491b-9817-7b50835c8f43" />
Fig. 1. Overview of the proposed framework for biomedical knowledge mining. (A) Biomedical knowledge sources, such as research papers and user queries, are processed through (B) 
A knowledge mining pipeline that leverages a LLM alongside the Integrated and Progressive Retrieval-Augmented Reasoning approach, designed to generate knowledge graph and precise answers. (C) The outputs enable diverse applications, including drug synergy/antagonism, drug repurposing, precision medicine, bottleneck analysis, research planning, and knowledge transfer.

## Framework of IP-RAR

<img width="1171" alt="image" src="https://github.com/user-attachments/assets/b4ba9d05-d950-4033-a723-6cc9177ccb3d" />



Fig. 2. Framework of Integrated and Progressive Retrieval-Augmented Reasoning. (A) Integrated Reasoning-based Retrieval: Performs pre-retrieval reasoning, extracting keywords and generating a virtual answer. Then, a multi-level, multi-granularity retrieval strategy is used to retrieve relevant text chunks, which are ranked based on relevance. (B) Progressive Reasoning-based Generation: Filters out irrelevant text chunks through explanations or self-reflection, then leverages DeepSeek-R1 for deep-thinking-based reasoning on the valid text chunks, generating a precise final response.

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

3、You should download the text and convert it into either Markdown or TXT format. We use [Marker](https://github.com/VikParuchuri/marker.git) to convert the text into Markdown format. 

4、Split the text into appropriately sized chunks (e.g., complete sentences with 500–1000 tokens per chunk) and save the chunks as all_text_chunks.tsv.
```
tsv_data['id'].append(idx)
tsv_data['text'].append(item['content'])
tsv_data['title'].append(item['pid'])
```
5、The abstract does not need to be downloaded or split. It can be directly obtained from the metadata in all_document.json and converted into all_abstract_chunks.tsv.

#### Other Dataset
BioASQ: The benchmark dataset for biomedical semantic indexing and question answering at https://participants-area.bioasq.org/datasets/
MASH-QA: A clinical QA dataset with semantic hierarchies at https://github.com/mingzhu0527/MASHQA.git

### Integrated Reasoning-based Retrieval
#### Download Retrieval Model
We use [Contriever-MSMARCO](https://huggingface.co/facebook/contriever-msmarco) as our retrieval component.

#### Pre-Retrieval Reasoning
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

### Code
The code in this repository is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

### Data
The data in this repository is licensed under the Creative Commons Public Domain Dedication (CC0 1.0 Universal). See the [DATA_LICENSE](DATA_LICENSE) file for details.

## Citation
If you use the repository of this project, please cite it.
```
@article{feng2025retrieval,
  title={A Retrieval-Augmented Knowledge Mining Method with Deep Thinking LLMs for Biomedical Research and Clinical Support},
  author={Feng, Yichun and Wang, Jiawei and He, Ruikun and Zhou, Lu and Li, Yixue},
  journal={GigaScience},
  year={2025},
  publisher={Oxford University Press},
  doi={10.1093/gigascience/giaf109}
}

```
