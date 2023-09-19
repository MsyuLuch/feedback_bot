import logging, datetime

API_TOKEN = '*********************' # bot token
admin = [*********************] # id админа
DEFAULT_RATE_LIMIT = 0.5 # seconds RATE_LIMIT - throttling rate limit (anti-spam)

formatter = '[%(asctime)s] %(levelname)8s --- %(message)s (%(filename)s:%(lineno)s)'		
logging.basicConfig(	
    filename=f'bot-from-{datetime.datetime.now().date()}.log',
    #filemode='w',
    format=formatter,
    datefmt='%Y-%m-%d %H:%M:%S',
    level=logging.INFO
)