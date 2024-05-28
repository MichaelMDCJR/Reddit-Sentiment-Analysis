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


# posts = []
# title = []
# selftext = []
# pos_score = []
# neg_score = []
# neu_score = []
# overall_rating = []
# testing = []

async def main():
    # The number of post actually being used, as we discard videos
    posts_grabbed = 0

    # To test you must visit https://www.reddit.com/prefs/apps and create an app and input given data
    reddit = asyncpraw.Reddit(client_id="----------------", client_secret="---------------",
                              user_agent="------------")

    # Create a sentiment analyzer
    sent_analyzer = SentimentIntensityAnalyzer()

    # Gets the subreddit and loads in the hot submissions into a dictionary
    #subreddit = await reddit.Front()
    subreddit = await reddit.subreddit("politics")
    async for submission in subreddit.top(limit=50, time_filter="day"):
        #print(str(submission.url))
        # posts.append({
        #     "title": submission.title,
        #     "author": str(submission.author),
        #     "image": submission.url,
        #     "text": submission.selftext,
        # })
        # [titlepos, titleneg, titleneu, titlerating, textpos, textneg, textneu, commpos, comneg, comneu, comrating, date]
        title = submission.title
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

        #comment_neu_avg =

        num_com = 5

        #https://asyncpraw.readthedocs.io/en/stable/tutorials/comments.html#extracting-comments

        comments = await submission.comments()
        await comments.replace_more(limit=0)
        for top_level_comment in comments:
            print(top_level_comment.author)

        posts_grabbed += 1

    # for i in range(posts_grabbed):
    #     print(posts[i]["title"])
    #     if posts[i]["text"] != None:
    #        print(posts[i]["text"] + "\n\n")

        '''
        # converts the posts grabbed to raw data to then be put in an image object
        with urllib.request.urlopen(posts[i]["image"]) as u:
            raw_data = u.read()

        image = Image.open(io.BytesIO(raw_data))

        # image is reduced to a smaller size but with same dimesions
        image.thumbnail((550,550))
        #photo = ImageTk.PhotoImage(image)
        '''
    frame = pandas.DataFrame(title)
    frame.columns=["Title"]
    # #if selftext ==:
    #     #frame['Text'] = selftext
    # frame['Positive'] = pos_score
    # frame['Negative'] = neg_score
    # frame['Neutral'] = neu_score
    # frame['Overall'] = overall_rating

    pandas.set_option("display.max_columns", None)
    display(frame)

    #for i in range(posts_grabbed):


    await reddit.close()



def regular():
    asyncio.run(main())


regular()
