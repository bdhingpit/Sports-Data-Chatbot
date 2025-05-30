import requests
from dotenv import load_dotenv
from pyprojroot import here
import os
import pandas as pd
from langchain_community.utilities import SQLDatabase
from langchain_community.agent_toolkits import SQLDatabaseToolkit
from sqlalchemy import create_engine
import warnings
from langchain_openai import ChatOpenAI
import langchain
from langchain import hub
from langgraph.prebuilt import create_react_agent

langchain.debug = True
warnings.filterwarnings('ignore')


PROJECT_ROOT = here()
print(PROJECT_ROOT)


# ----- Load environment variables
load_dotenv()
SPORTSDATA_API_KEY = os.getenv('SPORTSDATA_API_KEY')
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
print(SPORTSDATA_API_KEY)
print(OPENAI_API_KEY)


# ----- Create engine for SQL database
db_path = str(PROJECT_ROOT / 'data/sportsdata/nba/sql_nba.db')
db_path = f'sqlite:///{db_path}'
engine = create_engine(db_path)


# ----- Get team season stats data from sportsdata.io and save
team_stats_endpt = f'https://api.sportsdata.io/v3/nba/scores/json/TeamSeasonStats/2024?key={SPORTSDATA_API_KEY}'
response = requests.get(team_stats_endpt)
team_season_stats_lst = response.json()

team_season_stats_dct_lst = [
    {k: v for k, v in ts.items() if k != 'OpponentStat'} for ts in team_season_stats_lst
]  # Remove OpponentStat
team_season_stats_df = pd.DataFrame(team_season_stats_dct_lst)
team_season_stats_df = team_season_stats_df.dropna(axis=1, how='all')  # Remove columns with all NaN values
team_season_stats_df = team_season_stats_df.rename(columns={'Name': 'FullTeamName', 'Team': 'AbbreviatedTeamName'})
team_season_stats_df.head()
team_season_stats_df.to_csv(os.path.join(PROJECT_ROOT, 'data/sportsdata/nba/team_stats.csv'), index=False)
team_season_stats_df.to_sql('team_stats', con=engine, if_exists='replace', index=False)


# ----- Get player game log data
# For trial only, let's focus on  G. Antetokounmpo
player_id = 20000497
season = 2024
player_logs_endpt = (
    f'https://api.sportsdata.io/v3/nba/stats/json/PlayerGameStatsBySeason/{season}/{player_id}/all?key={SPORTSDATA_API_KEY}'
)
response = requests.get(player_logs_endpt)
player_game_logs_lst = response.json()

player_game_logs_df = pd.DataFrame(player_game_logs_lst)
player_game_logs_df = player_game_logs_df.dropna(axis=1, how='all')
player_game_logs_df = player_game_logs_df.rename(
    columns={'Name': 'PlayerName', 'Games': 'DidPlayerPlay', 'Team': 'AbbreviatedTeamName'}
)
player_game_logs_df.head()
player_game_logs_df.to_csv(os.path.join(PROJECT_ROOT, 'data/sportsdata/nba/player_game_log.csv'))
player_game_logs_df.to_sql('player_game_logs', con=engine, if_exists='replace', index=False)


# ----- Get team game log data
# Again, for trial, let's get Bucks only
team_id = 15
season = 2024
team_game_logs_endpt = (
    f'https://api.sportsdata.io/v3/nba/scores/json/TeamGameStatsBySeason/{season}/{team_id}/all?key={SPORTSDATA_API_KEY}'
)
response = requests.get(team_game_logs_endpt)
team_game_logs_lst = response.json()

team_game_logs_df = pd.DataFrame(team_game_logs_lst)
team_game_logs_df = team_game_logs_df.dropna(axis=1, how='all')
team_game_logs_df = team_game_logs_df.rename(columns={'Name': 'FullTeamName', 'Team': 'AbbreviatedTeamName'})
team_game_logs_df.head()
team_game_logs_df.to_csv(os.path.join(PROJECT_ROOT, 'data/sportsdata/nba/team_game_logs.csv'))
team_game_logs_df.to_sql('team_game_logs', con=engine, if_exists='replace', index=False)


# ----- Load SQL database
db = SQLDatabase.from_uri(db_path)

print(db.dialect)
print(db.get_usable_table_names())
print(db.get_table_info(['team_stats']))


# ----- Try querying database
db.run('SELECT AbbreviatedTeamName, Wins, Losses FROM team_stats WHERE Wins > 45;')
db.run(
    'SELECT "AbbreviatedTeamName", "Wins", "Losses" FROM team_stats WHERE "Name" IN ("Dallas Mavericks", "Cleveland Cavaliers") AND "SeasonType" = 1;'
)
db.run('SELECT pg.GameID FROM player_game_logs pg WHERE pg.Name = "Giannis Antetokounmpo" AND pg.DidPlayerPlay = 0')

db.run(
    'SELECT SUM(tg.Wins) AS TotalWins, SUM(tg.Losses) AS TotalLosses FROM team_game_logs tg WHERE tg.FullTeamName = "Milwaukee Bucks" AND tg.IsGameOver = 1 AND tg.GameID IN (SELECT pg.GameID FROM player_game_logs pg WHERE pg.PlayerName = "Giannis Antetokounmpo" AND pg.DidPlayerPlay = 0)'
)


# ----- Initialize LLM
llm = ChatOpenAI(model='gpt-4o-mini', temperature=0, timeout=None, max_retries=2)


# ----- Make a prompt that guides agent on what tables to include
prompt_template = hub.pull('langchain-ai/sql-agent-system-prompt')
assert len(prompt_template.messages) == 1

system_message = prompt_template.format(dialect='SQLite', top_k=5)

print(system_message)
print(prompt_template)


# -----Initialize agent
toolkit = SQLDatabaseToolkit(db=db, llm=llm)
tools = toolkit.get_tools()

agent_executor = create_react_agent(llm, tools, prompt=system_message)

# ----- Trial invoke the agent
question = 'Who had a better regular season? Dallas or Cleveland? Show me their team records.'
question = 'how many wins won above 40 games last 2024 season?'
question = 'What is Bucks record in games where Giannis did not play?'
question = 'What is Bucks record when Giannis scores less than 30 points?'
question = 'Who had the best record in NBA regular season 2024?'

# response = agent_executor.invoke({'messages': [{'role': 'user', 'content': question}]}, stream_mode='values')

for step in agent_executor.stream(
    {'messages': [{'role': 'user', 'content': question}]},
    stream_mode='values',
):
    step['messages'][-1].pretty_print()

type(step['messages'][-1])
step['messages'][-1].content
