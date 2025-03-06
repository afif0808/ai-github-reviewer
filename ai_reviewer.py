from langchain_ollama import ChatOllama
from langchain_core.prompts import PromptTemplate
import re
import os
import json

def read_code_rules():
    """Read code review rules from file"""
    with open('code_rules.txt', 'r') as file:
        return file.read().strip()

def read_input_json():
    """Read and parse input JSON file"""
    with open('input.json') as json_file:
        return json.load(json_file)

def extract_changed_lines(code_snippet, start_line):
    """Extract and format changed lines from code snippet"""
    code_lines = code_snippet.split("\n")
    changed_lines = []
    current_line = start_line

    for line in code_lines:
        if "<CHANGED_LINE>" in line:
            clean_line = line.replace("<CHANGED_LINE>", "").strip()
            changed_lines.append(f"{current_line}: {clean_line}")
        current_line += 1

    return "\n".join(changed_lines)

def get_review_prompt():
    """Return the review prompt template"""
    return PromptTemplate.from_template(
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
        {{
            "reviews": [
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

        - **If no issues are found**, return json:  
          {{
              "reviews": null
          }}
          
        - **If a code modification is required**, provide the updated code snippet inside `"code_change"`.  

        Now, review the following changed lines from `{file_name}` (starting at line {start_line}):  

        ```golang
        {changed_code}
        ```

        **Your output must be valid JSON following the specified format.**
        """
    )

def review_code():
    """Main function to perform code review"""
    # Read necessary files
    code_rules = read_code_rules()
    data_json = read_input_json()

    # Extract information from JSON
    file_name = data_json["file"]
    start_line = data_json["starting_line"]
    code_snippet = data_json["code"]

    # Process code and create prompt
    changed_code = extract_changed_lines(code_snippet, start_line)
    prompt_template = get_review_prompt()
    
    prompt_input = prompt_template.format(
        code_rules=code_rules,
        file_name=file_name,
        start_line=start_line,
        changed_code=changed_code,
    )

    # Initialize LLM and get response
    llm = ChatOllama(model="qwen2.5-coder", temperature=0.1)
    llm_resp = llm.invoke(prompt_input)

    # Parse response content as JSON and return
    result = llm_resp.content
    # print(result)
    pattern = r"(\`\`\`json\n)([\s\S]*\n)(\`\`\`)"
    replacement = r"\2"  # Keep only the middle part
    result = re.sub(pattern, replacement, result)
    return json.loads(result)


