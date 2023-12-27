import requests

def get_tiktok_followers_count(username, access_token):
    # URL de l'API TikTok
    api_url = 'https://open.tiktokapis.com/v2/research/user/info/'

    # Paramètres de requête
    query_params = {
        'fields': 'follower_count',
    }

    # En-têtes de requête
    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/json',
    }

    # Corps de la requête
    body_params = {
        'username': username,
    }

    try:
        # Envoi de la requête POST
        response = requests.post(api_url, params=query_params, headers=headers, json=body_params)
        response_data = response.json()

        # Vérification de la présence de la clé 'follower_count' dans la réponse
        if 'data' in response_data and 'follower_count' in response_data['data']:
            followers_count = response_data['data']['follower_count']
            return followers_count
        else:
            # Gestion des erreurs ou des cas où les données nécessaires ne sont pas présentes dans la réponse
            print('Erreur lors de la récupération des données.')
            return None

    except requests.exceptions.RequestException as e:
        print(f'Erreur de requête : {e}')
        return None

# Exemple d'utilisation de la fonction
username = 'leo.49_'
access_token = 'clt.LRm9ILzZ2hs3xjtawZkVs7X7FcAiLja2'

followers_count = get_tiktok_followers_count(username, access_token)

if followers_count is not None:
    print(f"Le compte {username} a {followers_count} abonnés sur TikTok.")
else:
    print("Impossible de récupérer le nombre d'abonnés.")