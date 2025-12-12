import asyncio
from twikit import Client
from twikit.errors import TooManyRequests, NotFound
import json
import pandas as pd

USERNAME = 'X Username (@)'
EMAIL = 'Email for X account'
PASSWORD = 'Password for X account'


client = Client('en-us')

#Function to combine new collected data with saved data
def concatNewData(df, twtList, twt):
    tempDf = pd.DataFrame({
        'tweet_id': [twt.id],
        'username': [twt.user.name],
        'tweet_content': [twt.text],
        'tweet_label': [""]
    })

    df = pd.concat([df, tempDf], ignore_index=True)
    twtList.append(twt.id)

    return df

async def main():
    #Login to X
    await client.login(
        auth_info_1=USERNAME, 
        auth_info_2=EMAIL, 
        password=PASSWORD, 
        cookies_file='cookies2.json'
    )

    print("Logged in!!")

    try:
        #File will be saved in CSV and JSON
        #CSV to store the whole file
        #JSON to store the ids of retrieved tweets (to reduce duplicated datas)
        df = pd.read_csv("tweets.csv")
        with open ('twtList.json', 'r') as file:
            twtList = json.load(file)
    except FileNotFoundError:
        twtList = []
        df = pd.DataFrame({
            'tweet_id' : [], 
            'username' : [],
            'tweet_content' : [], 
            'tweet_label' : []
        })

    print(twtList, df)
    
    #Used keyword: 'mbg' and 'makan bergizi gratis' with post types as 'latest' and 'top'
    twts = await client.search_tweet('mbg', 'Latest')
    for twt in twts:
        if twt.id not in twtList:
            df = concatNewData(df, twtList, twt)
    while (len(twtList) < 1500):
        try:
            moreTwt = await twts.next()

            for twt in moreTwt:
                if twt.id not in twtList:
                    df = concatNewData(df, twtList, twt)

        except TooManyRequests as e:
            break

        except NotFound as e:
            continue
    
    #When API overloads or number of data exceeded required amount, data would be saved to both JSON and CSV. 
    df.to_csv('tweets.csv', index=False) 
    with open('twtList.json', 'w') as file:
        json.dump(twtList, file)

    print("CSV and JSON saved.")
    

if __name__ == "__main__":
    asyncio.run(main())