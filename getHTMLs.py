import wikipedia

listsFile = open('data/Titles.txt', 'r')

for line in listsFile:
    try:
        page = wikipedia.page(line.decode('unicode-escape'))

        # For more find https://wikipedia.readthedocs.org/en/latest/code.html#wikipedia.WikipediaPage
        title = page.title
        summary  = page.summary
        html = page.html()
        url = page.url
        links = page.links

    except Exception:
        continue
