from dotenv import load_dotenv
import yaml
from pyprojroot import here
from langchain_openai import ChatOpenAI


print("Environment variables are loaded:", load_dotenv())


class LoadConfig:
    def __init__(self) -> None:
        with open(here('configs/app_config.yml')) as cfg:
            app_config = yaml.load(cfg, Loader=yaml.FullLoader)

        self.load_directories(app_config=app_config)
        self.load_llm_configs(app_config=app_config)
        self.load_openai_models()

    def load_directories(self, app_config):
        self.sqldb_directory = str(here(app_config['directories']['sqldb_directory']))

    def load_llm_configs(self, app_config):
        self.model_name = app_config['llm_config']['engine']
        self.agent_llm_system_role = app_config['llm_config']['agent_llm_system_role']
        self.temperature = app_config['llm_config']['temperature']

    def load_openai_models(self):
        self.langchain_llm = ChatOpenAI(model=self.model_name, temperature=self.temperature, timeout=None, max_retries=2)
