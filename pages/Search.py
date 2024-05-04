import streamlit as st
import googleapiclient.discovery
import mysql.connector
import pandas as pd

st.set_page_config(
    layout = "wide"
    )

# build connection 
def apiconnection(api_service_name, api_version, developer_key):
    youtubeapiconnection  =  googleapiclient.discovery.build(api_service_name, api_version, developerKey=developer_key)
    return youtubeapiconnection
#data fetching from youtubeapi function
def channelData(youtubeApiConnection, input):
    response = youtubeApiConnection.channels().list(
        id = input,
        part = 'snippet,statistics,contentDetails'
    )
    channel_data = response.execute()
    return channel_data
#videoid fetching function
def videoIdData(youtubeApiConnection, playlist_id):
    video_ids = []
    next_page_token = None
    while True:
        # Make API request
        request1 = youtubeApiConnection.playlistItems().list(
            part="contentDetails",
            playlistId=playlist_id,
            maxResults = 50,
            pageToken=next_page_token
        )
        response = request1.execute()
        # Process response
        for i in range(len(response["items"])):
            video_ids.append(response["items"][i]["contentDetails"]["videoId"]) 
        next_page_token = response.get("nextPageToken")
        if next_page_token is None:
            break
    return video_ids
#video detail fetching frm video id
def videoIdDetails(youtubeApiConnection,videoids):
    list_of_data = []  
    for i in videoids:
        request2 = youtubeApiConnection.videos().list(
            part = 'snippet,statistics,contentDetails',
            id   = i
        )
        response2 = request2.execute()
        data = {
            "VIDEO_ID" : i,
            "VIDEO_NAME" : response2["items"][0]["snippet"]["title"],
            "VIDEO_DESCRIPTIOIN" : response2["items"][0]["snippet"]["description"],
            "PUBLISHED_DATE" : response2["items"][0]["snippet"]["publishedAt"],
            "TUMBNAIL" : response2["items"][0]["snippet"]["thumbnails"]["default"]["url"] 
                if "thumbnails" in response2["items"][0]["snippet"] else None,
            "VIEW_COUNT" : response2["items"][0]["statistics"]["viewCount"]
                if "viewCount" in response2["items"][0]["statistics"] else 0,
            "LIKE_COUNT" : response2["items"][0]["statistics"]["likeCount"]
                if "likeCount" in response2["items"][0]["statistics"] else 0,
            "FAVORITE_COUNT" : response2["items"][0]["statistics"]["favoriteCount"]
                if "favoriteCount" in response2["items"][0]["statistics"] else 0,
            "COMMENT_COUNT" : response2["items"][0]["statistics"]["commentCount"] 
                if "commentCount" in response2["items"][0]["statistics"] else 0,
            "DURATION" : response2["items"][0]["contentDetails"]["duration"]
                if "duration" in response2["items"][0]["contentDetails"] else None
        }
        list_of_data.append(data)
    return list_of_data
#channel data filter from response function
def channeldatafilter(data):
    #snippet
    id = data['items'][0]['id']
    title = data['items'][0]['snippet']['localized']['title']
    description = data['items'][0]['snippet']['localized']['description']
    #contentDetails
    playlist_id = data['items'][0]['contentDetails']['relatedPlaylists']['uploads']
    #statistics
    viewCount = data['items'][0]['statistics']['viewCount']
    subscriberCount = data['items'][0]['statistics']['subscriberCount']
    videoCount=data['items'][0]['statistics']['videoCount']
    return id,title,description,playlist_id,viewCount,subscriberCount,videoCount
#comment data function
def commentdata(youtubeApiConnection, videoids):
    comment_data = []
    try:
        for i in videoids:
            request3 = youtubeApiConnection.commentThreads().list(
                part="snippet",
                videoId = i,
                maxResults=50
            )
            response3 = request3.execute()
            for comment in response3['items']:
                comment_information = {
                    "videoId":comment['snippet']['topLevelComment']['snippet']['videoId'],
                    "Comment_Id": comment['snippet']['topLevelComment']['id'],
                    "Comment_Text": comment['snippet']['topLevelComment']['snippet']['textDisplay'],
                    "Comment_Author": comment['snippet']['topLevelComment']['snippet']['authorDisplayName'],
                    "Comment_PublishedAt": comment['snippet']['topLevelComment']['snippet']['publishedAt']
                }
                comment_data.append(comment_information)
        
    except:
        pass
    return comment_data
