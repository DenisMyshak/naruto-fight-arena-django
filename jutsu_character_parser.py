# TODO:

# 1) solve problem with character_id:

    # When for the first time character is parsed, I set character_id.
    # For example for Naruto_Uzumaki/, but when I go to next page character_id
    # sets to None and for that reason jutsu doesnt match to character anymore

# 2) make parser asynchronous


# for accessing html page
from selenium.webdriver.chrome.options import Options
from selenium import webdriver

# for work with links
from urllib.parse import unquote
from fuzzywuzzy import fuzz
import re

# for parsing of html page
from bs4 import BeautifulSoup

# database stuff
import mysql.connector

import sys

def create_database_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="password",
        database="narutodb"
    )

# ----------------Db Functions----------------

def search_character_with_name(character_name):
    try:
        character_id = None
        sql = "SELECT * FROM characters WHERE character_name = %s"
        cursor.execute(sql, (character_name,))
        result = cursor.fetchall()

        if len(result):
            character_id = result[0][0]
        else:
            character_name_parts = character_name.split()

            for name_part in character_name_parts:
                sql = "SELECT * FROM characters WHERE character_name LIKE %s"
                cursor.execute(sql, ('%' + name_part + '%',))
                result = cursor.fetchall()
                if len(result) == 1:
                    character_id = result[0][0]

    except Exception as e:
        print("SEARCH::CHARACTER::BY::NAME::FAILED \n" + str(e))
        sys.exit()
    
    if not character_id: unmatched_characters.append(character_name)

    print("character id: " + str(character_id))

    return character_id


def search_jutsu_with_name(jutsu_name):
    try:
        sql = "SELECT * FROM jutsu WHERE jutsu_name = %s"
        cursor.execute(sql, (jutsu_name,))
        result = cursor.fetchall()

    except Exception as e:
        print("SEARCH::JUTSU::BY::NAME::FAILED \n" + str(e))
        sys.exit()

    return result[0][0] # jutsu id column


def update_character_battle_image(character_name, image_link):
    try:
        character_id = search_character_with_name(character_name)
        if character_id:
            sql = "UPDATE characters SET battle_image = %s WHERE character_name = %s"
            cursor.execute(sql, (image_link, character_name))
            mydb.commit()

    except Exception as e:
        print("UPDATE::CHARACTER::BATTLE::IMAGE::FAILED \n" + str(e))
        sys.exit()
    
    return character_id


def match_jutsu_to_character(character_id, jutsu_id):
    try:
        sql = "INSERT INTO characters_jutsu VALUES (%s, %s)"
        cursor.execute(sql, (character_id, jutsu_id))
        mydb.commit()

    except Exception as e:
        print("MATCH::JUTSU::TO::CHARAC::FAILED \n" + str(e))
        sys.exit()

def create_and_match_jutsu_in_db(character_name, character_id, jutsu_name, jutsu_image, jutsu_gif, jutsu_desc):
    try:
        sql = "INSERT INTO jutsu (jutsu_name, jutsu_image, jutsu_gif, jutsu_description) VALUES (%s, %s, %s, %s)"
        cursor.execute(sql, (jutsu_name, jutsu_image, jutsu_gif, jutsu_desc))
        mydb.commit()

        jutsu_id = search_jutsu_with_name(jutsu_name)

        if character_id:
            match_jutsu_to_character(character_id, jutsu_id)

    except Exception as e:
        print("CREATE::AND::MATCH::JUTSU::FAILED \n" + str(e))
        sys.exit()


# ----------------Link Lists Functions----------------
    
def create_characters_link_list():
    url = "https://jut.su/ninja"
    
    try:
        driver.get(url)
        driver.implicitly_wait(3)
        page_source = driver.page_source

        soup = BeautifulSoup(page_source, "html.parser")
        ninja_list_ul = soup.find('ul', class_='ninja_list')

        character_links = [ li.find('a')['href'] for li in ninja_list_ul.find_all('li', recursive=False) if li.find('a')]
        href_pat = r"^\/ninja\/.*$"
        valid_character_links = ['https://jut.su' + link for link in character_links if re.match(href_pat, link)]

    except Exception as e:
        print("CREATE::CHARAC::LINKS::FAILED \n" + str(e))
        sys.exit()

    return valid_character_links


