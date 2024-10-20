import pandas as pd
from tqdm import tqdm
from deeponto.onto import Ontology, OntologyReasoner
from concurrent.futures import ThreadPoolExecutor, as_completed

# Define file paths
owl_file_path = "/S1_OwlFile/SnomedCT.owx"
input_csv_path = "/S2_database/19.csv"
output_csv_path = "/S2_database/19000_extended.csv"

# Load the SnomedCT OWL file
ontology = Ontology(owl_path=owl_file_path)
reasoner = OntologyReasoner(ontology, reasoner_type="elk")

# Function to process each entity and retrieve required information
def process_entity(row):
    iri = row['IRI']
    owl_object = ontology.get_owl_object(iri)

    # Retrieve IRI and Concept Name
    concept_iri = ontology.get_iri(owl_object)
    concept_name = next(iter(ontology.get_annotations(owl_object, annotation_property_iri="http://www.w3.org/2000/01/rdf-schema#label")), "N/A")

    # Retrieve additional annotations
    class_rdfs_label = next(iter(ontology.get_annotations(owl_object, annotation_property_iri="http://www.w3.org/2000/01/rdf-schema#label")), "N/A")
    class_skos_prefLabel = next(iter(ontology.get_annotations(owl_object, annotation_property_iri="http://www.w3.org/2004/02/skos/core#prefLabel")), "N/A")
    class_skos_definition = next(iter(ontology.get_annotations(owl_object, annotation_property_iri="http://www.w3.org/2004/02/skos/core#definition")), "N/A")
    class_skos_altLabel = next(iter(ontology.get_annotations(owl_object, annotation_property_iri="http://www.w3.org/2004/02/skos/core#altLabel")), "N/A")

    # Retrieve SubClassOf relationships (direct and anonymous ancestor)
    subclass_of_iris = reasoner.get_inferred_super_entities(owl_object, direct=True)
    subclass_of_anon_iris = reasoner.get_inferred_super_entities(owl_object, direct=False)

    # Retrieve EquivalentTo relations
    equivalence_axioms = ontology.get_equivalence_axioms(entity_type='Classes')
    equivalent_to_iris = [ontology.get_iri(eq_class) for axiom in equivalence_axioms for eq_class in axiom.getSignature() if owl_object in axiom.getSignature() and eq_class != owl_object]

    return {
        "IRI": concept_iri,
        "concept name": concept_name,
        "Class_rdfs:label": class_rdfs_label,
        "Class_skos:prefLabel": class_skos_prefLabel,
        "Class_skos:definition": class_skos_definition,
        "Class_skos:altLabel": class_skos_altLabel,
        "SubClassOf": "|".join(subclass_of_iris),
        "SubClass Of (Anonymous Ancestor)": "|".join(subclass_of_anon_iris),
        "EquivalentTo": "|".join(equivalent_to_iris)
    }

# Read the input CSV file
df = pd.read_csv(input_csv_path)

# Initialize the list to store results
extended_info_list = []

# Use ThreadPoolExecutor for parallel processing
with ThreadPoolExecutor(max_workers=4) as executor:  # Adjust max_workers as needed
    # Submit tasks to the executor
    futures = {executor.submit(process_entity, row): row for _, row in df.iterrows()}

    # Use tqdm for progress bar display
    for future in tqdm(as_completed(futures), total=len(futures), desc="Processing entities"):
        # Append the processed result to the extended_info_list
        extended_info_list.append(future.result())

# Convert the list of dictionaries to a DataFrame
extended_df = pd.DataFrame(extended_info_list)

# Save the results to a new CSV file
extended_df.to_csv(output_csv_path, index=False)

print(f"Extended information saved to {output_csv_path}")