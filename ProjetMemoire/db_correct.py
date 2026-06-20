# update_passwords.py
import mysql.connector
import hashlib

# Connexion à la base
conn = mysql.connector.connect(
    host='localhost',
    user='root',
    password='',  # Votre mot de passe MySQL
    database='uac_thesis_manager'
)

cursor = conn.cursor()

# Mettre à jour tous les utilisateurs avec le bon mot de passe
password = "password123"
hashed = hashlib.sha256(password.encode()).hexdigest()

print(f"Mise à jour des mots de passe avec le hash: {hashed}")

# Mettre à jour tous les utilisateurs
cursor.execute("""
    UPDATE utilisateurs SET mot_de_passe = %s
""", (hashed,))

conn.commit()
print(f"✅ {cursor.rowcount} utilisateurs mis à jour")

# Vérification
cursor.execute("SELECT email, mot_de_passe FROM utilisateurs LIMIT 5")
for row in cursor.fetchall():
    print(f"  {row[0]} - {row[1][:20]}...")

cursor.close()
conn.close()
print("\n✅ Terminé! Vous pouvez maintenant vous connecter avec 'password123'")