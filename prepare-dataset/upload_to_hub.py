from datasets import load_dataset, DatasetDict
import os 
dataset_folder = "disk/dataset"
token = ""

ds = DatasetDict()

for file in os.listdir(dataset_folder):
    if file.endswith(".json"):
        file_name = file.split(".")[0]  #make it aplhanmueric only
        file_name = "".join([i for i in file_name if i.isalpha() or i.isdigit()])
        #upload to hub carlesoctav/en-id-parallel-sentences, on subset file
        dataset = load_dataset('json', data_files=f"{dataset_folder}/{file}")["train"]
        ds.update({file_name:dataset})
    if file.endswith(".csv"):
        file_name = file.split(".")[0]  #make it aplhanmueric only
        file_name = "".join([i for i in file_name if i.isalpha() or i.isdigit()])
        #upload to hub carlesoctav/en-id-parallel-sentences, on subset file
        dataset = load_dataset('csv', data_files=f"{dataset_folder}/{file}", sep="\t",
                               names=["text_en","text_id"])["train"]
        ds.update({file_name:dataset})


print(ds)
print(ds.push_to_hub("carlesoctav/en-id-parallel-sentences",token =token ))
    
                               