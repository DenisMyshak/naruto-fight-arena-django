import requests
import mysql.connector

baseurl = 'https://narutodb.xyz/api/'
endpoint = 'clan?page=1&limit=58'

r = requests.get(baseurl + endpoint)
data = r.json()

mydb = mysql.connector.connect(
  host="localhost",
  user="root",
  password="password",
  database="narutodb"
)

clanCursor = mydb.cursor()
characterCursor = mydb.cursor()

clans = data['clans']

for clan in clans:
    cl_id = clan['id']
    cl_name = clan['name']
    cl_characters = clan['characters']

    clanCursor.execute("SELECT * FROM clans WHERE clan_id = '" + str(cl_id) + "'")
    allCorrespondClans = clanCursor.fetchall()

    if len(allCorrespondClans) == 0:
      sql = "INSERT INTO clans (clan_id, clan_name) VALUES (%s, %s)"
      val = (cl_id, cl_name)
      clanCursor.execute(sql, val)
      mydb.commit()

    for character in cl_characters:
        c_id = character['id']
        characterCursor.execute("SELECT * FROM characters WHERE character_id = '" + str(c_id) + "'")
        allCorrespondCharacters = characterCursor.fetchall()

        if len(allCorrespondCharacters) != 0:
           characterCursor.execute("UPDATE characters SET clan_id = '" + str(cl_id) + "'"
           + "WHERE character_id = '" + str(c_id) + "'")
           mydb.commit()
    

clanCursor.close()
characterCursor.close()
mydb.close()



