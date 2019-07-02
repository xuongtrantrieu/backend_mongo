from settings import (
    app, load,
    DEV_ENVIRONMENT, PRD_ENVIRONMENT, CURRENT_ENVIRONMENT,
    CERT_FILE_PATH, KEY_FILE_PATH,
)

if __name__ == '__main__':
    load()

    if CURRENT_ENVIRONMENT == DEV_ENVIRONMENT:
        app.run(host='0.0.0.0', port='5000', ssl_context=(CERT_FILE_PATH, KEY_FILE_PATH))
    elif CURRENT_ENVIRONMENT == PRD_ENVIRONMENT:
        app.run()
    else:
        pass

