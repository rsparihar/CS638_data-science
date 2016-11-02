import pandas as pd
import unicodecsv

path_A="TableA.csv"
path_B="TableB.csv"
path_B_mod = "TableB_mod.csv"

df = pd.read_csv(path_B)
runtime_column = df.Runtime
totalMinutesColumn = []

#firstFlag = 0

for i in runtime_column:
    #if(firstFlag == 0):
        #print("yoyo" + str(type(i)))
    if("-" in str(i)):
        i="0" + " minutes"
    elif( " " in str(i) ):
        hourMinutePair = str(i).split(" ")
        hour = int(hourMinutePair[0].replace("h",""))
        minute = int(hourMinutePair[1].replace("m", ""))
        totalMinutes = hour*60 + minute
        # print(str(totalMinutes) + " minutes")
        i = str(totalMinutes) + " minutes"
        #if (firstFlag == 0):
           # print(type(i))
           # firstFlag =1

    totalMinutesColumn.append(i)

df.Runtime = totalMinutesColumn
df.to_csv(path_B_mod,index=False,encoding="utf-8")