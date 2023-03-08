import pandas as pd

data = pd.read_csv("UserFollowers.csv")
users = data[["UserId"]].copy().sort_values(by="UserId").drop_duplicates(subset=['UserId']).reset_index().drop(columns=["index"]).loc[:1000]

follow_temp = []

for value in data.values:
    if value[1] in users.values:
        follow_temp.append({"UserID": value[1], "FollowUserId": value[2]})

follow = pd.DataFrame(follow_temp, columns=["UserID", "FollowUserId"])
print(follow)