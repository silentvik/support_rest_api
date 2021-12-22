from django.contrib.auth import get_user_model
from django.core.exceptions import ObjectDoesNotExist
from rest_framework import exceptions
from rest_framework.permissions import BasePermission

User = get_user_model()


class IsIdOwnerOrSupportPlus(BasePermission):

    def has_permission(self, request, view):
        """
            Return `True` if permission is granted, `False` otherwise.
            Raise ObjectDoesNotExist error if requested user does not exist.
            If client asked user by id - has_permission is working.
            Can raise error with helpful message.
        """

        if request.method == 'POST':
            return True
        if request.user.is_superuser or request.user.is_support:
            return True

        asked_user_id = request.GET.get('user_id', None)
        if asked_user_id is None:
            asked_user_id = request.parser_context["kwargs"].get('pk', None)

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

            if asked_user.id == request.user.id:
                return True
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
            self.restricted_class must be set.
            restricted_class - Ticket in support_app.
            User can't view tickets owned by another users.
            Can raise error with helpful message.
        """

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
        """
            Return `True` if permission is granted, raise an exception otherwise.
            Users with support status can't detele tickets, staff+ can.
            Users can't 'patch' tickets, but can view.
            Can raise error with helpful message.
        """
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
