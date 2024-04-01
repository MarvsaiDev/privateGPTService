import os

import openai
import yaml

class EnvironmentConfig:
    def __init__(self, config_file="settings.yaml"):
        self.config_file = config_file
        self.config = None
        self.load_config()

    def load_str_stream(self,string:str):
        try:
            config = yaml.safe_load(string)
            self.config.update(config)
            for key, value in config.items():
                os.environ[key] = str(value)
            return config
        except Exception as e:
            print(f"Error: {self.config_file} not found. Using default environment variables.")
            return None

    def load_config(self):
        try:
            with open(self.config_file, "r") as yaml_file:
                config = yaml.safe_load(yaml_file)
                self.config = config
                for key, value in config.items():
                    os.environ[key] = str(value)
        except FileNotFoundError:
            print(f"Error: {self.config_file} not found. Using default environment variables.")

    def reset_config(self):
        # Reset all environment variables to their default values
        os.environ.clear()

if __name__=='__main__':
    # Example usage
    env_config = EnvironmentConfig('../settings.yaml')


    # Set global variables based on the environment configuration
    openai.api_base = env_config.config.get("OPENAI_API_BASE")
    openai.api_version = env_config.config.get("OPENAI_API_VERSION")
    openai.api_key = env_config.config.get("OPENAI_API_KEY")
    embeddings_model_name = env_config.config.get("EMBEDDINGS_MODEL_NAME")
    persist_directory = env_config.config.get("PERSIST_DIRECTORY")
    model_type = env_config.config.get("MODEL_TYPE")
    model_subtype = env_config.config.get("MODEL_SUBTYPE", "gpt-35-16k")
    model_path = env_config.config.get("MODEL_PATH")
    model_n_ctx = env_config.config.get("MODEL_N_CTX")
    model_n_batch = int(env_config.config.get("MODEL_N_BATCH", 8))
    target_source_chunks = int(env_config.config.get("TARGET_SOURCE_CHUNKS", 4))
    qa_system = None

    print(f"API Base: {os.environ.get('OPENAI_API_BASE')}")
    print(f"API Version: {os.environ.get('OPENAI_API_VERSION')}")
    print(f"API Key: {os.environ.get('OPENAI_API_KEY')}")
    print(f"Embeddings Model Name: {os.environ.get('EMBEDDINGS_MODEL_NAME')}")
    print(f"Persist Directory: {os.environ.get('PERSIST_DIRECTORY')}")
    print(f"Model Type: {os.environ.get('MODEL_TYPE')}")
    print(f"Model Subtype: {os.environ.get('MODEL_SUBTYPE')}")
    print(f"Model Path: {os.environ.get('MODEL_PATH')}")
    print(f"Model N Context: {os.environ.get('MODEL_N_CTX')}")
    print(f"Model N Batch: {os.environ.get('MODEL_N_BATCH')}")
    print(f"Target Source Chunks: {os.environ.get('TARGET_SOURCE_CHUNKS')}")
    print(f"QA System: {os.environ.get('QA_SYSTEM')}")
