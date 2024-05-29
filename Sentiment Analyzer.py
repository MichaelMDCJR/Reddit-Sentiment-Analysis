import io
import urllib.request
from tkinter import *
import time
import asyncpraw
import urllib3
import asyncio
from PIL import ImageTk, Image
import requests
from io import BytesIO
import pandas
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from IPython.display import display
import datetime


# posts = []
# title = []
# selftext = []
# pos_score = []
# neg_score = []
# neu_score = []
# overall_rating = []
# testing = []

async def main():
    # TEMP CREATE DATA FRAME
    # [titlepos, titleneg, titleneu, titlerating, textpos, textneg, textneu, textrating,commpos, comneg, comneu, comrating, date]
    frame = pandas.DataFrame(columns=['titlepos', 'titleneg', 'titleneu', 'titlerating', 'textpos', 'textneg', 'textneu', 'textrating','commpos', 'comneg', 'comneu', 'comrating', 'date'])
    #frame.columns = ["Title"]

    pandas.set_option("display.max_columns", None)
    display(frame)

    # The number of post actually being used, as we discard videos
    posts_grabbed = 0

    # To test you must visit https://www.reddit.com/prefs/apps and create an app and input given data
    reddit = asyncpraw.Reddit(client_id="----------------", client_secret="---------------",
                              user_agent="------------")

    # Create a sentiment analyzer
    sent_analyzer = SentimentIntensityAnalyzer()

    # Gets the subreddit and loads in the hot submissions into a dictionary
    #subreddit = await reddit.Front()
    subreddit = await reddit.subreddit("popular")
    async for submission in subreddit.top(limit=5, time_filter="day"):
        # [titlepos, titleneg, titleneu, titlerating, textpos, textneg, textneu, commpos, comneg, comneu, comrating, date]
        title = submission.title
        print(title)
        sentiment_dict = sent_analyzer.polarity_scores(title)
        title_neg_score = sentiment_dict['neg'] * 100
        title_pos_score = sentiment_dict['pos'] * 100
        title_neu_score = sentiment_dict['neu'] * 100
        if sentiment_dict['compound'] >= 0.05:
            title_overall_rating = "Positive"
        elif sentiment_dict['compound'] <= -0.05:
            title_overall_rating = "Negative"
        else:
            title_overall_rating = "Neutral"
        # Analyzes text if post is a text post
        if submission.is_self:
            #selftext.append(submission.selftext)
            sentiment_dict = sent_analyzer.polarity_scores(submission.selftext)
            text_neg_score = sentiment_dict['neg'] * 100
            text_pos_score = sentiment_dict['pos'] * 100
            text_neu_score = sentiment_dict['neu'] * 100
            if sentiment_dict['compound'] >= 0.05:
                text_overall_rating = "Positive"
            elif sentiment_dict['compound'] <= -0.05:
                text_overall_rating = "Negative"
            else:
                text_overall_rating = "Neutral"
        else:
            text_pos_score = pandas.NA
            text_neu_score = pandas.NA
            text_neg_score = pandas.NA
            text_overall_rating = pandas.NA

        #comment_neu_avg =

        num_com = 5
        grabbed_com = 0
        total_com_pos = 0
        total_com_neg = 0
        total_com_neu = 0
        com_rating_pos = 0
        com_rating_neg = 0
        com_rating_neu = 0



        #https://asyncpraw.readthedocs.io/en/stable/tutorials/comments.html#extracting-comments

        # Get the submission comments
        comments = await submission.comments()
        #await comments.replace_more(limit=0)

        # For a number of comments, iterate through them, recording sentiment
        i = 0
        while (i < num_com):
        #for i in num_com:
            #TESTING REMOVE LATER
            com_overall_rating = ""

            top_level_comment = comments[i]
            # Ignore comments by automoderator
            if top_level_comment.author != "Automoderator":
                print(top_level_comment.author)

                com_text = top_level_comment.body
                sentiment_dict = sent_analyzer.polarity_scores(com_text)
                total_com_neg += sentiment_dict['neg'] * 100
                total_com_pos += sentiment_dict['pos'] * 100
                total_com_neu += sentiment_dict['neu'] * 100
                if sentiment_dict['compound'] >= 0.05:
                    com_rating_pos += 1
                elif sentiment_dict['compound'] <= -0.05:
                    com_rating_neg += 1
                else:
                    com_rating_neu += 1

                # If comments are a majority polarity, set that as the overall rating
                if com_rating_neu >= 3:
                    com_overall_rating = "Neutral"
                elif com_rating_neg >= 3:
                    com_overall_rating = "Negative"
                elif com_rating_pos >= 3:
                    com_overall_rating = "Positive"

                # If the ratings are mixed with neutral, prefer the pos or neg rating
                if com_rating_neu == 2 and com_rating_pos == 2:
                    com_overall_rating = "Positive"
                elif com_rating_neu == 2 and com_rating_neg == 2:
                    com_overall_rating = "Negative"
                # If ratings are split pos and neg, choose based on polarity scores
                elif com_rating_pos == 2 and com_rating_neg == 2:
                    if total_com_pos > total_com_neg:
                        com_overall_rating = "Positive"
                    else:
                        com_overall_rating = "Negative"

            # If there is an automod comment, add 1 to the number of comments to be grabbed
            else:
                num_com += 1
                print("YAYYYYYYYYYY")
                print("Num of com" + str(num_com))

            i += 1


        posts_grabbed += 1

        print(total_com_neu)
        print(total_com_neg)
        print(total_com_pos)
        total_com_pos = total_com_pos/5.0
        total_com_neg = total_com_neg/5.0
        total_com_neu = total_com_neu/5.0


        # [titlepos, titleneg, titleneu, titlerating, textpos, textneg, textneu, textrating, commpos, comneg, comneu, comrating, date]
        # Loop adding rows to data frame
        print(com_rating_pos)
        print(com_rating_neg)
        print(com_rating_neu)

        # Create date object
        date = datetime.datetime.now()
        #print(date.strftime("%x"))

        # Add row to data frame
        frame.loc[len(frame.index)] = [title_pos_score, title_neg_score, title_neu_score, title_overall_rating, text_pos_score, text_neg_score, text_neu_score, text_overall_rating, total_com_pos, total_com_neg, total_com_neu, com_overall_rating, date.strftime("%x")]


    await reddit.close()

    display(frame)


def regular():
    asyncio.run(main())


regular()
