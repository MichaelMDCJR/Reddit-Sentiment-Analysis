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

async def main():
    # The subreddits to be scanned, 15 of the top subreddits, excluding those with little discussion/humor. Also 5 political subreddits, 1 neutral, 2 left, 2 right
    subreddits = ['popular', 'askreddit', 'worldnews', 'todayilearned', 'music', 'movies', 'science', 'pics', 'news',
                  'gaming', 'DIY', 'futurology', 'explainlikeimfive', 'lifeprotips', 'sports', 'politics', 'democrats',
                  'libertarian', 'republican', 'conservative']
    

    for chosen_sub in subreddits:
        # [titlepos, titleneg, titleneu, titlerating, textpos, textneg, textneu, textrating,commpos, comneg, comneu, comrating, date]
        frame = pandas.DataFrame(columns=['titlepos', 'titleneg', 'titleneu', 'titlerating', 'textpos', 'textneg', 'textneu', 'textrating','commpos', 'comneg', 'comneu', 'comrating', 'date'])
        pandas.set_option("display.max_columns", None)
        display(frame)
        # We grab 70 post but only keep 50, discarding posts with less than 5 comments
        limit = 70

        # The number of post actually being used, as we discard posts with less than 5 comments
        posts_grabbed = 0

        # To test you must visit https://www.reddit.com/prefs/apps and create an app and input given data
        reddit = asyncpraw.Reddit(client_id="----------------", client_secret="---------------",
                              user_agent="------------")

        # Create a sentiment analyzer
        sent_analyzer = SentimentIntensityAnalyzer()

        # file1 = open(str(chosen_sub) + ".csv", "w")
        file1 = open(str(chosen_sub) + ".csv", "a")
        #file1.write("titlepos,titleneg,titleneu,titlerating,textpos,textneg,textneu,textrating,commpos,comneg,comneu,comrating,date\n")

        # Gets the subreddit and loads in the top submissions of that day and adds them to a dataframe
        subreddit = await reddit.subreddit(chosen_sub)
        async for submission in subreddit.top(limit=limit, time_filter="week"):
            # Get the submission comments
            comments = await submission.comments()

            # Check to make sure we grab a max of 50 posts
            if posts_grabbed > 50:
                continue

            # If there is less than 5 comments, skip this submission
            if len(comments) < 5:
                continue
            else:
                posts_grabbed += 1

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

            num_com = 5
            grabbed_com = 0
            total_com_pos = 0
            total_com_neg = 0
            total_com_neu = 0
            com_rating_pos = 0
            com_rating_neg = 0
            com_rating_neu = 0

            # For a number of comments, iterate through them, recording sentiment
            i = 0
            while (i < num_com and i < len(comments)):
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

            print(total_com_neu)
            print(total_com_neg)
            print(total_com_pos)
            total_com_pos = total_com_pos/5.0
            total_com_neg = total_com_neg/5.0
            total_com_neu = total_com_neu/5.0

            # Loop adding rows to data frame
            print(com_rating_pos)
            print(com_rating_neg)
            print(com_rating_neu)

            # Create date object
            date = datetime.datetime.now()

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
            if com_rating_neu + com_rating_neg + com_rating_pos == 5:
                file1.write(str(title_pos_score) + "," + str(title_neg_score) + "," + str(title_neu_score) + "," +
                            str(title_overall_rating) + "," + str(text_pos_score) + "," + str(text_neg_score) + "," +
                            str(text_neu_score) + "," + str(text_overall_rating) + "," + str(total_com_pos) + "," +
                            str(total_com_neg) + "," + str(total_com_neu) + "," + str(com_overall_rating) + "," +
                            date.strftime("%x") + "\n")
                frame.loc[len(frame.index)] = [title_pos_score, title_neg_score, title_neu_score, title_overall_rating,
                                               text_pos_score, text_neg_score, text_neu_score, text_overall_rating,
                                               total_com_pos, total_com_neg, total_com_neu, com_overall_rating,
                                               date.strftime("%x")]

        # Subreddits: Popular, askreddit, worldnews, todayilearned, music, movies, science, pics, news, askscience, DIY, books, explainlikeim5, lifeprotips, sports
        # Politic subreddits: politics, democrats, libertarian, republican, conservative

        await reddit.close()
        display(frame)
        file1.close()


def regular():
    asyncio.run(main())


regular()
