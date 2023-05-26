import json
import os
from markdownify import markdownify as md
import re
from pyprojroot.here import here
import re

def remove_code_blocks(markdown):
    """
    Removes all code blocks from a markdown string.
    markdown: a string of markdown
    """
    pattern = re.compile(r"(```[a-z]*\n[\s\S]*?\n```)|(`[^`\n]+`)")
    return pattern.sub('', markdown)

def remove_images_and_links(markdown):
    """
    Removes all images from a markdown string.
    markdown: a string of markdown
    """
    pattern = re.compile(r'\!\[.*\]\(.*\)')
    markdown = pattern.sub('', markdown)
    pattern = re.compile(r'\[.*\]\(.*\)')
    return pattern.sub('', markdown)


def remove_tables(markdown):
    """
    Removes all tables from a markdown string.
    markdown: a string of markdown
    """
    pattern = re.compile(r'\|.*\|')
    return pattern.sub('', markdown)

def remove_whitespace(markdown):
    """
    remove trailing \n and whitespace
    if there's a \n*, replace it with \n

    """
    markdown = re.sub(r'\n\s*\n', '\n', markdown)
    return markdown



def remove_hashes_and_pipe(markdown):
    """
    Removes all hashes and pipes from a markdown string.
    markdown: a string of markdown
    """
    markdown = re.sub(r'\|', '', markdown)
    markdown =re.sub(r'#+', '', markdown)
    return markdown

def alpha_numeric_only(text):
    """
    converts a string to alphanumeric only
    text: a string
    """
    return re.sub(r'\W+', '', text)

def remove_blockquotes(markdown):
    """
    extract the text from blockquotes,
    if it's empty, remove it
    """
    pattern = re.compile(r'>\s*(.*)')
    pattern_2 = re.compile(r'>\s')
    markdown = pattern.sub(r'\1', markdown)
    return pattern_2.sub('', markdown)

    





def generate_content_modules(file = "data/discussions.json", text_only = False):
    """
    Generates content modules from a json file (HTML to markdown)
    file: a string of the json file path
    text_only: a boolean indicating whether to remove all non-text elements from the markdown
    """
    # extract last part of file /{file_name}.json
    file_name = str(file).split("/")[-1].split(".")[0]
    print(file_name)
    file = here(file)
    if text_only:
        folder_to_save = here(f"content_{file_name}/content_only_text")
    else:
        folder_to_save = here(f"content_{file_name}/content")

    if not os.path.exists(folder_to_save):
        os.makedirs(folder_to_save)        

    with open(file, encoding="utf-8") as f:
        data = json.load(f)
        for i, module in enumerate(data):
            # get content
            if file_name =="discussions":
                content = module['question']
            if file_name == "":
                content = module['content']
            markdown = md(content, heading_style="ATX", code_language = "javascript",)
        
            if text_only:
                markdown = remove_code_blocks(markdown)
                markdown = remove_images_and_links(markdown)
                markdown = remove_tables(markdown)
                markdown = remove_hashes_and_pipe(markdown)
                markdown = remove_blockquotes(markdown)
                markdown = remove_whitespace(markdown)
                markdown = markdown.strip()
            
            title = alpha_numeric_only(module["discussion_title"])
            with open(os.path.join(folder_to_save, f"{i}".zfill(3) + f"_{title}.md" ), "w", encoding="utf-8") as f:
                f.write(markdown)
    

if __name__ == "__main__":
    generate_content_modules( text_only = False )
 


