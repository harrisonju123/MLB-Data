# MLB-Data
Calls the Fangraphs API to get pitcher data.
Batting data is in the works.

How to get started
1. Clone the repository using https
```
git clone https://github.com/harrisonju123/MLB-Data.git
```

2. To generate data, all you have to do is run main.py. 
  a. This can be done via IDE or in your terminal by typing:
  `python main.py` once you're inside the directory
  
  
  
Adding data to run daily

1. There's a pattern of `mm-dd-YYYY.json`
  This is found in `/pitchers`, `/teams`, and inside the main directory.
2. Inside `pitchers/mm-dd-YYYY.json`
  You want to use the same pattern as other json files.
  
  ``` { "players": ["name1", "name2", "name3"] } ```
  
  What this does is define the pitchers that will be playing on this date.
  
3. Also inside the same directory, we have `pitchers.json`
4. 
  This is to keep track of fangraphs pitcher ids that we use to query pitcher data.
  
  This can be found by going to fangraphs.com, search for the player name.
  
  You should be able to see the player_id in the url like this:![image](https://user-images.githubusercontent.com/102977991/187341527-2289f157-ddd8-4ade-883b-6033ea9def91.png)
  
  For all the players that were added in step 2, we should add them to `pitchers.json`. You may see some repeat names, that's a good thing we only have to do this for each player once.
  
4. Inside `teams/mm-dd-YYYY.json`:
5. 
  You want to use the same pattern again as others in the same directory.
  
  ``` { "team1": "team2", "team2": "team1 } ```
  
  What this does is it maps teams that will be playing against each other.

  
