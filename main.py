import os
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from urllib.parse import urlparse
from urllib.request import urlretrieve
from selenium.common.exceptions import NoSuchElementException


def create_dir_csv(category_dir, subcategory_dir):
    if os.path.isdir(category_dir) is not True:
        print('Creating category directory...')
        os.mkdir(category_dir)

    if os.path.isdir(subcategory_dir) is not True:
        print('Creating subcategory directory...')
        os.mkdir(subcategory_dir)

    return True


def create_done_list_file(done_file_path):
    if os.path.isfile(done_file_path) is not True:
        print('Creating List of Done URLs file...')
        with open(done_file_path, 'a') as done_file:
            pass
        done_file.close()
    return True


def get_product_id(url):
    url_parse = urlparse(url)
    product_path = url_parse.path
    pro_path_split = product_path.split('/')
    pro_id_str = pro_path_split[2].strip("snp-")
    return pro_id_str


def get_product_price(driver):
    try:
        price_element = driver.find_element(By.XPATH, "//span[@class='h5 text-bold']")
        price = price_element.text.strip()
    except NoSuchElementException as e:
        price = 0.99

    return price


def get_main_feature(driver):
    try:
        main_feature_div = driver.find_element(By.XPATH, "//div[@class='d-flex text-gray-800 body-2']")
        main_feature_spans = main_feature_div.find_elements(By.TAG_NAME, "span")
    except NoSuchElementException:
        try:
            main_feature_div = driver.find_element(By.XPATH,
                                                   "//div[@class='d-flex justify-content-between text-gray-800 body-2']")
            main_feature_spans = main_feature_div.find_elements(By.TAG_NAME, "span")
        except NoSuchElementException:
            main_feature_spans = []

    main_feature_list = []
    if len(main_feature_spans):
        for span in main_feature_spans:
            main_feature_list.append(span.text.strip().strip(':'))

        return {main_feature_list[0]: main_feature_list[1]}

    return {}


def fix_image_url(url):
    parsed_url = urlparse(url)
    if parsed_url.netloc == "cdn.shop.snapp.ir":
        fix_url = parsed_url.scheme + "://cdn.snappshop.ir" + parsed_url.path
        return fix_url
    return url


def get_product_images(driver, save_path):
    images_divs_list = driver.find_elements(By.XPATH,
                                            "//div[@class='keen-slider__slide gallery_gallery__thumbnail-slide__gMe2B']")
    images_list = []
    for image_div in images_divs_list:
        image = image_div.find_element(By.TAG_NAME, "img")
        image_url = image.get_attribute("data-src")
        images_list.append(image_url)

    print("Downloading Product Images...")
    image_names_list = []
    error_count = 0
    for i in range(len(images_list)):
        print("Downloading  ", images_list[i])
        url_parse = urlparse(images_list[i])
        url_split = url_parse.path.split("/")
        clear_img_name = url_split[len(url_split) - 1]
        image_names_list.append(clear_img_name)
        img_url_fixed = fix_image_url(images_list[i])
        try:
            urlretrieve(img_url_fixed, save_path + "/" + clear_img_name)
        except Exception as e:
            error_count += 1

    return images_list, image_names_list, error_count


def get_product_name(driver):
    name_element = driver.find_element(By.XPATH,
                                       "//h1[@class='text-gray-900 body-1 text-bold text-iransans-en-digits']")
    name_text = name_element.text.strip()
    return name_text


def get_product_features(driver):
    keys = driver.find_elements(By.XPATH, "//ul[@class='pt-m']//span[@class='caption d-inline-block']")
    values = driver.find_elements(By.XPATH,
                                  "//ul[@class='pt-m']//span[@class='pr-xxs caption text-gray-800 text-bold']")

    feature_key = []
    feature_value = []
    for key in keys:
        key_text = key.text.strip()
        feature_key.append(key_text)
    for value in values:
        value_text = value.text.strip()
        feature_value.append(value_text)

    feature_dic = {}
    for i in range(len(feature_key)):
        feature_dic[feature_key[i]] = feature_value[i]

    return feature_dic


def check_if_url_processed(url, subcategory_url_done_list):
    with open(subcategory_url_done_list, "r") as sdl:
        is_exist = False
        for p_link in sdl:
            if url == p_link.strip(",\n"):
                is_exist = True
                break
    sdl.close()
    return is_exist


def add_url_to_done_list(url, subcategory_url_done_list):
    with open(subcategory_url_done_list, "a") as sdl:
        sdl.write(url + ",\n")

    sdl.close()
    return True


if __name__ == "__main__":
    driver = webdriver.Chrome()

    sub_category = "women-blouse-tonic"
    category = "fashion"
    sequence = "04"

    sub_cat_pro_ulist_path = f"./urls/{sequence}-{category}/{sub_category}.txt"
    cat_pro_url_done_list = f"./urls/{sequence}-{category}/{sub_category}-done.txt"
    create_done_list_file(cat_pro_url_done_list)

    current_dir = os.getcwd()
    category_dir = current_dir + '/dataset/' + sequence + '-' + category
    subcategory_dir = current_dir + '/dataset/' + sequence + '-' + category + '/' + sub_category

    create_dir_csv(category_dir, subcategory_dir)

    with open(sub_cat_pro_ulist_path, "r") as pro_u_list:
        with open(subcategory_dir + "/metadata.txt", "a", encoding="utf-8") as metadata_file:
            for link in pro_u_list:
                clear_link = link.strip(",\n")
                print("clear link ", clear_link)
                print("Checking clear link...")
                if check_if_url_processed(clear_link, cat_pro_url_done_list):
                    print("URL already processed...")
                    continue
                else:
                    print("Start crawling link...")
                    driver.get(clear_link)
                    time.sleep(6)

                    product_id = get_product_id(link)
                    print("product_id: ", product_id)
                    p_features = get_product_features(driver)
                    print("Features: ", p_features)
                    name = get_product_name(driver)
                    print("Name: ", name)
                    price = get_product_price(driver)
                    if price == 0.99:
                        add_url_to_done_list(clear_link, cat_pro_url_done_list)
                        print("Finished crawling.")
                        print("Product is Not Available.")
                        continue
                    print("Price: ", price)
                    img_url_list, img_name_list, errors = get_product_images(driver, subcategory_dir)
                    print("Images: ", img_name_list)
                    if len(img_url_list) == errors:
                        add_url_to_done_list(clear_link, cat_pro_url_done_list)
                        print("Finished crawling.")
                        print("Product's Images are Not Available.")
                        continue
                    main_feature = get_main_feature(driver)
                    print("Main feature: ", main_feature)

                    metadata_file.write(f"{product_id}@{name}@{price}@{main_feature}@{p_features}@{img_name_list}\n")
                    print("Adding product link to Done list...")
                    add_url_to_done_list(clear_link, cat_pro_url_done_list)
                    print("Finished crawling.")

        metadata_file.close()

    time.sleep(5)
    driver.quit()
