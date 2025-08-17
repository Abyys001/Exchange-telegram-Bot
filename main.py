from pyromod import Client
from plugins.secret_keys import PARDIS_SECRET_KEY

# BOT_TOKEN = PARDIS_SECRET_KEY

PLUGIN = dict(root="plugins")


app = Client(
    "app",
    API_ID, # your api and hash XD
    API_HASH,
    plugins=PLUGIN,  # check the plugins folder
    bot_token=PARDIS_SECRET_KEY,
)


if __name__ == "__main__": 
    app.run()
