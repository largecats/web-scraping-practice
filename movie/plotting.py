import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

filepath = "C:/Users/LENOVO/Fun/Programming/data science/cmu practical data science course/mynotes/web scraping/DoubanTop250vsIMDB_cleaned.csv"
#filepath = "C:/Users/LENOVO/Fun/Programming/data science/cmu practical data science course/mynotes/web scraping/IMDBTop250vsDouban_movie_ratings.csv"
df = pd.read_csv(filepath, encoding = u"utf-8")


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

'''
plt.figure(0)
series1.plot.pie(figsize=(6,6))

plt.figure(1)
series2.plot.pie(figsize=(6,6))
'''

'''
# create a figure with two subplots
fig, (ax1, ax2) = plt.subplots(1, 2, subplot_kw={'aspect':'equal'})

# plot each pie chart in a separate subplot
ax1.pie(counts1)
ax2.pie(counts2)

plt.show()
'''

plt.suptitle('douban top 250')
# 121 > 1行2列第1个
fig1 = plt.subplot(121)
series1.plot.pie(figsize=(6,6), autopct='%1.1f%%')
plt.title('Regions')
# 122 > 1行2列第2个
fig2 = plt.subplot(122)
series2.plot.pie(figsize=(6,6), autopct='%1.1f%%')
plt.title('Genres')

plt.show()


'''
fig, axes = plt.subplots(nrows = 1, ncols = 2, figsize = (6,6))
ax1, ax2 = fig.axes
ax1.pie(counts1, labels=uniqueRegions, autopct='%1.1f%%')
ax1.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle.
ax1.set_title('Regions')

ax2.pie(counts2, labels=uniqueGenres, autopct='%1.1f%%')
ax2.axis('equal')
ax2.set_title('Genres')

plt.show()
'''