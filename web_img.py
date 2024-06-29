from helper import WEB_URL_IBK


def download_cur_img():
    return None
    failure = False
    from selenium.webdriver import Firefox, FirefoxOptions, FirefoxProfile
    from selenium.webdriver.firefox.service import Service as FirefoxService
    from webdriver_manager.firefox import GeckoDriverManager

    options = FirefoxOptions()
    options.add_argument("--headless")
    # options.binary = r'C:\Program Files\Mozilla Firefox\firefox.exe'  # on Windows

    profile = FirefoxProfile()  # '/root/.mozilla/firefox/abcdefgh.default')

    driver = Firefox(
        service=FirefoxService(GeckoDriverManager().install()),
        options=options)

    print(WEB_URL_IBK)
    driver.get(WEB_URL_IBK)
    print("Headless Firefox Initialized")
    driver.quit()

    return not failure


def get_current_image():
    if download_cur_img():
        return open('./cur_img/cur.jpg', 'br')
    else:
        return None