#mysql connetion function
def mysql_connector_connect():
    connection = mysql.connector.connect(
        host = 'localhost',
        port = 3306,
        user = 'root',
        password = '1234',
        database = 'youtube'
    )
    return connection

# check function
def ispresent(querry):
    connection = mysql_connector_connect()
    cursor = connection.cursor()
    cursor.execute(querry)
    result = cursor.fetchall()
    connection.close()
    return True if result else False

#select querry for sql
def select_sql(querry):
    connection = mysql_connector_connect()
    cursor = connection.cursor()
    cursor.execute(querry)
    list_of_channel_data = cursor.fetchall()
    connection.close()
    return list_of_channel_data
#column output based on tablename
def choose_columns(table_name):
    youtube = {
        "channeldata" : ["channelid","title","description","playlist_id","viewCount","subscriberCount","videoCount"],
        "videotable" : ["VIDEO_ID","PLAYLIST_ID","VIDEO_NAME","VIDEO_DESCRIPTIOIN","PUBLISHED_DATE","TUMBNAIL","VIEW_COUNT","LIKE_COUNT","FAVORITE_COUNT","COMMENT_COUNT","DURATION"],
        "commenttable" : ["video_id", "comment_id", "comment_text", "comment_author", "comment_published_data"],
        "AllTable" : ["channelid","title","description","playlist_id","viewCount","subscriberCount","videoCount",
                      "videotable.VIDEO_ID","videotable.PLAYLIST_ID","videotable.VIDEO_NAME","videotable.VIDEO_DESCRIPTIOIN","videotable.PUBLISHED_DATE","videotable.TUMBNAIL","videotable.VIEW_COUNT",
                      "videotable.LIKE_COUNT","videotable.FAVORITE_COUNT","videotable.COMMENT_COUNT","videotable.DURATION",
                      "commenttable.comment_id", "commenttable.comment_text", "commenttable.comment_author", "commenttable.comment_published_data"]
    }
    return youtube[table_name]
#select columns are changed to string
def stringchanger(column_name):
    initial = ""
    for index, value in enumerate(column_name):
        if index == 0:
            initial = initial + value
        else:
            initial = initial + ", " + value
    return initial
#select primary key based on choosed table
def primary_key(table_name):
    primaryKey = {
        "channeldata": "channelid",
        "videotable" : "VIDEO_ID",
        "commenttable" : "comment_id"
    }
    return primaryKey[table_name]
#video duration to second convertor
def duration_sec(sam1):
  try:
    sam1 = sam1[2::]
    value = {'H': None, 'M': None, 'S': None}
    for i in value.keys():
        if i in sam1:
            index = sam1.index(i)
            value[i] = index
    values = {}
    if value['H']:
        values['H'] = sam1[0:value['H']] 
        values['M'] = sam1[value['H']+1:value['M']] if value['M'] else None
        values['S'] = sam1[value['M']+1:value['S']] if value['S'] else None
    elif value['M']:
        values['M'] = sam1[0:value['M']] 
        values['S'] = sam1[value['M']+1:value['S']] if value['S'] else None
    else:
        values['S'] = sam1[0:value['S']]
    for j in values.keys():
        if values[j]:
            if j == "H":
                values[j] = int(values[j]) * 3600
            if j == "M":
                values[j] = int(values[j]) * 60
            if j == "S":
                values[j] = int(values[j])
    result = 0
    for k in values.values():   
        if k:
            result = result + k
    return result
  except:
      None
#This function used to insert or update in video and comment data
def insert_update_videodata(con,querry,video_values):
    #insert into table("column name") values("column values");
    cursor = con.cursor()
    cursor.execute(operation = querry,params = video_values)
    con.commit()
    return "**Saved Successfully**"

