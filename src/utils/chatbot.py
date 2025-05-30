import os
from typing import List, Tuple
from utils.load_chatbot_config import LoadConfig
from langchain_community.utilities import SQLDatabase
from langchain.chains import create_sql_query_chain
from langchain_community.agent_toolkits import SQLDatabaseToolkit
from langchain_community.agent_toolkits import create_sql_agent
from sqlalchemy import create_engine
import langchain
from langchain import hub
from langgraph.prebuilt import create_react_agent

langchain.debug = True


APPCFG = LoadConfig()


class ChatBot:
    @staticmethod
    def respond(chatbot: List, message: str, app_functionality: str) -> Tuple:
        if app_functionality == 'Chat':
            if os.path.exists(APPCFG.sqldb_directory):
                db = SQLDatabase.from_uri(f'sqlite:///{APPCFG.sqldb_directory}')

                prompt_template = hub.pull('langchain-ai/sql-agent-system-prompt')
                system_message = prompt_template.format(dialect='SQLite', top_k=5)
                #  prompt = PromptTemplate(input_variables=['question'])

                toolkit = SQLDatabaseToolkit(db=db, llm=APPCFG.langchain_llm)
                tools = toolkit.get_tools()

                agent_executor = create_react_agent(APPCFG.langchain_llm, tools, prompt=system_message)

                response = agent_executor.invoke({'messages': [{'role': 'user', 'content': message}]})
                response_fin = response['messages'][-1].content

                chatbot.append((message, response_fin))

                return '', chatbot
            else:
                chatbot.append((message, 'SQL DB does not exist. Please create the database first'))

                return '', chatbot

        return '', chatbot
