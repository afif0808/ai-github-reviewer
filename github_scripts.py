import os
import re
from github import Github
import json

def fetch_pr_diff(token: str, github_repo: str, github_pr_num: int):
    # Authenticate using GitHub token
    g = Github(token)

    # Access the repository and the pull request
    repo = g.get_repo(f"{github_repo}")
    pr = repo.get_pull(github_pr_num)

    # Get the diff of the pull request
    files = pr.get_files()

    # Iterate through the files and print their diffs
    # Create array to store file diffs
    file_diffs = []
    
    for file in files:
        file_diff = {
            "filename": file.filename,
            "patch": file.patch
        }
        file_diffs.append(file_diff)
    
    return file_diffs


def extract_pr_diff_blocks(file_diff):
    pattern = r"^@@\s-(\d+),(\d+)\s[-+]?(\d+),(\d+)\s@@.*"
    regex = re.compile(pattern, re.MULTILINE)
    patch = file_diff["patch"]
    matches = regex.findall(patch)
    blocks = []
    for i in range(len(matches)):
        match = matches[i]
        prev_start_line = int(match[0])
        prev_num_lines = int(match[1])
        
        # match_str = "@@ -" + str(prev_start_line) + ", " + str(prev_num_lines) + " +" + str(prev_start_line) + ", " + str(prev_num_lines) + " @@"
        # patch.replace(match_str, "<BLOCK_DIFF>")
        
        new_start_line = int(match[2])
        new_num_lines = int(match[3])
        blocks.append({
            'filename' : file_diff["filename"],
            'prev_start_line': prev_start_line,
            'prev_num_lines': prev_num_lines,
            'new_start_line': new_start_line,
            'new_num_lines': new_num_lines,
        })
    
    

    pattern = r"^@@\s-\d+,\d+\s[-+]?\d+,\d+\s@@.*"
    regex = re.compile(pattern, re.MULTILINE)
    patch = regex.sub("<BLOCK_DIFF>", patch)
    # print(patch)
    diffs = patch.split("<BLOCK_DIFF>")
    diffs.pop(0)
    print(file_diff["filename"])
    print(diffs)
    print(len(diffs))
    print(len(blocks))
    
    # print(len(blocks),len(diffs))
    for i in range(len(blocks)):
        blocks[i]['diff'] = diffs[i]
        
    return blocks


def review_comments(token: str, github_repo: str, github_pr_num: int, filename: str, line_number: int, comment_body: str):
    """
    Add a review comment to a specific line in a pull request file
    
    Args:
        token (str): GitHub authentication token
        github_repo (str): Repository name in format 'owner/repo'
        github_pr_num (int): Pull request number
        filename (str): Path to the file to comment on
        line_number (int): Line number to attach the comment to
        comment_body (str): Content of the comment
    """
    # Initialize GitHub client
    g = Github(token)
    
    # Get repository and pull request
    repo = g.get_repo(github_repo)
    pr = repo.get_pull(github_pr_num)
    
    print(line_number)
    print(pr.get_commits()[0])
    
    # Create a review comment
    commit = pr.get_commits()[0]  # Get latest commit
    pr.create_review_comment(
        body=comment_body,
        commit=commit,
        path=filename,
        line=line_number
    )