#insert or update channeldata to sql youtiube database function
def channel_sql(table_name,column_name,values):
    con = mysql_connector_connect()
    querry_insert = f'insert into {table_name} {column_name} values (%s, %s, %s, %s, %s, %s, %s)'
    # update querry
    query_update = f'update {table_name} set channelid = %s, title=%s, description=%s, playlist_id=%s, viewCount=%s, subscriberCount=%s, videoCount=%s where channelid = "{id}"'
    # check querry
    querry_check = f'select * from {table_name} where channelid = "{id}";'
    #function selection
    Result = insert_update_videodata(con, query_update, values) if ispresent(querry_check) else insert_update_videodata(con, querry_insert,values)
    con.close()
    return Result

def video_data_inputer(list_of_data,video_table_name,video_column_name,playlist_id):   
    con = mysql_connector_connect()
    for i in range(len(list_of_data)):
        value_in_dict = list_of_data[i]   
        video_values = (value_in_dict["VIDEO_ID"], playlist_id, value_in_dict["VIDEO_NAME"], value_in_dict["VIDEO_DESCRIPTIOIN"], value_in_dict["PUBLISHED_DATE"][0:10]+" "+value_in_dict["PUBLISHED_DATE"][11:(len(value_in_dict["PUBLISHED_DATE"])-1)] ,value_in_dict["TUMBNAIL"], value_in_dict["VIEW_COUNT"], value_in_dict["LIKE_COUNT"], value_in_dict["FAVORITE_COUNT"], value_in_dict["COMMENT_COUNT"], duration_sec(value_in_dict["DURATION"]))
        video_querry_insert = f'insert into {video_table_name} {video_column_name} values (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)'
        # update querry
        video_query_update = f'update {video_table_name} set VIDEO_ID =( %s),PLAYLIST_ID = (%s), VIDEO_NAME=(%s),VIDEO_DESCRIPTIOIN= (%s), PUBLISHED_DATE = (%s), TUMBNAIL=(%s),VIEW_COUNT = (%s),LIKE_COUNT=(%s),FAVORITE_COUNT=(%s),COMMENT_COUNT=(%s),DURATION=(%s) where VIDEO_ID = "{value_in_dict["VIDEO_ID"]}"'
        # check querry
        video_querry_check = f'select * from {video_table_name} where VIDEO_ID = "{value_in_dict["VIDEO_ID"]}";'
        #function selection
        Result1 = insert_update_videodata(con, video_query_update, video_values) if ispresent(video_querry_check) else insert_update_videodata(con, video_querry_insert,video_values)
    con.close()
    return Result1

def comment_sql(list_of_comment,comment_table_name,comment_column_name):
    con = mysql_connector_connect()
    for i in range(len(list_of_comment)):
        value_in_dict = list_of_comment[i]
        comment_values = (value_in_dict["videoId"],value_in_dict["Comment_Id"],value_in_dict["Comment_Text"],value_in_dict["Comment_Author"], value_in_dict["Comment_PublishedAt"][0:10]+" "+value_in_dict["Comment_PublishedAt"][11:(len(value_in_dict["Comment_PublishedAt"])-1)])
        comment_querry_insert = f'insert into {comment_table_name} {comment_column_name} values (%s, %s, %s, %s, %s)'
        # update querry
        comment_query_update = f"update {comment_table_name} set video_id = %s, comment_id = %s, comment_text= %s, comment_author= %s, comment_published_data = %s where comment_id = '{value_in_dict["Comment_Id"]}'"
        # check querry
        comment_querry_check = f'select * from {comment_table_name} where comment_id = "{value_in_dict["Comment_Id"]}";'
        #function selection
        Result1 = insert_update_videodata(con,comment_query_update,comment_values) if ispresent(comment_querry_check) else insert_update_videodata(con,comment_querry_insert,comment_values)                
    con.close()
    return Result1




