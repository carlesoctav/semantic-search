# i will generate json based on planning.md scheme

from pyprojroot.here import here
import os
import json
import re


def generate_modules_json():
    # copy data/moudules.json to data/modules_updated.json
    file_updated_json = here("data/modules.json")
    folder_content = here("content_modules/content")
    folder_content_file = os.listdir(folder_content)
    folder_content_only_text = here("content_modules/content_only_text")
    folder_content_only_text_file = os.listdir(folder_content_only_text)
    print(folder_content)
    with open(file_updated_json, "r", encoding="utf-8") as f:
        data = json.load(f)

        for i, each_module in enumerate(data):
            each_module["modules_id"] = str(i) 
            each_module["id"] = str(each_module["id"])
            module_file_md = ""
            with open(os.path.join(folder_content, folder_content_file[i]), "r", encoding="utf-8") as f:
                module_file_md = f.read()

            with open(os.path.join(folder_content_only_text, folder_content_only_text_file[i]), "r", encoding="utf-8") as f:
                module_file_only_text = f.read()

            each_module["content_md"] = module_file_md
            each_module["content_only_text"] = module_file_only_text
            

            #check if there's an iframe, if there is, extract the video link with youtube.com/embed/...
            if re.search(r"<iframe.*?src=\"https:\/\/www.youtube.com\/embed\/(.*?)\".*?>", each_module["content"]):
                 #extract the video link with workable link
                video_link = re.search(r"<iframe.*?src=\"https:\/\/www.youtube.com\/embed\/(.*?)\".*?>", each_module["content"]).group(1)
                video_link = video_link.split("?")[0]
                each_module["video_link"] = "https://www.youtube.com/watch?v=" + video_link
                each_module["video_id"] = video_link
            else:
                each_module["video_link"] = "None"
                each_module["video_id"] = "None"

        
    with open(here("data/modules_updated.json"), "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)
        





        


if __name__ == "__main__":
    generate_modules_json()
