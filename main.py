from pyromod import Client
from plugins.secret_keys import PARDIS_SECRET_KEY

# BOT_TOKEN = PARDIS_SECRET_KEY
API_ID = 25659111
API_HASH = "2f4d5e01c109e278ac7d29e907647db1"

PULUGIN = dict(root="plugins")


app = Client(
    "app",
    API_ID,
    API_HASH,
    plugins=PULUGIN,  # check the plugins folder
    bot_token=PARDIS_SECRET_KEY,
)


if __name__ == "__main__": 
    app.run()
