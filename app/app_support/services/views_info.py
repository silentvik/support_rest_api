# only simple info here

USERS_PAGE_INFO = {
    'Allowed methods info': {
        'GET': {
            'Info page': 'for non-support users',
            'List of users': 'for support+'
        },
        'POST': {
            'username': 'required',
            'password': 'required',
            'email': 'required',
            'first_name': 'optional',
            'last_name': 'optional',
            'screen_name': 'optional',
        },
    }
}

ROOT_PAGE_INFO = {
        'Endpoints': {
            'obtainjwt/': {
                'methods': {
                    'POST': 'create access and refresh tokens'
                }
            },
            'refreshjwt/': {
                'methods': {
                    'POST': 'create new access token',
                }
            },
            'users/': {
                'methods': {
                    'GET': 'view users list (auth support+). Args: [mode, filter, order]',
                    'POST': 'create access and refresh tokens',
                }
            },
            'users/<int>/': {
                'methods': {
                    'GET': 'view users list (auth support+)',
                    'POST': 'create access and refresh tokens',
                }
            },
            'tickets/': 'to view tickets (if have credentials for) or create new',
        }
    }
