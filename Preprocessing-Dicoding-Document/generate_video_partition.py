from pyprojroot.here import here
import os
import json
import re
import subprocess


def generate_video_partition_json():
    file_to_loop = here("data/modules_updated.json")
    list_to_create_json = []

    with open(file_to_loop, "r", encoding="utf-8") as f:
        data = json.load(f)

        for each_module in data:
            if each_module["video_link"] != "None":
                # call subprocess to generate caption
                print(each_module["video_id"]) 
                subprocess.call(["node", "youtube-cc-scrapper.js", f"{each_module['video_id']}", "id"])
                # read caption
                caption_file = here("captions.json")
                with open(caption_file, "r", encoding="utf-8") as f:
                    caption_data = json.load(f)

                    # combine caption until 100-150 words
                    caption_100_words = ""
                    counter_sub_id = 0
                    for each_caption in caption_data:
                        if caption_100_words == "":
                            time_start = each_caption["start"]

                        caption_100_words += each_caption["text"]+" "

                        if len(caption_100_words.split()) > 100:
                            list_to_create_json.append({
                                "modules_id": each_module["id"],
                                "sub_id": str(counter_sub_id),
                                "caption": caption_100_words,
                                "time_start": time_start,
                                "video_with_time_start": each_module["video_link"]+"&t="+time_start+"s"
                            
                            })

                            counter_sub_id+=1
                            caption_100_words = ""
                    
                    list_to_create_json.append({
                        "id": each_module["id"],
                        "sub_id": counter_sub_id,
                        "caption": caption_100_words,
                        "time_start": time_start,
                        "video_with_time_start": each_module["video_link"]+"&t="+time_start+"s"
                    })

    with open(here("data/video_partition.json"), "w", encoding="utf-8") as f:
        json.dump(list_to_create_json, f, indent=4)

                    





if __name__ == "__main__":
    generate_video_partition_json()