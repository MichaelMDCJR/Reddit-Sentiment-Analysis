from datetime import datetime
from datetime import timedelta

import numpy as np
import matplotlib.pyplot as plt
import pandas

#subreddits = ['popular', 'askreddit', 'worldnews', 'todayilearned', 'music', 'movies', 'science', 'pics', 'news',
#                  'askscience', 'DIY', 'futurology', 'explainlikeimfive', 'lifeprotips', 'sports', 'politics', 'democrats',
 #                 'libertarian', 'republican', 'conservative']

subreddits = ['askreddit']

# Bar plot with average %pos %neg and %neu per subreddit
complete_frame = pandas.DataFrame(columns=["Subreddit", "Title Positive", "Title Negative", "Title Neutral", "Comment Positive",
                                           "Comment Negative", "Comment Neutral"])
# First graph: bar graph of # of positive,negative, and neutral comments
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

# Second graph
complete_frame = pandas.DataFrame(columns=["Date", "Percent Positive", "Percent Negative", "Percent Neutral"])
#chosen_sub = "test"
chosen_sub = "askreddit"
new_frame = pandas.read_parquet(str(chosen_sub + ".gzip"))
print(new_frame)
#new_frame = pandas.read_csv(str(chosen_sub + ".csv"))

# Initialize the sums
pos_sum = 0
neg_sum = 0
neu_sum = 0

# Create a new DataFrame to store the results
result_df = pandas.DataFrame(columns=['Date', 'Sum'])

# Iterate through unique dates in the original DataFrame
for date in new_frame['date'].unique():
    # Filter rows with the current date
    rows_with_date = new_frame[new_frame['date'] == date]
    # Calculate the sum of 'Value' for the current date
    pos_sum += rows_with_date['titlepos'].sum()
    neg_sum += rows_with_date['titleneg'].sum()
    neu_sum += rows_with_date['titleneu'].sum()
    # The number of rows summed from
    num_rows = len(rows_with_date)
    # Append the date and sum to the frame to be plotted
    complete_frame.loc[len(complete_frame.index)] = [date, pos_sum/num_rows, neg_sum/num_rows, neu_sum/num_rows]
    # Reset the sums
    pos_sum = 0
    neg_sum = 0
    neu_sum = 0

# Now result_df contains the sums for each unique date
print(complete_frame)

# Plot
complete_frame.set_index(['Date'], inplace=True)
complete_frame.plot(kind="line")
plt.show()