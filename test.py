import re

text = """prefix_hello world
prefix_goodbye world
no_prefix_here
prefix_python regex
keep_this_line"""

# Pattern to match entire lines starting with "prefix_"
pattern = r"^prefix_.*\n?"  # Matches the whole line including newline if it starts with "prefix_"

result = re.sub(pattern, "", text, flags=re.MULTILINE)

# print(result)
