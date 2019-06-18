import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

# set working directory
path = ""
os.chdir(path)

filepath = "DoubanTop250vsIMDB_cleaned.csv"
# filepath = "IMDBTop250vsDouban_cleaned.csv"

# read csv
df = pd.read_csv(filepath, encoding = u"utf-8")

##################################################
#                   histograms                   #
##################################################
fig, axes = plt.subplots(nrows = 1, ncols = 3, figsize = (16,4))
ax1, ax2, ax3 = fig.axes

ax1.hist(df['douban'], bins = 10, range = (0,10))
ax1.set_title('douban top250 rating')

ax2.hist(df['imdb'], bins = 10, range = (0,10)) # bin range = 10
ax2.set_title('Corresponding IMDb rating')

ax3.hist(df['imdb'], bins = 10, range = (0,10), histtype = 'step')
ax3.hist(df['douban'], bins = 10, range = (0,10), histtype = 'step')
ax3.legend(loc = 'upper left')
ax3.set_title('The Two Normalized Distributions')

for ax in fig.axes:
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)

plt.show()

##################################################
#                   pie charts                   #
##################################################
# pie chart of region percentage
regions = []
for r in df.region:
	r = r.split('/')
	regions += r
uniqueRegions = list(set(regions)) # get unique values
counts1 = []
for r in uniqueRegions:
	count= 0
	for i in range(0,len(df.region)):
		regionTags = df.region[i].split('/')
		check = sum([r in regionTags]) # if true + 1 if false + 0
		count += check
	counts1.append(count)
series1 = pd.Series(counts1, index=uniqueRegions, name = "")

# pie chart of genre percentage
def strip(s):
	return s.strip()
genres = []
for g in df.genre:
	g = g.split(',')
	g = list(map(strip, g))
	genres += g
uniqueGenres = list(set(genres)) # get unique values
counts2 = []
for g in uniqueGenres:
	count= 0
	for i in range(0,len(df.genre)):
		genreTags = df.genre[i].split(',')
		genreTags = list(map(strip, genreTags))
		check = sum([g in genreTags]) # if true + 1 if false + 0
		count += check
	counts2.append(count)
series2 = pd.Series(counts2, index=uniqueGenres, name = "")

plt.suptitle('douban top 250')
# 121
fig1 = plt.subplot(121)
series1.plot.pie(figsize=(6,6), autopct='%1.1f%%')
plt.title('Regions')
# 122
fig2 = plt.subplot(122)
series2.plot.pie(figsize=(6,6), autopct='%1.1f%%')
plt.title('Genres')
plt.show()