import numpy as np
import matplotlib.pyplot as plt
import pandas

subreddits = ['popular', 'askreddit', 'worldnews', 'todayilearned', 'music', 'movies', 'science', 'pics', 'news',
                  'askscience', 'DIY', 'futurology', 'explainlikeimfive', 'lifeprotips', 'sports', 'politics', 'democrats',
                  'libertarian', 'republican', 'conservative']

# Bar plot with average %pos %neg and %neu per subreddit
complete_frame = pandas.DataFrame(columns=["Subreddit", "Title Positive", "Title Negative", "Title Neutral", "Comment Positive",
                                           "Comment Negative", "Comment Neutral"])
for i in range(len(subreddits)):
    new_frame = pandas.read_parquet(str(subreddits[i] + ".gzip"))
    title_sentiment_counts = new_frame['titlerating'].value_counts()
    title_pos = title_sentiment_counts.get("Positive", 0)
    title_neg = title_sentiment_counts.get("Negative", 0)
    title_neu = title_sentiment_counts.get("Neutral", 0)

    com_sentiment_counts = new_frame['comrating'].value_counts()
    com_pos = com_sentiment_counts.get("Positive", 0)
    com_neg = com_sentiment_counts.get("Negative", 0)
    com_neu = com_sentiment_counts.get("Neutral", 0)

    complete_frame.loc[len(complete_frame.index)] = [subreddits[i], title_pos,title_neg, title_neu, com_pos, com_neg, com_neu]

complete_frame.set_index([subreddits]).plot(kind="bar")
plt.show()
complete_frame = pandas.DataFrame(columns=["Date", "Percent Positive", "Percent Negative", "Percent Neutral"])
chosen_sub = "test"
#new_frame = pandas.read_parquet(str(chosen_sub + ".gzip"))
new_frame = pandas.read_csv(str(chosen_sub + ".csv"))
initial_date = new_frame.iloc[0][12]
end_date = new_frame.iloc[len(new_frame.index)-1][12]
chosen_date = new_frame.iloc[0][12]
counter = 0
while chosen_date < end_date:
    current_date = new_frame.iloc[counter][12]
    num_submissions = 0
    if current_date == chosen_date:
        print("J")

    print(initial_date)
    print("test" + end_date)
