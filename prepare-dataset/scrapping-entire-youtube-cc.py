from youtube_transcript_api import YouTubeTranscriptApi
from pyprojroot.here import here
import os 
from pytube import Playlist
import json

def get_transcript(video_id, dir, playlist_name):

    directory = here(f"{dir}/youtube-tech-transcript/{playlist_name}/sentences")

    #extract id from url ?v=
    video_id = video_id.split("?v=")[1]


    if not os.path.exists(directory):
        os.makedirs(directory)
    

    try:

        transcript_list = YouTubeTranscriptApi.list_transcripts(video_id)
    except:
        print("there's no cc for this video")
        return 

    try:
        transcript  = transcript_list.find_manually_created_transcript(['en'])

    except:
        print("there's no manual created english cc for this video")
        return 

    try:
        transcript_id = transcript.translate('id')


    except:
        print("there's no indonesian cc translation for this video")
        return

    transcript = transcript.fetch()
    transcript_id = transcript_id.fetch()

    #combine transcript and transcript_id, create new dict based on this

    transcript_combined = []
    for en, id in zip(transcript, transcript_id):
        #remove \n escape character
        en["text"] = en["text"].replace("\n", " ")
        id["text"] = id["text"].replace("\n", " ")
        #strip extra spaces
        en["text"] = en["text"].strip()
        id["text"] = id["text"].strip()


        transcript_combined.append({"text_en": en["text"], "text_id": id["text"]})

    
    #convert to csv and save to folder
    
    print("generated transcript for video id", video_id)
    with open(f"{directory}/{video_id}.json", "w", encoding="utf-8") as f:
        json.dump(transcript_combined, f, indent=4, ensure_ascii=True)


def get_playlist_url(playlist_id):

    playlist = Playlist(playlist_id)
    return playlist.video_urls, playlist.title



if __name__ == "__main__":

    playlist_list = ["https://youtube.com/playlist?list=PLyuswlrh3_XgTEeYHHfs11SBk6d8cG0ds",
                     "https://youtube.com/playlist?list=PLWKjhJtqVAblfum5WiQblKPwIbqYXkDoC",
                     "https://youtube.com/playlist?list=PLWKjhJtqVAbleDe3_ZA8h3AO2rXar-q2V",
                     "https://youtube.com/playlist?list=PLWKjhJtqVAbmGQoa3vFjeRbRADAOC9drk",
                     "https://youtube.com/playlist?list=PLWKjhJtqVAblStefaz_YOVpDWqcRScc2s",
                     "https://youtube.com/playlist?list=PLWKjhJtqVAblQe2CCWqV4Zy3LY01Z8aF1",
                     "https://youtube.com/playlist?list=PLWKjhJtqVAbmGw5fN5BQlwuug-8bDmabi",
                     "https://youtube.com/playlist?list=PLWKjhJtqVAbkArDMazoARtNz1aMwNWmvC",
                     "https://youtube.com/playlist?list=PLWKjhJtqVAbnupwRFOq9zGOWjdvPRtCmO",
                     "https://youtube.com/playlist?list=PLWKjhJtqVAbluXJKKbCIb4xd7fcRkpzoz",
                     "https://youtube.com/playlist?list=PLWKjhJtqVAbnRT_hue-3zyiuIYj0OlpyG",
                     "https://youtube.com/playlist?list=PLWKjhJtqVAbnSe1qUNMG7AbPmjIG54u88",
                     ]
    
    playlist_list.append(["https://youtube.com/playlist?list=PLWKjhJtqVAbn5emQ3RRG8gEBqkhf_5vxD",
                     "https://youtube.com/playlist?list=PLWKjhJtqVAbkoMsX4hgwxbJZW4aB0cbaB",
                     "https://youtube.com/playlist?list=PLWKjhJtqVAbkXQS12WiLsH1oaNZBSoWuV",
                     "https://youtube.com/playlist?list=PLWKjhJtqVAbkzvvpY12KkfiIGso9A_Ixs",
                     "https://youtube.com/playlist?list=PLWKjhJtqVAbl5SlE6aBHzUVZ1e6q1Wz0v"
    ])

    
    for playlist in playlist_list:
        video_ids, playlist_title = get_playlist_url(playlist)
        print(video_ids, playlist_title)

        for video_id in video_ids:
            get_transcript(video_id, "disk", playlist_title)


