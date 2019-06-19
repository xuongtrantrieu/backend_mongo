import settings

if __name__ == '__main__':
    settings.load()

    settings.app.run(host='0.0.0.0', port='8000')

