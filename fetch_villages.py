import requests
import mysql.connector

baseurl = 'https://narutodb.xyz/api/'
endpoint = 'village?page=1&limit=39'

r = requests.get(baseurl + endpoint)
data = r.json()

mydb = mysql.connector.connect(
  host="localhost",
  user="root",
  password="password",
  database="narutodb"
)

villageCursor = mydb.cursor()
characterCursor = mydb.cursor()

villages = data['villages']

for village in villages:
    v_id = village['id']
    v_name = village['name']
    v_characters = village['characters']

    villageCursor.execute("SELECT * FROM villages WHERE village_id = '" + str(v_id) + "'")
    allCorrespondVillages = villageCursor.fetchall()

    if len(allCorrespondVillages) == 0:
      sql = "INSERT INTO villages (village_id, village_name) VALUES (%s, %s)"
      val = (v_id, v_name)
      villageCursor.execute(sql, val)
      mydb.commit()

    for character in v_characters:
        c_id = character['id']
        characterCursor.execute("SELECT * FROM characters WHERE character_id = '" + str(c_id) + "'")
        allCorrespondCharacters = characterCursor.fetchall()

        if len(allCorrespondCharacters) != 0:
           villageCursor.execute("UPDATE characters SET village_id = '" + str(v_id) + "'"
           + "WHERE character_id = '" + str(c_id) + "'")
           mydb.commit()
    

villageCursor.close()
characterCursor.close()
mydb.close()



