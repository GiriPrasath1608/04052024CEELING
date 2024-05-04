import streamlit as st

if __name__ == "__main__":
    st.set_page_config(layout = "wide")
    
    st.title("YouTube Data Harvesting and Warehousing using SQL and Streamlit")
    st.header("Domain - Social Media")
    tab1, tab2 = st.tabs(["About Prject", "How to Use"])
    with tab1:
        st.write("*This project aims to develop a user-friendly Streamlit application that utilizes the Google API to extract information on a YouTube channel, stores it in a SQL database, and enables users to search for channel details and join tables to view data in the Streamlit app.*")
    with tab2:
        st.subheader("Q&A page")
        st.image("Q&A image.PNG", width = 800)
        st.text("""
                step 1 : Select Q&A page
                step 2 : Click arrow symbol in select box
                step 3 : Slect one question
                step 4 : Press Submit botton
                output : Outut will be a DataFrame  
                """)
        st.subheader("Search page")
        st.image("search 1 image.PNG", width = 800)
        st.text("""
                step 1 : Select Search page
                step 2 : Click arrow symbol in select box
                step 3 : Slect one method
                """)
        st.subheader("Data from SQL DataBase")
        st.image("search 2 image.PNG", width = 800)
        st.text("""
                step 1 : Enter Channel ID/Video ID/Comment ID 
                step 2 : In select table box click arrow symbol
                step 3 : Select table name
                step 4 : In Select column box click arrow symbol
                step 5 : Select which column do you want
                step 6 : Press Search button
                output : Outut will be a DataFrame   
                """)
        st.subheader("Data from Youtube API")
        st.image("search 3 image.PNG", width = 800)
        st.text("""
                step 1 : Enter channel ID 
                step 2 : Press Search and Save button
                output : Output will be a DataFrame of channel details, video details and comment details
                """)
        
        