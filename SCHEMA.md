# Schema for the BioStrataKG Knowledge Graph

This document details the schema for the Biomedical Stratified Knowledge Graph (BioStrataKG), a graph constructed from biomedical literature as described in our paper. The graph is composed of two main layers: an entity-level graph and a document-level graph.

The official namespace for the schema is `https://github.com/yichun10/BioCDQA/schema#`.

## Node Labels

BioStrataKG contains the following types of nodes, representing both biomedical entities and document-level concepts.

* `Paper`: Represents a single biomedical research article, identified by its PMID or an internal ID.
* `Gene`: Represents a specific gene. Normalization is based on the UniProt database.
* `Protein`: Represents a specific protein. Normalization is based on the UniProt database.
* `Disease`: Represents a specific disease or condition. Normalization is based on the MeSH database.
* `Drug`: Represents a specific drug or chemical compound. Normalization is based on the MeSH database.
* `Method`: Represents a research methodology or technique described in a paper.
* `Dataset`: Represents a dataset used or referenced in a research paper.
* `Research Domain`: Represents a field of study or research area.

## Relationship Types

The nodes in BioStrataKG are connected by the following relationship types.

### Document-Level Relationships

* **`CITES`**: Indicates that one paper cites another paper.
    * Example: `(:Paper)-[:CITES]->(:Paper)`
* **`HAS_METHOD`**: Connects a paper to a research method used within it.
    * Example: `(:Paper)-[:HAS_METHOD]->(:Method)`
* **`USES_DATASET`**: Connects a paper to a dataset it utilizes.
    * Example: `(:Paper)-[:USES_DATASET]->(:Dataset)`
* **`BELONGS_TO_DOMAIN`**: Connects a paper to its corresponding research domain.
    * Example: `(:Paper)-[:BELONGS_TO_DOMAIN]->(:Research Domain)`

### Entity-Level Relationships

* **`TREATS`**: Indicates that a drug is used for the treatment of a disease.
    * Example: `(:Drug)-[:TREATS]->(:Disease)`
* **`ASSOCIATED_WITH`**: A general relationship indicating an association between two entities, most commonly a gene and a disease.
    * Example: `(:Gene)-[:ASSOCIATED_WITH]->(:Disease)`
* **`INTERACTS_WITH`**: Represents an interaction between two entities, such as a drug-drug interaction or a protein-protein interaction.
    * Example: `(:Drug)-[:INTERACTS_WITH]->(:Drug)` or `(:Protein)-[:INTERACTS_WITH]->(:Protein)`
* **`INHIBITS_PROTEIN_ACTIVITY`**: A specific relationship where a drug or compound inhibits the activity of a protein.
    * Example: `(:Drug)-[:INHIBITS_PROTEIN_ACTIVITY]->(:Protein)`
* **`ACTIVATES_PROTEIN_ACTIVITY`**: A specific relationship where a drug or compound activates the activity of a protein.
    * Example: `(:Drug)-[:ACTIVATES_PROTEIN_ACTIVITY]->(:Protein)`
* **`CODES_FOR`**: Indicates that a gene codes for a specific protein.
    * Example: `(:Gene)-[:CODES_FOR]->(:Protein)`
* **`PRODUCES`**: A relationship indicating that a gene produces a protein (often used interchangeably with `CODES_FOR`).
    * Example: `(:Gene)-[:PRODUCES]->(:Protein)`



---

## Node and Relationship Properties

In addition to labels and types, nodes and relationships in BioStrataKG store key-value attributes (properties) that provide detailed, specific information.

### Node Properties

The properties stored depend on the node's label.

* **For `Paper` nodes:**
    * `pmid` (string): The unique PubMed ID of the article.
    * `title` (string): The official title of the article.
    * `abstract` (string): The abstract text of the paper.
    * `year` (integer): The year of publication.
    * `cited_by_count` (integer): The number of times the paper has been cited.

* **For entity nodes (`Gene`, `Protein`, `Disease`, `Drug`):**
    * `id` (string): The canonical identifier from the respective normalization database.
    * `name` (string): The standardized name or term for the entity.

* **For conceptual nodes (`Method`, `Dataset`, `Research Domain`):**
    * `name` (string): The normalized name of the concept.

### Relationship Properties

To ensure traceability, every relationship extracted from a document contains a reference back to its source.

* **For all relationship types:**
    * `EvidenceSource` (string): The ID (e.g., PMID) of the source `Paper` node from which the relationship was extracted. This makes every assertion in the knowledge graph traceable to its origin in the literature.
