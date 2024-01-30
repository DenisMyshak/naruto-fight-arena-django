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

mycursor.execute("ALTER TABLE jutsu AUTO_INCREMENT = 0")

for character in characters:
    if 'jutsu' not in character:
        continue
    
    c_jutsu = character['jutsu']

    for jutsu in c_jutsu:
      if len(jutsu) > 255 or jutsu.startswith("Naruto"):
         continue
      sql = "SELECT * FROM jutsu WHERE jutsu_name = %s"
      mycursor.execute(sql, (jutsu,))
      res = mycursor.fetchall()

      if len(res) == 0:
        sql = "INSERT INTO jutsu (jutsu_name) VALUES (%s)"
        val = (jutsu,)
        mycursor.execute(sql, val)
        mydb.commit()

mydb.close()