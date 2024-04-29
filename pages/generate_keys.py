"""
Script 100% de prueba, de momento no es necesario para el website.
"""

#import pickle
#from pathlib import Path

import streamlit_authenticator as stauth

names = ['Bernardo Cisneros', 'Emilio Alvarado']
usernames = ['bcisneros', 'libretico']
passwords = ['abcd1234', 'soybiengay']

# hashing passwords with bcrypt algorithm
hashed_passwords = stauth.Hasher(passwords).generate()

for i, pw in enumerate(hashed_passwords):
    print(f'{usernames[i]} : {pw}')

# pickle file to store hashed passwords.
'''
file_path = Path(__file__).parent / 'hashed_pw.pkl' # parent folder of this script (front/)
with file_path.open('wb') as file:
    pickle.dump(hashed_passwords, file)
'''