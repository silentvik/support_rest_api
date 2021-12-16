from django.contrib.auth import get_user_model
from django.core.exceptions import ObjectDoesNotExist
# from support.models import Ticket
from rest_framework import exceptions
from rest_framework.permissions import BasePermission, IsAuthenticated

User = get_user_model()


class IsSupportAuthenticated(IsAuthenticated):
    pass
    # def has_permission(self, request, view):
    #     res = bool(request.user and request.user.is_authenticated and request.user.is_staff)
    #     return res


# class IsOwnerOrAdmin(BasePermission)
#     def has_object_permission(self, request, view, obj):
#         res = bool(request.user is  or request.user.is_superuser)
#         return res

class IsIdOwnerOrSuperUser(BasePermission):

    def has_permission(self, request, view):
        """
            Return `True` if permission is granted, `False` otherwise.
            Raise ObjectDoesNotExist error if requested user does not exist.
            If client asked user/.. by id - has_permission is working
        """
        print('***IsIdOwnerOrSuperUser.has_permission')
        print(f'     type(request.parser_context["kwargs"]) = {type(request.parser_context["kwargs"])}')
        user_id_kwarg = request.parser_context["kwargs"].get('pk', None)
        if not user_id_kwarg:
            user_id_kwarg = request.parser_context["kwargs"].get('user_id', None)

        print(f'***IsIdOwnerOrSuperUser.has_permission user_id_kwarg = {user_id_kwarg}')
        if user_id_kwarg:
            try:
                asked_user = User.objects.get(id=user_id_kwarg)
            except ObjectDoesNotExist:
                raise ObjectDoesNotExist('User with this id does not exist1')
            print(f'     asked_user={asked_user}, request.user = {request.user}')
            if request.user.is_superuser or asked_user.id == request.user.id:
                return True
            print('     asked_user NOT IS request.user')
            return False
        return True


class IsIdOwnerOrSupportPlus(BasePermission):

    def has_permission(self, request, view):
        """
            Return `True` if permission is granted, `False` otherwise.
            Raise ObjectDoesNotExist error if requested user does not exist.
            If client asked user/.. by id - has_permission is working
        """
        print('***IsIdOwnerOrSupportPlus.has_permission')
        # asked_user_id = request.parser_context["kwargs"].get('user_id', None)
        # if not asked_user_id:
        if request.method == 'POST':
            return True
        if request.user.is_superuser or request.user.is_support:
            return True

        asked_user_id = request.GET.get('user_id', None)
        print(f'     asked as user_id = {asked_user_id}')
        # print(f"     request.GET.get('user_id', None) = {request.GET.get('user_id', None)}")
        if asked_user_id is None:
            asked_user_id = request.parser_context["kwargs"].get('pk', None)
            print(f'     asked as pk = {asked_user_id}')

        if asked_user_id is not None:
            try:
                asked_user_id_int = int(asked_user_id)
                if asked_user_id_int == 0:
                    asked_user_id_int = request.user.id
                # print(f'    asked_user_id_int = {asked_user_id_int}')
                asked_user = User.objects.get(id=asked_user_id_int)
            except ObjectDoesNotExist:
                raise exceptions.NotFound(f'User with id=({asked_user_id_int}) does not exist.')

            except ValueError:
                raise exceptions.ValidationError(
                    f'Can not handle user_id({asked_user_id}). Please enter a valid user_id.'
                )

            # print(f'     asked_user={asked_user}, request.user = {request.user}')
            if asked_user.id == request.user.id:
                return True
            # print('     asked_user NOT IS request.user')
        else:
            raise exceptions.PermissionDenied(
                'Permission denied. '
                f'Current user_id = {request.user.id}. '
                f'Use "?user_id={request.user.id}" to get list of items or try another request method.'
            )
        return False


class IsItemOwnerOrSupportPlus(BasePermission):

    def has_permission(self, request, view):
        """
            Return `True` if permission is granted, raise an exception otherwise.
        """
        print('***IsItemOwnerOrSupportPlus.has_permission')

        asked_ticket_id = request.parser_context["kwargs"].get('ticket_id', None)
        restricted_class = view.restricted_class
        try:
            asked_ticket_id = int(asked_ticket_id)
            ticket = restricted_class.objects.get(id=asked_ticket_id)
        except ObjectDoesNotExist:
            raise exceptions.NotFound('Ticket with this id does not exist')
        except ValueError:
            raise exceptions.ValidationError(
                f'Can not handle ticket_id({asked_ticket_id}). Please enter a valid ticket_id.'
            )

        if request.user.is_superuser or request.user.is_support:
            return True
        if ticket.opened_by.id == request.user.id:
            return True
        else:
            raise exceptions.PermissionDenied(
                'Permission denied. Current user is not a ticket owner. '
                f'Current user_id = {request.user.id}'
            )


class MethodsPermissions(BasePermission):

    def has_permission(self, request, view):
        user = request.user
        if user.is_staff or user.is_superuser:
            return True
        if user.is_support:
            if request.method in ['GET', 'PATCH']:
                return True
        else:
            if request.method in ['GET']:
                return True
        if request.method in ['GET', 'PUT', 'PATCH', 'DELETE', '']:
            raise exceptions.PermissionDenied(
                f'Permission denied. Insufficient permissions to use the method {request.method}.'
            )
        raise exceptions.MethodNotAllowed(method=request.method)
