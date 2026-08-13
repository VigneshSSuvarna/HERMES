import webbrowser

def web_search(query):
    url = "https://duckduckgo.com/?q=" + query
    webbrowser.open(url)
    print("Web search opened, Sir.")

def main():
    query = "current weather in Tokyo"
    web_search(query)

if __name__ == "__main__":
    main()