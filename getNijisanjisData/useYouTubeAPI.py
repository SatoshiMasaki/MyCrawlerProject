import time
import requests
import os
from manageDatabase import getVideoComments, getLiveChat, checkSearchedID

YOUTUBE_API_KEY = os.environ['API_KEY']
URL = 'https://www.googleapis.com/youtube/v3/'
VIDEO_ID_RECORD = "datas/videoId.txt"


def get_chat_id(target_url):
    """
    https://developers.google.com/youtube/v3/docs/videos/list?hl=ja

    チャット欄の取得は原則リアルタイムのみ。
    """
    video_id = target_url.replace('https://www.youtube.com/watch?v=', '')

    api_video_url = 'https://www.googleapis.com/youtube/v3/videos'
    params = {'key': YOUTUBE_API_KEY, 'id': video_id, 'part': 'liveStreamingDetails'}
    data = requests.get(api_video_url, params=params).json()
    channel_id = None
    video_title = None
    # channel_id = data['items'][0]['snippet']['channelId']
    # video_title = data['items'][0]['snippet']['title']
    liveStreamingDetails = data['items'][0]['liveStreamingDetails']
    if 'activeLiveChatId' in liveStreamingDetails.keys():
        chat_id = liveStreamingDetails['activeLiveChatId']
        print('get_chat_id done!')
    else:
        chat_id = None
        print('NOT live')

    return chat_id, channel_id, video_title, video_id


def get_chat(chat_id, channel_id, video_title, video_id, pageToken):
    """
    https://developers.google.com/youtube/v3/live/docs/liveChatMessages/list
    """
    api_messages_url = 'https://www.googleapis.com/youtube/v3/liveChat/messages'
    params = {'key': YOUTUBE_API_KEY, 'liveChatId': chat_id, 'part': 'id,snippet,authorDetails'}
    if type(pageToken) == str:
        params['pageToken'] = pageToken

    data = requests.get(api_messages_url, params=params).json()

    try:
        for item in data['items']:
            # channelId = item['snippet']['authorChannelId']
            msg = item['snippet']['displayMessage']

            getLiveChat((video_id, video_title, channel_id, None, msg))
            # usr = item['authorDetails']['displayName']
            # supChat   = item['snippet']['superChatDetails']
            # supStic   = item['snippet']['superStickerDetails']

    except Exception as e:
        print(e)
        pass

    time.sleep(2)
    if data['nextPageToken']:
        get_chat(chat_id, channel_id, video_title, video_id, data['nextPageToken'])


def main_chat(target_url):
    chat_id, channel_id, video_title, video_id = get_chat_id(target_url)

    nextPageToken = None
    get_chat(chat_id, channel_id, video_title, video_id, nextPageToken)


def searchVideoComment(video_id, next_page_token):
    api_video_url = 'https://www.googleapis.com/youtube/v3/videos'
    params = {'key': YOUTUBE_API_KEY, 'id': video_id, 'part': 'snippet'}

    if '\n' in video_id:
        video_id = video_id.replace("\n", "")
    datas = requests.get(api_video_url, params=params).json()

    video_title = None
    channel_id = None
    channel_name = None
    published_date = None

    for data in datas['items']:
        video_title = data['snippet']['title']
        channel_id = data['snippet']['channelId']
        channel_name = data['snippet']['channelTitle']
        published_date = data['snippet']['publishedAt']
        break

    params = {
        'key': YOUTUBE_API_KEY,
        'part': 'snippet',
        'videoId': video_id,
        'order': 'relevance',
        'textFormat': 'plaintext',
        'maxResults': 100,
    }
    if next_page_token is not None:
        params['pageToken'] = next_page_token
    response = requests.get(URL + 'commentThreads', params=params)
    resource = response.json()
    print(resource)

    for comment_info in resource['items']:
        comment = comment_info['snippet']['topLevelComment']['snippet']['textDisplay']
        getVideoComments((video_id, video_title, channel_id, channel_name, comment, published_date, 0))

    if 'nextPageToken' in resource:
        searchVideoComment(video_id, resource["nextPageToken"])


def searchVideoID(channel_id, next_page_token):
    params = {
        'key': YOUTUBE_API_KEY,
        'part': 'id',
        'channelId': channel_id,
        'order': 'date',
        'maxResults': 100,
        'type': 'video'
    }
    if next_page_token is not None:
        params['pageToken'] = next_page_token
    response = requests.get(URL + 'search', params=params)
    resource = response.json()
    video_id = []

    for item in resource['items']:
        video_id.append(item['id']['videoId'])

    with open(VIDEO_ID_RECORD, mode="a") as f:
        f.write('\n')
        f.write('\n'.join(video_id))

    if 'nextPageToken' in resource:
        searchVideoID(channel_id, resource["nextPageToken"])


def main_video_id(url):
    video_id = url.replace('https://www.youtube.com/channel/', '')
    searchVideoID(video_id, None)


def main_comment(target_url):
    video_id = target_url.replace('https://www.youtube.com/watch?v=', '')
    searchVideoComment(video_id, None)


def fileToDB():
    # TODO 歌動画はコメントが多すぎるので要対応
    with open(VIDEO_ID_RECORD, "rt") as f:
        id_list = f.readlines()

    for video_id in id_list:
        if checkSearchedID(video_id):  # TODO ファイルからIDを削除する
            pass
        else:
            print(video_id)
            searchVideoComment(video_id, None)
        time.sleep(1)


if __name__ == '__main__':
    # url = input('Input YouTube URL > ')
    # main_video_id(url)

    fileToDB()
