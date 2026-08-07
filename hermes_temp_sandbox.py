import urllib.request, urllib.parse, re, webbrowser

def search_and_play_video(search_query):
    """
    Searches for a video on YouTube and plays the first result.
    
    Args:
        search_query (str): The query to search for on YouTube.
    """
    query_string = urllib.parse.quote(search_query)
    url = 'https://www.youtube.com/results?search_query=' + query_string
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    html_content = urllib.request.urlopen(req).read().decode()
    video_ids = re.findall(r'watch\?v=(\S{11})', html_content)
    if video_ids:
        webbrowser.open('https://www.youtube.com/watch?v=' + video_ids[0])
        print('Video playing, Sir.')
    else:
        print('No videos found, Sir.')

def main():
    search_query = 'Python tutorials'
    print(f'Searching for "{search_query}" on YouTube, Sir.')
    search_and_play_video(search_query)

if __name__ == '__main__':
    main()