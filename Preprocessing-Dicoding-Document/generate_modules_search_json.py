from pyprojroot.here import here
import os
import json
import re
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM
import torch

model_name = 'doc2query/msmarco-indonesian-mt5-base-v1'
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForSeq2SeqLM.from_pretrained(model_name)

def create_queries(para):
    input_ids = tokenizer.encode(para, return_tensors='pt')
    with torch.no_grad():
        # Here we use top_k / top_k random sampling. It generates more diverse queries, but of lower quality

        # Here we use Beam-search. It generates better quality queries, but with less diversity
        beam_outputs = model.generate(
            input_ids=input_ids, 
            max_length=64, 
            num_beams=5, 
            no_repeat_ngram_size=2, 
            num_return_sequences=5, 
            early_stopping=True
        )

    beam_list = []
    for i in range(len(beam_outputs)):
        query = tokenizer.decode(beam_outputs[i], skip_special_tokens=True)
        beam_list.append(query)
    
    print(beam_list)

    return beam_list 


def extract_code_blocks(markdown):
    """
    Removes all code blocks from a markdown string.
    markdown: a string of markdown
    """
    pattern = re.compile(r"(```[a-z]*\n[\s\S]*?\n```)|(`[^`\n]+`)")
    return pattern.findall(markdown)

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

def generate_modules_partition_json():
    file_updated_json = here("data/modules_updated.json")
    list_to_create_json = []
    list_to_create_translateable_json = []
    code_blocks_list = []

     
    with open(file_updated_json, "r", encoding="utf-8") as f:
        data = json.load(f)

        for i, each_module in enumerate(data):
            # partition the content into split by \n

            code_blocks = extract_code_blocks(each_module["content_md"])
            for n, code_block in enumerate(code_blocks):
                code_blocks_list.append({
                    "code": code_block[0],
                    "type": "code_in_modules",
                    "in_document": str(i),
                    "code_id": str(n),
                    "title": each_module["title"],
                    "content_display": each_module["content_md"]
                })

                
            text_list = each_module["content_only_text"].split("\n")
            for j,text in enumerate(text_list):

                if len(text.split()) >25:
                
                    query = create_queries(text)
                    query = [each + "." for each in query]
                    for query_text in query:
                        list_to_create_translateable_json.append({
                            "text_id": each_module["title"]+". " + query_text,
                        })
                    
                else:
                    query= [""]
                    print(f"text too short {j}")


    



                list_to_create_json.append({
                    "type": "modules",
                    "document_id": str(i),
                    "sub_id": str(j),
                    "title": each_module["title"],
                    "content_only_text": text,
                    "content_only_text_searchable": each_module["title"]+". " + " ".join(query)+ "."+ text,
                    "content_display": each_module["content_md"]
                }),

                
    
                list_to_create_translateable_json.append({
                    "text_id": each_module["title"]+". " + text,
                })
                
    with open(here("data/modules_discussion_search.json"), "w", encoding="utf-8") as f:
        json.dump(list_to_create_json, f, indent=4, ensure_ascii=False)

    with open(here("data/modules_partition_translateable.json"), "w", encoding="utf-8") as f:
        json.dump(list_to_create_translateable_json, f, indent=4, ensure_ascii=False)
    
    with open(here("data/code_search.json"), "w", encoding="utf-8") as f:
        json.dump(code_blocks_list, f, indent=4, ensure_ascii=False)


    

if __name__ == "__main__":
    generate_modules_partition_json()
