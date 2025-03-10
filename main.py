import os
import github_scripts
import ai_reviewer
import re
import json

github_repo = os.getenv('GITHUB_REPO', 'default-repo-name')
github_pr_number = int(os.getenv('GITHUB_PR_NUMBER', '0'))
github_token = os.getenv('GITHUB_TOKEN', 'no-token')



def remove_deleted_line_diff(diff_str):
    pattern = r"^\-.*\n?"  # Matches the whole line including newline if it starts with "prefix_"
    # Use re.sub to replace all occurrences of the pattern with an empty string
    cleaned_diff = re.sub(pattern, "", diff_str, flags=re.MULTILINE)
    return cleaned_diff

def mark_changed_line(diff_str):
    pattern = r"^\+"  
    cleaned_diff = re.sub(pattern, "<CHANGED_LINE>", diff_str, flags=re.MULTILINE)
    return cleaned_diff

def create_ai_review_payload(diff_block):
    diff = diff_block["diff"]
    diff = remove_deleted_line_diff(diff)
    diff = mark_changed_line(diff)
    diff = diff.strip()
    return {
        "starting_line": diff_block["new_start_line"],
        "file": diff_block["filename"],
        "code": diff
    }
        


pr_file_diffs = github_scripts.fetch_pr_diff(github_token,github_repo,github_pr_number)

for file_diff in pr_file_diffs:
    diff_blocks = github_scripts.extract_pr_diff_blocks(file_diff)
    for diff_block in diff_blocks:
        ai_review_payload = create_ai_review_payload(diff_block)
        with open('input.json', 'w') as f:
            json.dump(ai_review_payload, f, indent=2)
        result = ai_reviewer.review_code()
        reviews = result["reviews"]
        if reviews == None:
            continue
        for review in reviews:
            github_scripts.review_comments(github_token,github_repo,github_pr_number,review["file_name"],review["line"],review["description"])

        

    
