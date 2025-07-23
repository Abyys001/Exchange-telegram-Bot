from pyromod import Client

BOT_TOKEN = "7161796991:AAFJVKfjeHu3PG5rZjHXTnA0lEzieQQLFoI"
API_ID = 25659111
API_HASH = "2f4d5e01c109e278ac7d29e907647db1"

PULUGIN = dict(root="plugins")


app = Client(
    "app",
    API_ID,
    API_HASH,
    plugins=PULUGIN,  # check the plugins folder
    bot_token=BOT_TOKEN,
)


if __name__ == "__main__": 
    app.run()
