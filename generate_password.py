import streamlit_authenticator as stauth

hasher = stauth.Hasher()
hashed_password = hasher.hash('senha123')
print(f"Senha hasheada: {hashed_password}") 