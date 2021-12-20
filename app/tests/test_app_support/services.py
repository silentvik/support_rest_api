from django.contrib.auth import get_user_model
from rest_framework.authtoken.models import Token

User = get_user_model()


class ServiceClass:
    """
        This class helps to make complex tests with multiple usertypes and kwargs.
    """
    USER_TYPE_ARGS_PACK = {
        # usertype: (is_superuser, is_staff, is_support, forced auth)
        'Admin': (True, True, True, True),
        'Staff': (False, True, True, True),
        'Support': (False, False, True, True),
        'User': (False, False, False, True),
        'Anonimous': (False, False, False, False),
    }

    @staticmethod
    def user_creation_generator(create_user_fxt, api_client_fxt, default_username='test1000', **kwargs):
        """
            Generator.
            create users / auth them (if created).
            returns: api_client_fixture, user object (if created)
        """
        user_type_args_pack = ServiceClass.USER_TYPE_ARGS_PACK
        for i, key in enumerate(user_type_args_pack.keys()):
            args_pack = user_type_args_pack[key]
            if args_pack[3]:
                user = create_user_fxt(
                    username=default_username+str(i),
                    is_superuser=args_pack[0],
                    is_staff=args_pack[1],
                    is_support=args_pack[2],
                    **kwargs
                )
                api_client_fxt.force_authenticate(user=user)
            else:
                user = None
            yield (api_client_fxt, user)

    @staticmethod
    def GET_response_generator(url, user_creation_generator, *args, **kwargs):
        """
            Generator.
            Generates GET responces with given url and user_creation_generator
        """
        for api_client, user in user_creation_generator(*args, **kwargs):
            yield (api_client.get(url), user)

    @staticmethod
    def make_responses(response_generator, *args, **kwargs):
        """
            Returns a list filled with only results. (Excludes user objects.)
        """
        return [response for response, _ in response_generator(*args, **kwargs)]

    @staticmethod
    def args_responses_generator(key_word, args_list, url, make_responses_func, *args, **kwargs):
        """
            Generator.
            Applies given <key_word> for every arg in <args_list> and adds it to the given <url>.
            Creates responces pack for every completed url.
            Returns responces one by one.
        """
        for j, val in enumerate(args_list):
            new_url = url + f'?{key_word}={val}'
            kwargs['url'] = new_url
            kwargs['default_username'] = kwargs['default_username']+str(j)
            responses = make_responses_func(*args, **kwargs)
            for i, response in enumerate(responses):
                yield (i, j, response)


def create_token(user):
    token, _ = Token.objects.get_or_create(user=user)
    return token


class TestMixin:
    default_username = 'test'
    default_password = 'testtest'
    default_email = '@aa.aa'
    users = {}

    def create_tmp_users(self, count_to_create=3, celery_task=None):
        total_written = 0
        queryset = User.objects.all()
        ln = len(queryset)
        for postfix in range(0, ln+count_to_create):
            user = queryset.filter(username=f'{self.default_username}{postfix}').first()
            if not user:
                if celery_task:
                    celery_task(
                        username=f'{self.default_username}{postfix}',
                        password=self.default_password,
                        email=f'{self.default_username}{postfix}{self.default_email}',
                    )
                else:
                    user = User.objects.create(
                        username=f'{self.default_username}{postfix}',
                        password=self.default_password,
                        email=f'{self.default_username}{postfix}{self.default_email}',
                    )
                    user.save()
                total_written += 1
                self.users[str(total_written)] = {'username': f'{self.default_username}{postfix}'}
                if total_written >= count_to_create:
                    break

    def delete_tmp_users(self, celery_task=None):
        users = self.users
        for key in users.keys():
            username = users[key]['username']
            if celery_task:
                celery_task(username=username)
            else:
                user = User.objects.get(username=username)
                user.delete()
