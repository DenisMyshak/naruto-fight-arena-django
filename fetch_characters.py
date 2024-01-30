import requests
import mysql.connector

baseurl = 'https://narutodb.xyz/api/'
endpoint = 'character?page=1&limit=1431'

r = requests.get(baseurl + endpoint)
data = r.json()

mydb = mysql.connector.connect(
  host="localhost",
  user="root",
  password="password",
  database="narutodb"
)

mycursor = mydb.cursor()

characters = data['characters']

for character in characters:
    if 'jutsu' not in character:
        continue
    
    c_id = character['id']
    c_name = character['name']
    c_image = '' if not character['images'] else character['images'][0] 

    mycursor.execute("SELECT * FROM characters WHERE character_id = '" + str(c_id) + "'")
    res = mycursor.fetchall()

    if len(res) == 0:
      sql = "INSERT INTO characters (character_id, character_name, character_image) VALUES (%s, %s, %s)"
      val = (c_id, c_name, c_image)
      mycursor.execute(sql, val)
      mydb.commit()

mydb.close()



