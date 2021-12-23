Business task: create a support service (api).
1) The user can create and send tickets.
2) Support can view tickets, respond to them.
3) The user can view the support response and add a new message.
4) Support can change ticket statuses.

Technologies:
	Django + Django Rest Framework, Celery (Redis),
 	JWT auth, Docker-compose, Pytest, PostgreSQL.
	
From me:
1) The user has the right to create as many tickets as he(she) wants on different topics (product, security, etc.). 
2) The user can view only his own tickets, his own profile.
    User cant view some staff-only fields.
3) Support can view tickets in various convenient modes, as well as view users with their tickets, excluding user details.
4) In addition to the usual filters, support can sort tickets by the longest period without a response.
    Sort the list of users by the actual ticket with the longest unanswered period.
    (Without additional requests to the database.)
5) Support staff can exchange information within the ticket (if, for example,
    it is a difficult case and it is necessary for someone else to figure it out).
    The information is hidden from users ofc.
6) The support can change the status of tickets, but cannot delete them.
    Only the admin can delete a ticket.
7) The ticket contains messages. Ticket can be created with message together.
8) The ticket can be patched (by support+) with adding a message in the end. (Its only an option. This can be useful if a support worker wants to both add a message and close the ticket at once.)
9) Admin (and staff) can find out who (from the support service) closed the ticket.
10) Admin (staff) can change/delete messages from tickets.
11) Admin (staff) have full control and can make support workers from users.
12) Friendly error messages: incorrect input of arguments or references, insufficient rights.
13) If possible, multiple queries in the database are excluded.
14) The project can be easily configured if you need to restrict the access
    of support workers to user's personal information, or something like this.

Notes:
1) Celery used so far only for async deletion of objects.
2) Several tests added symbolically.
