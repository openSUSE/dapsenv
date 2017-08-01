import logging
DEFAULT_LOGGING_DICT = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'standard': {'format': '[%(levelname)s] %(name)s: %(message)s'},
        'tf': {'format': '[%(levelname)s] %(module)s: %(message)s'},
    },
    'handlers': {
        'default': {
            'level': logging.DEBUG,
            'formatter': 'standard',
            'class': 'logging.StreamHandler',
        },
        'th': {
            'level': logging.DEBUG,
            'formatter': 'tf',
            'class': 'logging.StreamHandler',
        },
    },
    'loggers': {
        'test': {
            'handlers': ['th'],
            'level': logging.DEBUG,
            'propagate': True
        },
        'job': {
            'handlers': ['th'],
            'level': logging.DEBUG,
            'propagate': True
        },
    }
}

#: Map verbosity level (int) to log level
LOGLEVELS = {None: logging.WARNING,  # 0
             0: logging.WARNING,
             1: logging.INFO,
             2: logging.DEBUG,
             }
