import random
import pandas as pd
from deeponto.onto import Ontology

# 加载SnomedCT OWL文件
owl_file_path = "/S1_OwlFile/SnomedCT.owx"
ontology = Ontology(owl_path=owl_file_path)

# 定义 'SNOMED CT Concept' 的 IRI
snomed_ct_concept_iri = 'http://snomed.info/id/138875005'  # 这是 SNOMED CT Concept 的 IRI

# 获取 SNOMED CT Concept 类
snomed_ct_concept = ontology.get_owl_object(snomed_ct_concept_iri)

# 获取所有 subclassOf 是 SNOMED CT Concept 的类
subclasses = ontology.get_asserted_children(snomed_ct_concept, named_only=True)

# 随机抽取最多19000个实例
sampled_subclasses = random.sample(list(subclasses), min(19000, len(subclasses)))

# 创建一个空的DataFrame来存储结果
df_list = []

for subclass in sampled_subclasses:
    label = ontology.get_annotations(subclass, annotation_property_iri="http://www.w3.org/2000/01/rdf-schema#label")
    iri = ontology.get_iri(subclass)
    df_list.append({"parent class": 'SNOMED CT Concept', "rdfs:label": next(iter(label), ""), "IRI": iri})

# 将所有数据组合成一个DataFrame
df = pd.DataFrame(df_list)

# 将结果保存到CSV文件
df.to_csv("/Users/Sprzwty/Developer/Can_LLMs_speak_DL/S2_database/19.csv", index=False)
