import streamlit as st 
import pandas as pd
from pages import Search


if __name__ == "__main__":
    st.set_page_config(layout = "wide")
    st.title("YouTube Data Harvesting and Warehousing using SQL and Streamlit")
    st.title("Question & Answer")
    st.divider()     


    DATA = {
            "What are the names of all the videos and their corresponding channels?" : ["select title as CHANNEL_NAME, videotable.VIDEO_NAME from channeldata JOIN videotable on channeldata.playlist_id = videotable.PLAYLIST_ID;",["CHANNEL NAME", "VIDEO NAME"]],
            "Which channels have the most number of videos, and how many videos do they have?" : ["select title as CHANNEL_NAME, videoCount from channeldata where videoCount = (select max(videoCount) from channeldata);",["CHANNEL_NAME", "videoCount"]],
            "What are the top 10 most viewed videos and their respective channels?" : ["SELECT channeldata.title as CHANNEL_NAME, VIDEO_NAME, VIEW_COUNT FROM videotable join channeldata on  videotable.PLAYLIST_ID = channeldata.playlist_id order by  VIEW_COUNT desc LIMIT 10;", ["CHANNEL_NAME", "VIDEO_NAME", "VIEW_COUNT"]],
            "How many comments were made on each video, and what are their corresponding video names?" : ["select title as CHANNEL_NAME, videotable.VIDEO_NAME, videotable.COMMENT_COUNT FROM channeldata join videotable on channeldata.playlist_id = videotable.PLAYLIST_ID;",["CHANNEL_NAME", "VIDEO_NAME", "COMMENT_COUNT"]],
            "Which videos have the highest number of likes, and what are their  corresponding channel names?" : ["select channeldata.title as CHANNEL_NAME,  VIDEO_NAME, LIKE_COUNT  FROM videotable join channeldata on  videotable.playlist_id = channeldata.PLAYLIST_ID where LIKE_COUNT = (select max(LIKE_COUNT) FROM videotable);",["CHANNEL_NAME", "VIDEO_NAME", "LIKE_COUNT"]],
            "What is the total number of likes and dislikes for each video, and what are their corresponding video names?" : ["SELECT VIDEO_NAME, LIKE_COUNT FROM videotable;",["VIDEO_NAME", "LIKE_COUNT"]],
            "What is the total number of views for each channel, and what are their corresponding channel names?" : ["select title as CHANNEL_NAME, viewCount from channeldata;",["CHANNEL_NAME", "viewCount"]],
            "What are the names of all the channels that have published videos in the year 2022?" : ["SELECT title as CHANNEL_NAME from channeldata join videotable on channeldata.playlist_id = videotable.PLAYLIST_ID where YEAR(PUBLISHED_DATE) = '2022' group by title;",["CHANNEL_NAME"]],
            "What is the average duration of all videos in each channel, and what are their corresponding channel names?" : ["SELECT title as CHANNEL_NAME, avg(videotable.DURATION) as AVERAGE_DURATION_IN_SECOND from channeldata join videotable on channeldata.playlist_id = videotable.PLAYLIST_ID group by title;",["CHANNEL_NAME", "AVERAGE_DURATION_IN_SECOND"]],
            "Which videos have the highest number of comments, and what are their corresponding channel names?" : ["select title as CHANNEL_NAME ,VIDEO_NAME, videotable.COMMENT_COUNT from videotable join channeldata on videotable.PLAYLIST_ID = channeldata.playlist_id where COMMENT_COUNT = (SELECT max(COMMENT_COUNT) from videotable);",["CHANNEL_NAME", "VIDEO_NAME", "COMMENT_COUNT"]]
            }
    
    Q = st.selectbox("*select one*", DATA.keys())
    button_2 = st.button("*Submit*")
    if button_2:
        if Q:
            st.write("*Selected Question is -*", Q)
            result = Search.select_sql(DATA[Q][0])
            df = pd.DataFrame(result, columns=DATA[Q][1])
            st.dataframe(df, width = 1240)
            
        else:
            st.write("*Select one question*")

        