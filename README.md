# LeagueOfLegentAnalyticsPlatformWithKubernetes

## Background
- This project is the final project of Data center scale computing (CSCI 5253)
- The team members are
    - Jooseok Lee
    - Seungwook Lee
    - Chanheum Park
- Main compenents used in this project
    - Kubernetes: Container
    - Flask RESTful API, Riot API
    - MySQL: Player info Database
    - Kafka: Messaging queue
    - Cassandra: Caching
    - Redis: Logging
    - MinIO: Back-up storage

## Introduction
- We aim to build an extension to the platform OP.GG is a platform that allows League of Legends users to view their in-game statistics and view others. 
- On top of its functionality, we build an additional module that recommends other players with similar statistics holding a higher win rate than the requested user. 
- This information will allow the user to learn from similar play-style users with a higher win ratio leading the user to gradually increase their tier. 
- We will be providing a web service where users will input their user ID and Region information. 
- User queries will be stored in databases which we utilize to further enhance the performance of our system.
    - Create an analytic web-service when users input their user ID and Region it recommends other players with similar in-game statistics holding a higher win rate than the requested user.
    - Achieve multi-region support capable of handling multiple requests with scalability along with safety measures.

<div style="text-align: center;">
  <img src="img/system architecture.jpg" alt="System architecture" width="500">
</div>

## Architecture
- Users interact with our REST API web server where the user inputs their
ID/Region information that will be queued into our Kafka database. 
- Depending on the user’s Region(KOR: Korea / NA: North America), the data will be sent to the corresponding workers where KOR-workers handle the request of users in the Korea server and NA-workers handle the request
from the NA users. 
- Workers then retrieve data from the Riot Games API such as gold per minute, damage per minute, death, assist, and the number of kills.

### Interaction between Components
- Ingress is set up against the Flask REST service.
- Users interact with the Flask web server by providing
their Region/ID information.
- We created a work queue with Kafka to handle requests
by region allowing our service to be more efficient and able to scale.
-  Here, we have two workers corresponding to each region (Korea and North America). 
- Before queuing the work into Kafka Rest server checks whether the result of the request is cached in Cassandra first. 
- If there is a cache, the rest server returns the result to the users.
- Workers then request the player’s data from Riot Games API and store the retrieved data in MySQL.
- Using this data, our workers output a similarity by calculating
the Euclidian distance upon features such as DPS, gold per minute, KDA, etc.
- The similarity output is cached in Cassandra 3 to account for the same request made on the same day. 
- Similarity results vary by time as more user data is stored
in our MySQL database. 
- when the same request is made on the same date, it retrieves information from our cached data in Cassandra and is sent to the requesting
user. 
- Otherwise, the request is queued and runs the cycle. 
