from langchain_ollama import ChatOllama
from langchain_core.prompts import PromptTemplate
import os
import json

# Membaca aturan dari file
with open('code_rules.txt', 'r') as file:
    code_rules = file.read().strip()

with open('input.json') as json_file:
    data_json = json.load(json_file)

# Ambil informasi dari JSON
file_name = data_json["file"]
start_line = data_json["starting_line"]
code_snippet = data_json["code"]

# Pisahkan baris kode
code_lines = code_snippet.split("\n")

# Hitung line_number berdasarkan tag <CHANGED_LINE>
changed_lines = []
current_line = start_line  # Inisialisasi line pertama

for line in code_lines:
    if "<CHANGED_LINE>" in line:
        # Bersihkan tag <CHANGED_LINE>
        clean_line = line.replace("<CHANGED_LINE>", "").strip()
        changed_lines.append(f"{current_line}: {clean_line}")
    current_line += 1  # Selalu naik meskipun baris tidak berubah

# Gabungkan kembali hanya baris yang berubah
changed_code = "\n".join(changed_lines)

# Template Prompt
prompt_template = PromptTemplate.from_template(
    """
    You are an AI assistant specialized in code review.  
    Your task is to review the provided Golang code snippet **primarily based on the given rules**,  
    but you may use general best practices to enhance the review when necessary.  

    🚨 **Do not introduce arbitrary or unnecessary rules.** 🚨  

    ## **Rules for Code Review**  
    {code_rules}

    1️⃣ **Only review the lines marked with `<CHANGED_LINE>`**.  
       - Ignore all other lines.  
       - The first line of the provided code starts at **line {start_line}** in `{file_name}`.  
       - Each `<CHANGED_LINE>` corresponds to its actual line number in the file.  
       - If no meaningful issues are found, provide a brief confirmation that the changes align with best practices.  

    2️⃣ Identify and report the following issues **(if applicable)**:  
        - Code redundancy  
        - Inefficient logic  
        - Security vulnerabilities  
        - Bad coding practices  
        - High complexity that reduces maintainability  
        - Unnecessary dependencies  

    3️⃣ You **may** provide suggestions beyond these categories if they improve readability, maintainability, or performance,  
        but avoid nitpicking minor style issues unless they significantly impact code quality.  

    4️⃣ Your review **must** follow this JSON format:  
    ```json
    {{
        "review": [
            {{
                "file_name": "{file_name}",
                "line": <line_number>,
                "point": "<issue_category>",
                "description": "<brief_explanation>",
                "suggested_fix": "<how_to_fix>",
                "code_change": "<modified_code_if_needed>"
            }}
        ]
    }}
    ```

    - **If no issues are found**, return:  
      ```json
      {{
          "review": []
      }}
      ```  
    - **If a code modification is required**, provide the updated code snippet inside `"code_change"`.  

    Now, review the following changed lines from `{file_name}` (starting at line {start_line}):  

    ```golang
    {changed_code}
    ```

    **Your output must be valid JSON following the specified format.**
    """
)

# Format prompt dengan data
prompt_input = prompt_template.format(
    code_rules=code_rules,
    file_name=file_name,
    start_line=start_line,
    changed_code=changed_code,
)

# Inisialisasi LLM
llm = ChatOllama(model="qwen2.5-coder", temperature=0.1)
llm_resp = llm.invoke(prompt_input)

# Output hasil review
print(llm_resp.content)