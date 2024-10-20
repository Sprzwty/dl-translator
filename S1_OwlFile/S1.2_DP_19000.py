# import random
# import pandas as pd
# from deeponto.onto import Ontology
#
# # 定义输入和输出文件路径
# input_csv_path = "/Users/Sprzwty/Developer/Can_LLMs_speak_DL/S2_database/19.csv"
# output_csv_path = "/Users/Sprzwty/Developer/Can_LLMs_speak_DL/S2_database/19000.csv"
# owl_file_path = "/Users/Sprzwty/Developer/Can_LLMs_speak_DL/S1_OwlFile/SnomedCT.owx"
#
# # 加载SnomedCT OWL文件
# ontology = Ontology(owl_path=owl_file_path)
#
# # 读取父类的结果
# df = pd.read_csv(input_csv_path)
#
# # 创建一个空的DataFrame来存储结果
# df_list = []
#
# for index, row in df.iterrows():
#     parent_class_iri = row['IRI']
#     parent_class_label = row['rdfs:label']
#
#     # 获取父类实体
#     parent_class = ontology.get_owl_object(parent_class_iri)
#
#     # 获取所有 subclassOf 是这个父类的类
#     subclasses = ontology.get_asserted_children(parent_class, named_only=True)
#
#     # 随机抽取1000个子类
#     sampled_subclasses = random.sample(list(subclasses), min(1000, len(subclasses)))
#
#     for subclass in sampled_subclasses:
#         label = ontology.get_annotations(subclass, annotation_property_iri="http://www.w3.org/2000/01/rdf-schema#label")
#         iri = ontology.get_iri(subclass)
#         df_list.append({"parent class": parent_class_label, "rdfs:label": next(iter(label), ""), "IRI": iri})
#
# # 将所有数据组合成一个DataFrame
# result_df = pd.DataFrame(df_list)
#
# # 将结果保存到CSV文件
# result_df.to_csv(output_csv_path, index=False)
import random
import pandas as pd
from deeponto.onto import Ontology

# 定义输入和输出文件路径
input_csv_path = "/S2_database/19.csv"
output_csv_path = "/S2_database/19000.csv"
owl_file_path = "/S1_OwlFile/SnomedCT.owx"

# 加载SnomedCT OWL文件
ontology = Ontology(owl_path=owl_file_path)

# 读取父类的结果
df = pd.read_csv(input_csv_path)

# 创建一个空的DataFrame来存储结果
df_list = []


def get_all_subclasses(entity, limit=1000):
    """递归获取所有子类直到达到数量限制"""
    subclasses = ontology.get_asserted_children(entity, named_only=True)
    all_subclasses = list(subclasses)

    # 如果子类不足且限制数量大于现有数量，继续获取子类的子类
    while len(all_subclasses) < limit:
        additional_subclasses = []
        for subclass in subclasses:
            additional_subclasses.extend(ontology.get_asserted_children(subclass, named_only=True))

        # 如果没有更多的子类可获取，则跳出循环
        if not additional_subclasses:
            break

        all_subclasses.extend(additional_subclasses)
        subclasses = additional_subclasses  # 更新subclasses以继续获取子类的子类

    return all_subclasses


for index, row in df.iterrows():
    parent_class_iri = row['IRI']
    parent_class_label = row['rdfs:label']

    # 获取父类实体
    parent_class = ontology.get_owl_object(parent_class_iri)

    # 获取所有 subclassOf 是这个父类的类，并确保至少有1000个
    subclasses = get_all_subclasses(parent_class, limit=1000)

    # 随机抽取1000个子类
    sampled_subclasses = random.sample(list(subclasses), min(1000, len(subclasses)))

    for subclass in sampled_subclasses:
        label = ontology.get_annotations(subclass, annotation_property_iri="http://www.w3.org/2000/01/rdf-schema#label")
        iri = ontology.get_iri(subclass)
        df_list.append({"parent class": parent_class_label, "rdfs:label": next(iter(label), ""), "IRI": iri})

# 将所有数据组合成一个DataFrame
result_df = pd.DataFrame(df_list)

# 将结果保存到CSV文件
result_df.to_csv(output_csv_path, index=False)
