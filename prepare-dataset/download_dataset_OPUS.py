#!/usr/bin python3

from pyprojroot.here import here
import zipfile
import os
import urllib.request
import csv
import random

csv.field_size_limit(100000000)
quoting_style = csv.QUOTE_NONE

def download_raw_dataset(url, dir):
    #extract ?f= element
    if not os.path.exists(here(dir)):
        os.makedirs(here(dir))
    
    folder_name = url.split('?f=')[1].split('/')[0]
    here_folder_name = here(f"{dir}/{folder_name}/")
    file_name = here(f"{dir}/{folder_name}.zip")

    try:
        if os.path.exists(file_name):
            print("downloaded already")
            return
    except:
        pass
        



    urllib.request.urlretrieve(url, file_name)
    
    #unzip in new folder
    with zipfile.ZipFile(file_name, 'r') as zip_ref:
        zip_ref.extractall(here_folder_name)
    #remove zip file
    os.remove(file_name)

def make_pair(url, dir):
    download_raw_dataset(url,dir)
    folder_name = url.split('?f=')[1].split('/')[0]
    en = open(f"{dir}/{folder_name}/{folder_name}.en-id.en", 'r', encoding="utf-8")
    id = open(f"{dir}/{folder_name}/{folder_name}.en-id.id", 'r', encoding="utf-8")
    
    # en_id as csv  
    data = []

    if not os.path.exists(here(f"{dir}/parallel_sentences")):
        os.makedirs(here(f"{dir}/parallel_sentences"))

    en_id = open(f"{dir}/parallel_sentences/{folder_name}.csv", 'w', encoding="utf-8")

    for line_en, line_id in zip(en, id):
        if line_en.strip() == "" or line_id.strip() == "":
            continue

        data.append([line_en.strip(), line_id.strip()])

    csv_en_id = csv.writer(en_id,delimiter='\t',quoting=quoting_style,quotechar='"',escapechar="\\")
    csv_en_id = csv_en_id.writerows(data)
    en.close()
    id.close()
    en_id.close()

def argparse():
    import argparse
    parser = argparse.ArgumentParser(description='Download parallel_sentence dataset')
    #url 
    parser.add_argument('--url', type=str, default='https://opus.nlpl.eu/download.php?f=TED2020/v1/moses/en-id.txt.zip',
                        help='url of disk/raw_dataset')
    #folder name
    parser.add_argument('--dir', type=str, default='disk/raw_data')
    args = parser.parse_args()
    return args


if __name__ == '__main__':

    argparse = argparse()
    url = "https://opus.nlpl.eu/download.php?f=NeuLab-TedTalks/v1/moses/en-id.txt.zip"
    make_pair(url, argparse.dir)

