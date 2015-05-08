import wikipedia

listsFile = open('data/Titles.txt', 'r')
problemsFile = open('data/ProblemTitles.txt', 'w')

count = 0
for line in listsFile:
    print count
    count += 1
    try:
        page = wikipedia.page(line.decode('unicode-escape'))
    except Exception:
        problemsFile.write(line)

problemsFile.close()
