def get_auth_headers(token):
    return {
        'Authorization': f'Bearer {token}'
    }
