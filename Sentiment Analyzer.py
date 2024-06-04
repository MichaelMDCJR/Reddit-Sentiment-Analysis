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
    pandas.set_option("display.max_columns", None)
    display(frame)

    file1 = open("MyFile1.txt", "w+")
    file1.write("titlepos\t titleneg\t titleneu\t titlerating\t textpos\t textneg\t textneu\t textrating\t commpos\t comneg\t comneu\t comrating\t date\n")

    # The number of post actually being used, as we discard videos
    posts_grabbed = 0

    # To test you must visit https://www.reddit.com/prefs/apps and create an app and input given data
    reddit = asyncpraw.Reddit(client_id="----------------", client_secret="---------------",
                              user_agent="------------")

    # Create a sentiment analyzer
    sent_analyzer = SentimentIntensityAnalyzer()

    # The subreddits to be scanned, 15 of the top subreddits, excluding those with little discussion/humor. Also 5 political subreddits, 1 neutral, 2 left, 2 right
    subreddits = ['popular', 'askreddit', 'worldnews', 'todayilearned', 'music', 'movies', 'science', 'pics', 'news', 'askscience', 'DIY', 'books', 'explainlikeimfive', 'lifeprotips', 'sports', 'politics', 'democrats', 'libertarian', 'republican', 'conservative']
    #Most subreddits will get the top 50 posts, but since r/repbulican is smaller, it will only draw 25
    comments_to_get = [50, 25]

    # Gets the subreddit and loads in the top submissions of that day and adds them to a dataframe
    subreddit = await reddit.subreddit("politics")
    async for submission in subreddit.top(limit=50, time_filter="day"):
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
        while (i < num_com and i < len(comments)):
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

        # Rounding values
        title_pos_score = round(title_pos_score, 2)
        title_neg_score = round(title_neg_score, 2)
        title_neu_score = round(title_neu_score, 2)

        if submission.is_self:
            text_pos_score = round(text_pos_score, 2)
            text_neg_score = round(text_neg_score, 2)
            text_neu_score = round(text_neu_score, 2)

        total_com_pos = round(total_com_pos, 2)
        total_com_neg = round(total_com_neg, 2)
        total_com_neu = round(total_com_neu, 2)

        # Add row to data frame if there are enough comments
        if (com_rating_neu + com_rating_neg + com_rating_pos == 5):
            file1.write(str(title_pos_score) + "\t\t\t\t\t" + str(title_neg_score) + "\t\t\t\t\t" + str(title_neu_score) + "\t\t\t\t\t" + str(title_overall_rating) + "\t\t\t\t\t" + str(text_pos_score) + "\t\t\t\t\t" + str(text_neg_score) + "\t\t\t\t\t" + str(text_neu_score) + "\t\t\t\t\t" + str(text_overall_rating) + "\t\t\t\t\t" + str(total_com_pos) + "\t\t\t\t\t" + str(total_com_neg) + "\t\t\t\t\t" + str(total_com_neu) + "\t\t\t\t\t" + str(com_overall_rating) + "\t\t\t\t\t" + date.strftime("%x") + "\n")
            frame.loc[len(frame.index)] = [title_pos_score, title_neg_score, title_neu_score, title_overall_rating, text_pos_score, text_neg_score, text_neu_score, text_overall_rating, total_com_pos, total_com_neg, total_com_neu, com_overall_rating, date.strftime("%x")]
            #frame.to_csv("out.txt", sep="\t\t\t\t")

# Subreddits: Popular, askreddit, worldnews, todayilearned, music, movies, science, pics, news, askscience, DIY, books, explainlikeim5, lifeprotips, sports
    # Politic subreddits: politics, democrats, libertarian, republican, conservative

    await reddit.close()

    display(frame)
    file1.close()


def regular():
    asyncio.run(main())


regular()
