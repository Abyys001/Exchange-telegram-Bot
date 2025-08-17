from pyromod import Client

VR_BOT_FORTEST = "6861700509:AAFxrcsn7MZB1AxAS9m8SvArXMy6tpUAJjs" # vroadbot test api


DB_PASSWORD = "your-db-password-here"


PLUGIN = dict(root="plugins")
API_ID = 25659111
API_HASH = "2f4d5e01c109e278ac7d29e907647db1"

app = Client(
    "app",
    API_ID,
    API_HASH,
    plugins=PLUGIN,  # check the plugins folder
    bot_token=VR_BOT_FORTEST,
)

if __name__ == "__main__": 
    app.run()
