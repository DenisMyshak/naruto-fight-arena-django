from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
import mysql.connector
import re

def create_database_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="password",
        database="narutodb"
    )

def search_characters_with_name(character_name, cursor):
    sql = "SELECT * FROM characters WHERE character_name = %s"
    cursor.execute(sql, (character_name,))
    return cursor.fetchall()

def update_character_image(character_name, image_link, cursor):
    if search_characters_with_name(character_name, cursor):
        sql = "UPDATE characters SET battle_image = %s WHERE character_name = %s"
        cursor.execute(sql, (image_link, character_name))

def scrap_image_and_move_to_db(soup, character_name, cursor):
    try:
        img_container = soup.find("div", class_="imgContainer")
        image_link = "https://jut.su" + img_container.find("a")["href"]
        update_character_image(character_name, image_link, cursor)
    except Exception as e:
        return e

def create_characters_link_list():
    url = "https://jut.su/ninja"
    
    try:
        driver.get(url)
        driver.implicitly_wait(3)
        page_source = driver.page_source
    finally:
        driver.quit()

    soup = BeautifulSoup(page_source, "html.parser")
    ninja_list_ul = soup.find('ul', class_='ninja_list')

    character_links = [li.find('a')['href'] for li in ninja_list_ul.find_all('li', recursive=False) if li.find('a')]
    href_pat = r"^\/ninja\/.*$"
    valid_character_links = [url + link for link in character_links if re.match(href_pat, link)]

    return valid_character_links

def browse_jutsu_and_charac_image(seed_url, page_number=1):
    try:
        driver.get(seed_url.format(page_number) if page_number > 1 else seed_url)
        page_source = driver.page_source
        soup = BeautifulSoup(page_source, "html.parser")

        if page_number == 1:
            scrap_image_and_move_to_db(soup, extract_character_name(seed_url), cursor)

        next_button = soup.find("div", id="navigation").find('a', text="Далее")
        if next_button:
            seed_url += "page/{}/"
            page_number += 1
            browse_jutsu_and_charac_image(seed_url, page_number)
    except Exception as e:
        return e
    finally:
        driver.quit()

def extract_character_name(seed_url):
    pattern = r'/ninja/(\w+)/'
    match = re.search(pattern, seed_url)
    return match.group(1).replace("_", " ") if match else None

def main():
    global driver, cursor

    chrome_options = Options()
    chrome_options.add_argument("--headless")
    driver = webdriver.Chrome(options=chrome_options)

    mydb = create_database_connection()
    cursor = mydb.cursor()

    try:
        character_links = create_characters_link_list()
        for link in character_links:
            browse_jutsu_and_charac_image(link)
    finally:
        cursor.close()
        mydb.close()
        driver.quit()

if __name__ == "__main__":
    main()