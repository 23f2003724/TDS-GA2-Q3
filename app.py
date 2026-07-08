import os
import yaml

from dotenv import load_dotenv

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi import Query

load_dotenv()

app = FastAPI()

# Allow CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

######################################################
# DEFAULT CONFIG
######################################################

config = {
    "port": 8000,
    "workers": 1,
    "debug": False,
    "log_level": "info",
    "api_key": "default-secret-000",
}

######################################################
# YAML
######################################################

with open("config.development.yaml") as f:
    yaml_config = yaml.safe_load(f)

config.update(yaml_config)

######################################################
# .ENV
######################################################

if os.getenv("APP_LOG_LEVEL"):
    config["log_level"] = os.getenv("APP_LOG_LEVEL")

if os.getenv("NUM_WORKERS"):
    config["workers"] = int(os.getenv("NUM_WORKERS"))

######################################################
# OS ENV (APP_*)
######################################################

mapping = {
    "APP_PORT": "port",
    "APP_WORKERS": "workers",
    "APP_DEBUG": "debug",
    "APP_LOG_LEVEL": "log_level",
    "APP_API_KEY": "api_key",
}

for env_name, key in mapping.items():
    if env_name in os.environ:

        value = os.environ[env_name]

        if key in ["port", "workers"]:
            value = int(value)

        elif key == "debug":
            value = value.lower() in ["true", "1", "yes", "on"]

        config[key] = value


######################################################
# ENDPOINT
######################################################

@app.get("/effective-config")
def effective_config(set: list[str] = Query(default=[])):

    final = config.copy()

    for item in set:

        if "=" not in item:
            continue

        key, value = item.split("=", 1)

        if key in ["port", "workers"]:
            value = int(value)

        elif key == "debug":
            value = value.lower() in ["true", "1", "yes", "on"]

        final[key] = value

    final["api_key"] = "****"

    return final