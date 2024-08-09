import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver import ActionChains
from selenium.webdriver.common.actions.wheel_input import ScrollOrigin
from urllib.parse import urlparse


def get_categories_urls():
    driver = webdriver.Chrome()
    driver.get("https://snappshop.ir")
    time.sleep(5)

    urls_divs = driver.find_elements(By.XPATH, "//div[@class='d-flex flex-column AllCategories_all-categories__left-side-wrapper__6Bkxf']")

    file = open('00-mega-urls/mega-urls.txt', 'w+')
    for url_div in urls_divs:
        urls_elements = url_div.find_elements(By.TAG_NAME, "a")
        print(len(urls_elements))
        for url in urls_elements:
            file.write(url.get_attribute('href') + ',\n')

        file.write("#################  End Category Section  #################,\n")

    file.close()

    time.sleep(5)
    driver.quit()


def get_category_from_url(url):
    parse_url = urlparse(url)
    split_url_path = parse_url.path.split('/')[2]
    return split_url_path


def add_to_done_url_list(done_url, dir_path, dir_path_strip):
    with open(dir_path + "/" + dir_path_strip + "-done.txt", "a") as f:
        f.write(done_url + ",\n")
        f.close()


def add_to_product_url_list(products_cards, dir_path, category):
    sub_url = dir_path + "/" + category + ".txt"
    with open(sub_url, 'a') as f:
        for product in products_cards:
            f.write(product.get_attribute("href") + ",\n")
        f.close()


def get_sub_categories_urls():
    dir_list = open('./dir-list-for-processing.txt', 'r')

    for dir_path in dir_list:
        dir_path_strip = dir_path.strip("\n")
        dir_path = './' + dir_path_strip
        dir_list_file_path = dir_path + '/' + dir_path_strip + '.txt'
        categories_urls = open(dir_list_file_path, 'r')

        for category_url in categories_urls:
            clear_category_url = category_url.strip("\n").strip(" ").strip(",")
            print(f"Crawl Page is Starting: {clear_category_url}")
            driver = webdriver.Chrome()
            driver.get(clear_category_url)
            time.sleep(10)

            all_products_div = driver.find_element(By.XPATH, "//div[@class='PLPSection_plp-products-container__HSjLH pt-l pb-s']")

            scroll_origin = ScrollOrigin.from_viewport(10, 10)
            for i in range(60):
                ActionChains(driver).scroll_from_origin(scroll_origin, 0, 360).perform()
                time.sleep(3)

            all_products_card = all_products_div.find_elements(By.TAG_NAME, "a")

            category = get_category_from_url(clear_category_url)

            add_to_product_url_list(all_products_card, dir_path, category)

            add_to_done_url_list(clear_category_url, dir_path, dir_path_strip)

            time.sleep(10)
            driver.quit()

        categories_urls.close()


def create_categories_list():
    dir_path = "./" + "04-fashion"
    urls_file_name = "04-fashion.txt"

    categories_list_filename = "04-fashion-categories.txt"

    with open(dir_path + "/" + categories_list_filename, "a") as cat_list_file:

        with open(dir_path + "/" + urls_file_name, "r") as f:
            for url in f:
                category = get_category_from_url(url.strip("\n").strip(","))
                cat_list_file.write(category + ",\n")

            f.close()
        cat_list_file.close()

