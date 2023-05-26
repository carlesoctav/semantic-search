from pyprojroot.here import here
import os
import json
import re
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM
import torch
from markdownify import markdownify as md
import difflib
from transformers import pipeline
from unidecode import unidecode
model = "mrm8488/codebert-base-finetuned-stackoverflow-ner"
tokenizer = "mrm8488/codebert-base-finetuned-stackoverflow-ner"
tagger = pipeline("ner",model = model, tokenizer = tokenizer,aggregation_strategy="first")

model_name = 'doc2query/msmarco-indonesian-mt5-base-v1'
tokenizer_name = AutoTokenizer.from_pretrained(model_name)
model_name = AutoModelForSeq2SeqLM.from_pretrained(model_name)

def create_queries(para):
    input_ids = tokenizer_name.encode(para, return_tensors='pt')
    with torch.no_grad():
        # Here we use top_k / top_k random sampling. It generates more diverse queries, but of lower quality

        # Here we use Beam-search. It generates better quality queries, but with less diversity
        beam_outputs = model_name.generate(
            input_ids=input_ids, 
            max_length=64, 
            num_beams=5, 
            no_repeat_ngram_size=2, 
            num_return_sequences=5, 
            early_stopping=True
        )

    beam_list = []
    for i in range(len(beam_outputs)):
        query = tokenizer_name.decode(beam_outputs[i], skip_special_tokens=True)
        beam_list.append(query)
    
    print(beam_list)

    return beam_list 




def make_code_block(text, language="javascript"):
    """
    converts a string to a code block
    text: a string
    """
    tagg = tagger(text)
    counter = 0 
    reconsturcted_text = "```javascript\n"


    for entity in tagg:
        if entity["entity_group"] == "Code_Block":
            reconsturcted_text += entity["word"]
            counter += 1
    
    if counter == 0:
        return ("", text)
    else:
        reconsturcted_text += "\n```"
    



    diff = difflib.ndiff(text.splitlines(keepends=True), reconsturcted_text.splitlines(keepends=True))
    # return only missing lines 
    text_only = ''.join(x[2:] for x in diff if x.startswith('- '))


    return (reconsturcted_text, text_only)

    


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

def remove_non_standard_whitespace(markdown):
    """
    remove non breaking space
    "^[\u25A0\u00A0\s]+"
    """
    return unidecode(markdown)


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

def generate_discussion_partition_json():
    counter = 0
    code_discussion_search = []
    discussion_search = []

    discussion_data_file = open(here("data/discussions.json"), "r")
    discussion_data = json.load(discussion_data_file, encoding="utf-8")
    translateable_data_file = open(here("data/translateable.json"), "r")
    translateable_data = json.load(translateable_data_file, encoding="utf-8")

    for i,each_discussion in enumerate(discussion_data):
        content_display= md(each_discussion["question"], heading_style="ATX",code_language = "javascript",)
        content_display = remove_non_standard_whitespace(content_display)
        code_blocks = extract_code_blocks(content_display)
        
        if code_blocks !=[]:
            content_display = remove_whitespace(content_display)
            markdown = remove_code_blocks(content_display)
            markdown = remove_images_and_links(markdown)
            markdown = remove_tables(markdown)
            markdown = remove_hashes_and_pipe(markdown)
            markdown = remove_blockquotes(markdown)
            markdown = remove_whitespace(markdown)
            content_only_text = markdown.strip()

            if len(content_only_text.split()) > 20:

                query = create_queries(content_only_text)
                query = [each + "." for each in query]
                for query_text in query:
                    translateable_data.append({
                        "text_id": each_discussion["discussion_title"] + ". " + query_text,
                    })


            
            
            title = each_discussion ["discussion_title"]
            discussion_search.append({
                "type": "discussion",
                "document_id": str(i),
                "sub_id": "0",
                "title": each_discussion["discussion_title"],
                "content_only_text": content_only_text,
                "content_only_text_searchable": title + ". " + " ".join(query)+ content_only_text,
                "content_display": content_display,
            })

            translateable_data.append({
                "text_id": title+ ". " + content_only_text,
            })
        
            code_discussion_search.append({
                "code": code_blocks[0][0],
                "type": " code_in_discussion",
                "in_document": str(i),
                "title": each_discussion["discussion_title"],
                "content_display": content_display,
            })
            
            print(counter)
            counter += 1

        else:
            content_display = remove_whitespace(content_display)
            code_block, content_only_text = make_code_block(content_display)
            markdown = remove_images_and_links(content_only_text)
            markdown = remove_tables(markdown)
            markdown = remove_hashes_and_pipe(markdown)
            markdown = remove_blockquotes(markdown)
            markdown = remove_whitespace(markdown)
            content_only_text = markdown.strip()
            title = each_discussion ["discussion_title"]

            if len(content_only_text.split()) >20:

                query = create_queries(content_only_text)
                query = [each + "." for each in query]
                for query_text in query:
                    translateable_data.append({
                        "text_id": each_discussion["discussion_title"] + ". " + query_text,
                    })


            code_discussion_search.append({
                "code": code_block,
                "type": " code_in_discussion",
                "in_document": str(i),
                "title": each_discussion["discussion_title"],
                "content_display": content_display,
            })

            discussion_search.append({
                "type": "discussion",
                "document_id": str(i),
                "title": each_discussion["discussion_title"],
                "content_only_text": content_only_text,
                "content_only_text_searchable": title + ". " + " ".join(query)+ content_only_text,
                "content_display": content_display,
            })

            translateable_data.append({
                "text_id": title+ ". " + content_only_text,
            })

            print(counter)
            counter+=1
        
            
    with open(here("data/discussion_search.json"), "w", encoding="utf-8") as f:
        json.dump(discussion_search, f, indent=4, ensure_ascii=True)
    
    with open(here("data/code_discussion_search.json"), "w", encoding="utf-8") as f:
        json.dump(code_discussion_search, f, indent=4, ensure_ascii=True)

    with open(here("data/translateable.json"), "w", encoding="utf-8") as f:
        json.dump(translateable_data, f, indent=4, ensure_ascii=True)
        
        



                



    

if __name__ == "__main__":
    generate_discussion_partition_json()
