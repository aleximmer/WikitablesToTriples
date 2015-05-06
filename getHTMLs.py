import wikipedia

listsFile = open('data/Titles.txt', 'r')
problemsFile = open('data/ProblemTitles.txt', 'a')

for line in listsFile:
    try:
        page = wikipedia.page(line.decode('unicode-escape'))
    except Exception:
        problemsFile.write(line)

problemsFile.close()