def create_jutsu_link_list(soup):
    try:
        ninja_list_container = soup.find(id='dle-content')
        ninja_list_items = ninja_list_container.find_all('div', class_="technicBlock", recursive=False)

        jutsu_link_list = [item.find('a', class_="study")['href'] for item in ninja_list_items if item.find('a', class_="study")]

    except Exception as e:
        print("CREATE::JUTSU::LINKS::FAILED \n" + str(e))
        sys.exit()

    return jutsu_link_list


# ----------------Scrape Functions----------------

def scrap_jutsu_details_and_move_to_db(main_jutsu_page_soup, character_name, character_id):

    jutsu_link_list = create_jutsu_link_list(main_jutsu_page_soup)

    try:
        for jutsu_link in jutsu_link_list:

            driver.get(jutsu_link)
            page_source = driver.page_source
            jutsu_details_soup = BeautifulSoup(page_source, "html.parser")

            # parsing image
            image_origname_container = jutsu_details_soup.find('div', class_="leftfromvkvideo")
            jutsu_image = image_origname_container.find("a", class_="a_dash_b_img")["href"]

            # parsing name
            original_name = image_origname_container.find("div", string="Оригинальное название:")
            if original_name:
                original_name = original_name.find_next_sibling("div").text
            else:
                rus_name = jutsu_details_soup.find("div", class_="sector_border").find("h1").text
            
            jutsu_name = original_name if original_name else rus_name

            # parsing gif 
            jutsu_gif_container = jutsu_details_soup.find(id="show_gif_anim")
            jutsu_gif = jutsu_gif_container.find("noindex").find("a")["href"] if jutsu_gif_container else ""

            # parsing description
            jutsu_desc = jutsu_details_soup.find("div", class_="underthevkvideo").text

            create_and_match_jutsu_in_db(character_name, character_id, jutsu_name, jutsu_image, jutsu_gif, jutsu_desc)

    except Exception as e:
        print("SCRAPE::JUTSU::DETAILS::FAILED \n" + str(e))
        sys.exit()

    return True


def scrap_image_and_move_to_db(soup, character_name):
    try:
        img_container = soup.find("div", class_="imgContainer")
        image_link = "https://jut.su" + img_container.find("a")["href"]

        character_id = update_character_battle_image(character_name, image_link)

    except Exception as e:
        print("SCRAPE::IMAGE::FAILED \n" + str(e))
        sys.exit()
    
    return character_id

# ----------------Another----------------
    
def extract_character_name(seed_url):
    pattern = r'/ninja/(\w+)/'
    match = re.search(pattern, seed_url)
    # unquote just makes signs entcoded, such as %28 %29 to ()
    return unquote(match.group(1).replace("_", " ")) if match else None


# ----------------Main block----------------

def browse_jutsu_and_charac_image(seed_url, source_url, character_name, page_number=1):
    if page_number > 1:
        seed_url = seed_url.format(str(page_number))
    try:
        driver.get(seed_url)
        print("start parsing " + seed_url)
        page_source = driver.page_source
        soup = BeautifulSoup(page_source, "html.parser")

        character_id = None
        if page_number == 1:
            character_id = scrap_image_and_move_to_db(soup, character_name)

        scrap_jutsu_details_and_move_to_db(soup, character_name, character_id)

        next_button = soup.find("div", id="navigation").find('a', string="Далее")
        if next_button:
            seed_url = source_url + "page/{}"
            page_number += 1
            browse_jutsu_and_charac_image(seed_url, source_url, character_name, page_number)

    except Exception as e:
        print("BROWSE::JUTSU::FAILED \n" + str(e))
        sys.exit()

def main():
    global driver, cursor, unmatched_characters, mydb
    unmatched_characters = []

    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument('--log-level=3')
    driver = webdriver.Chrome(options=chrome_options)

    mydb = create_database_connection()
    cursor = mydb.cursor()

    try:
        character_links = create_characters_link_list()
        for link in character_links:
            character_name = extract_character_name(link)
            browse_jutsu_and_charac_image(link, link, character_name)
    finally:
        cursor.close()
        mydb.close()
        driver.quit()

if __name__ == "__main__":
    main()
    print(unmatched_characters)