if __name__ == "__main__":
    st.title("YouTube Data Harvesting and Warehousing using SQL and Streamlit")
    st.title("Search")
    st.divider()
    choose_input = st.selectbox("*Select one method*", ("Select one","Data from SQL database", "Data from youTube API"))
    
    # code below retrive data from MySQL DataBase 
    
    if choose_input == "Data from SQL database":
        st.write("*Your are selected data from SQL database*")
        input_id = st.text_input("*Enter channelID/videoId/commentId*")
        table_name = st.selectbox("Select table", ("AllTable","channeldata", "videotable", "commenttable"))
        Listcolumns = choose_columns(table_name)
        column_name = st.multiselect("Select columns", Listcolumns)
        output = st.button("*Search*")
        if output:    
            column_name_string = stringchanger(column_name)
            
            if table_name == "AllTable":
                querry = f"select {column_name_string} from channeldata join videotable on channeldata.playlist_id = videotable.PLAYLIST_ID join commenttable on videotable.VIDEO_ID = commenttable.video_id"
            else:
                pk = primary_key(table_name)    
                querry = f"select {column_name_string} from {table_name} where {pk} = '{input_id}';"

            connection = mysql_connector_connect()
            channel_data = select_sql(querry)
            if not channel_data:
                st.write("*Check id is valid or select correct table or data not database*")
            else:   
                df = pd.DataFrame(channel_data, columns = column_name)
                st.dataframe(df, width = 1240)

    
    # code below retrive data from youtube data API and visualize the data in table format
    
    if choose_input == "Data from youTube API":
        # search from streamlit
        input = st.text_input("*Enter channelID*")
        # search button
        button_1 = st.button("*Search and Save*")
        if button_1:
            api_service_name = "youtube"
            api_version = "v3"
            developer_key = "AIzaSyCMvfuUaY2rEZEHH5Tw59C7-p5iWjYmPsg"
            # bulid connection to youtube api
            youtubeApiConnection = apiconnection(api_service_name, api_version, developer_key)
            #channel details
            data = channelData(youtubeApiConnection, input)
            #channel details filter
            id,title,description,playlist_id,viewCount,subscriberCount,videoCount = channeldatafilter(data)
            df = pd.DataFrame(
                {"channel Details" : [id,title,description,playlist_id,viewCount,subscriberCount,videoCount]}, 
                index = ["id","title","description","playlist_id","viewCount","subscriberCount","videoCount"]
                )
            st.subheader("channel details")
            st.dataframe(df, width = 1240)
            #fetching videoid from playlist
            videoids = videoIdData(youtubeApiConnection, playlist_id)
            #video details
            list_of_data = videoIdDetails(youtubeApiConnection,videoids)
            df1 = pd.DataFrame(list_of_data)  
            df1.to_csv(path_or_buf=r"C:\Users\GIRI\Desktop\New folder\data.csv")
            st.subheader("video details")  
            st.dataframe(df1,width = 1240)
            # comment details
            list_of_comment = commentdata(youtubeApiConnection, videoids)
            df2 = pd.DataFrame(list_of_comment)
            st.subheader("comment details")
            st.dataframe(df2,width = 1240)
            
            #insert channel data to sql
            table_name = 'channeldata'
            # insert querry
            column_name = '(channelid,title,description,playlist_id,viewCount,subscriberCount,videoCount)'
            values = (id,title,description,playlist_id,viewCount,subscriberCount,videoCount)
            result = channel_sql(table_name,column_name,values)
            st.write(f'channel data {result}') 
            
            #insert video data to sql
            video_table_name = 'videotable'
            # insert querry
            video_column_name = '(VIDEO_ID,PLAYLIST_ID,VIDEO_NAME,VIDEO_DESCRIPTIOIN,PUBLISHED_DATE,TUMBNAIL,VIEW_COUNT,LIKE_COUNT,FAVORITE_COUNT,COMMENT_COUNT,DURATION)'
            videoFunOutput = video_data_inputer(list_of_data,video_table_name,video_column_name,playlist_id)
            st.write(f'video data {videoFunOutput}') 

            
            #insert comment data to sql
            comment_table_name = "commenttable"
            # insert querry
            comment_column_name = "(video_id, comment_id, comment_text, comment_author, comment_published_data)"
            Result1 = comment_sql(list_of_comment,comment_table_name,comment_column_name)
            st.write(f'comment data {Result1}') 

    



