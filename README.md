# Sports Data Chatbot
A proof-of-concept feature that implements a text-to-query chatbot that is powered by ChatGPT LLM. Briefly, a chatbot interface is available to a front-end user. Questions submitted through the interface is passed to the LLM agent. The LLM agent queries the question to ChatGPT using a pre-specified prompt, and ChatGPT returns an appropriate SQL query. This query is then used to retrieve the necessary data in the SQL database. Finally, the data provided to the user in a chat format.

**Note 1:**
Data was retrieved from sportsdata.io. On free tier, they only provide "mock" data. That is, they don't reflect actual NBA statistical data.