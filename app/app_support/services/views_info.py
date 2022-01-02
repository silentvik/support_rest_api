# only simple info here

USERS_PAGE_INFO = {
    'Errors': ['Insufficient permissions to display the list of users', ],
    'Allowed methods': {
        'GET': {
            'response': 'list of users',
            'auth': 'support+'
        },
        'POST': {
            'response': 'created user object',
            'auth': 'any',
            'fields': {
                'username': 'required',
                'password': 'required',
                'email': 'required',
                'first_name': 'optional',
                'last_name': 'optional',
                'screen_name': 'optional',
            }
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


def get_delete_process_msg(obj_name, user_id):
    """
        Returns a message that can be used in delayed object deletion.
        Returns [str].
    """
    return f'The process of deletion the {obj_name} with id {user_id} has been started.'
