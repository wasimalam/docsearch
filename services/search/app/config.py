import configparser
from app.model import Config, DBSettings, ElasticSearchSettings, GeneralSettings, StorageSettings
 
 # Create a ConfigParser object
def read_config():
    config = configparser.ConfigParser()
    # Read the configuration file
    config.read('config.ini')
    # Access values from the configuration file
 
    # Return a dictionary with the retrieved values

    dbSettings = DBSettings(dbname=config.get('Database', 'db_name'),
        host = config.get('Database', 'db_host'),
        port = config.get('Database', 'db_port'),
        user = config.get('Database', 'db_user'),
        password =  config.get('Database', 'db_password'))
    
    elasticsearch = ElasticSearchSettings(server = config.get('ElasticSearch', 'server'),
        port=config.get('ElasticSearch', 'port'),
        document_index=config.get('ElasticSearch', 'document_index'))

    storage = StorageSettings( folder = config.get('FileStorage', 'folder'))
    general = GeneralSettings(loglevel = config.get('General', 'log_level'))
    configsettings = Config(db = dbSettings, es = elasticsearch, storage=storage, general = general )
    return configsettings

"""

    config_values = {
        'debug_mode':  config.getboolean('General', 'debug'),
        'log_level': config.get('General', 'log_level'),
        'log_folder': config.get('General', 'log_folder'),
        'database' : {
            'db_name': config.get('Database', 'db_name'),
            'db_host': config.get('Database', 'db_host'),
            'db_port': config.get('Database', 'db_port'),
            'db_user': config.get('Database', 'db_user'),
            'db_password': config.get('Database', 'db_password'),
        },
        'elasticsearch' : {
            'server':config.get('ElasticSearch', 'server'),
            'port':config.get('ElasticSearch', 'port'),
            'document_index':config.get('ElasticSearch', 'document_index'),
        },
        'filestorage': { 
            'folder':config.get('FileStorage', 'folder'),
        }
    }
"""
 