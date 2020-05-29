from configparser import ConfigParser

# https://www.youtube.com/watch?v=HH9L9WFMfnE&t=155s&ab_channel=kishstats
config = ConfigParser()

config['Heartbeat'] = {
    'KeepALive': 'True',
    'Time': 3
}

config['Maximum'] = {
    'MaximumPackages': 25,
    'Start': 'false'
}

with open('./conf.ini', 'w') as f:
    config.write(f)
