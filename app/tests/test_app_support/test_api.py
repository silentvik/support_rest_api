import pytest
from django.urls import reverse

from .services import ServiceClass

URL_PREFIX = '/api/v1/'


@pytest.mark.django_db
class TestApiGET:
    """
        Test all urls w get method.
        Tests aren't detailed yet.
        About result type checks:
            when the client has permissions to view <list> - result['data'] type will be a <list>;
            else result['data'] type will be a <dict> with error(s) message or <dict> with some helpfull information.
    """

    def test_unknown_page(self, api_client):
        for url_postfix in ['asdf/', 'fffffffasss/asfaf/', 'sos/', 'g/g/g/', '///', 'asdf?ПРИВЕТ']:
            url = URL_PREFIX + url_postfix
            response = api_client.get(url)
            assert response.status_code == 404

    def test_home_page(self, create_user, api_client):
        url = reverse('home_page')
        responses = ServiceClass.make_responses(
            response_generator=ServiceClass.GET_response_generator,
            user_creation_generator=ServiceClass.user_creation_generator,
            url=url,
            create_user_fxt=create_user,
            api_client_fxt=api_client
        )
        for response in responses:
            assert response.status_code == 200

    def test_users_list_no_args(self, create_user, api_client):
        """
            The page opens without specifying arguments. But with different authentication.
        """

        url = reverse('users_list')
        expected_results = [(list, 200), (list, 200), (list, 200), (dict, 200), (dict, 200)]

        responses = ServiceClass.make_responses(
            response_generator=ServiceClass.GET_response_generator,
            user_creation_generator=ServiceClass.user_creation_generator,
            url=url,
            create_user_fxt=create_user,
            api_client_fxt=api_client
        )
        for i, response in enumerate(responses):
            assert response.status_code == expected_results[i][1]
            content = response.json()
            assert type(content['data']) == expected_results[i][0]

    def test_users_list_kwarg_mode_complex(self, create_user, api_client):
        """
            Test users_list page with arg '?mode='
        """

        url = reverse('users_list')
        args_list = ['basic', 'expanded', 'default', 'full']
        key_word = 'mode'

        expected_results_matrix = [
            # every tuple here contain (type of resulting data, response status, count of shown attributes)
            [(list, 200, 3), (list, 200, 4), (list, 200, 10), (list, 200, 14)],  # admin
            [(list, 200, 3), (list, 200, 4), (list, 200, 10), (list, 200, 14)],  # staff
            [(list, 200, 3), (list, 200, 4), (list, 200, 10), (type(None), 400, None)],  # support
            [(dict, 200, None), (dict, 200, None), (dict, 200, None), (dict, 200, None)],  # user
            [(dict, 200, None), (dict, 200, None), (dict, 200, None), (dict, 200, None)],  # anonim
        ]

        args_responses_generator = ServiceClass.args_responses_generator(
            key_word,
            args_list,
            url,
            make_responses_func=ServiceClass.make_responses,
            response_generator=ServiceClass.GET_response_generator,
            user_creation_generator=ServiceClass.user_creation_generator,
            api_client_fxt=api_client,
            create_user_fxt=create_user,
            default_username='test1000',
        )
        for i, j, response in args_responses_generator:
            content = response.json()
            content_data = content.get('data', None)
            content_type = type(content_data)
            len_user_attributes = None
            if content_type == list:
                len_user_attributes = len(content_data[0]['attributes'])

            res = (content_type, response.status_code, len_user_attributes)
            expected_res = expected_results_matrix[i][j]
            assert res == expected_res

    # perhaps it will be completed
    def test_user_profile(self, create_user, api_client):
        pass

    def test_tickets_list(self, create_user, api_client):
        pass

    def test_tickets_list_owner(self, create_user, api_client):
        pass

    def test_specific_ticket(self, create_user, api_client):
        pass

    def test_specific_message(self, create_user, api_client):
        pass


class TestApiPOST:
    pass
