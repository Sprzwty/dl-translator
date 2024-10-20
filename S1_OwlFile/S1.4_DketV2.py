import pandas as pd
import re


# Redesigned code to improve clarity and functionality

# Function to reconstruct the natural language sentence by removing POS tags
def reconstruct_sentence(pos_tagged_sentence):
    # Remove all POS tags (i.e., anything after '/') and remove <EOS>
    sentence = ' '.join([word.split('/')[0] for word in pos_tagged_sentence.split() if word.split('/')[0] != '<EOS>'])
    sentence = re.sub(r'\s+', ' ', sentence).strip()  # Remove extra spaces
    # Remove extra space before the final dot if it exists
    sentence = re.sub(r'\s+\.$', '.', sentence)
    return sentence


# Function to convert custom logical syntax to Manchester Syntax
def convert_to_manchester_syntax(expression):
    # Remove unwanted symbols and extra content
    expression = re.sub(r'<EOS>', '', expression)  # Remove <EOS>
    expression = re.sub(r'\.\s*\(\s*T\s*\)', '', expression)  # Remove '. ( T )'

    # Convert logical expression to Manchester syntax
    expression = expression.replace(':=', ' EquivalentTo ')  # Replace := with ' EquivalentTo '
    expression = expression.replace('^', ' and ')  # Replace ^ with ' and '
    expression = re.sub(r'\bA\b', ' some ', expression)  # Replace A with ' some '
    expression = re.sub(r'\bE\b', ' some ', expression)  # Replace E with ' some '
    expression = re.sub(r'\bU\b', ' or ', expression)  # Replace U with ' or '
    expression = re.sub(r'(?<=\w)\.(?=\s|\w)', ' has_value ', expression)  # Replace '.' with ' has_value '

    # Remove unnecessary parentheses and other unwanted characters
    expression = expression.replace('(', '').replace(')', '')
    expression = re.sub(r'[^a-zA-Z0-9\s]', '', expression)  # Remove non-alphanumeric characters
    expression = re.sub(r'\s+', ' ', expression).strip()  # Remove extra spaces

    return expression


# File paths
input_file_path = "/Users/Sprzwty/Developer/Can_LLMs_speak_DL/S1_OwlFile/reference_set.train.tsv"
output_file_path = "/Users/Sprzwty/Developer/Can_LLMs_speak_DL/S2_database/dketv2.csv"

# Read the input TSV file
df = pd.read_csv(input_file_path, sep='\t', header=None, names=['POS_tagged_sentence', 'Logical_expression'])

# Generate the natural language expression directly from the first column by removing POS tags
df['Natural_sentence'] = df['POS_tagged_sentence'].apply(reconstruct_sentence)

# Convert logical expressions to Manchester syntax
df['Manchester_syntax'] = df['Logical_expression'].apply(convert_to_manchester_syntax)

# Reorder the columns for better readability
df_processed = df[['POS_tagged_sentence', 'Logical_expression', 'Natural_sentence', 'Manchester_syntax']]

# Save the processed data into a CSV file
df_processed.to_csv(output_file_path, index=False)

print(f"Processed data has been saved to: {output_file_path}")
