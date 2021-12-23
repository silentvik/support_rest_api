# Support REST API
This is an example of how I perform a company task (internship).<br>
Task details: BUSINESSTASK.md
<br>
<br>
<b>Technologies:</b>
<br>
<ul>Django, Django Rest Framework, Celery (Redis),
 	JWT auth, Docker-compose, Pytest, PostgreSQL.</ul>

<b>Requirements:</b>
<ul>Docker-compose installed</ul>

<b>Usage:</b>
<ul>1. git clone repository</ul>
<ul>2. cd support_rest_api</ul>
<ul>3. docker-compose --env-file ./.env.dev up -d --build web</ul>

<b>Run tests in a separate container:</b>
<ul>docker-compose --env-file ./.env.dev up -d --build tests</ul>

<b>Run tests in a web container before django:</b>
<ul>Configure .env.dev > ENTRYPOINT_RUN_TESTS=1</ul>

<br>
<b>Endpoints (shortly)</b> <br>
<b>"/api/v1":</b>
<ul>
 <li><b>"/" : </b> 
  <ul>[GET] - Home page.</ul>
 </li> 
 <li><b>"/obtainjwt/" : </b> 
  <ul>[POST] - Obtain access and refresh tokens.</ul>
 </li> 
 <li><b>"/refreshjwt/" : </b>
  <ul>[POST] - Refresh token.</ul>
  
 </li> 
 <li><b>"/users/" : </b>
  <ul>[GET] - List of registered users.</ul>
  <ul>[POST] - Create a new user.</ul>
 </li> 
 <li><b>"/users/(int)/" : </b>
  <ul>[GET] - View user profile.</ul>
  <ul>[PATCH] - Change any user profile field value.</ul>
  <ul>[PUT] - Change all user profile fields values.</ul>
  <ul>[DELETE] - Delete an account.
  <ul><li>note: "/users/0/" - to view current authenticated user (similar to "/users/me/").</li></ul></ul>
 </li> 
 <li><b>"/tickets/" : </b>
  <ul>[GET] - List of tickets.
   <ul><li>note: ?user_id=(int) - to view tickets of a specific user.</li></ul></ul>
  <ul>[POST] - Create a new ticket with first message.</ul>
 </li> 
 <li><b>"/tickets/(int)/" : </b>
  <ul>[GET] - Viewing a specific ticket.</ul>
  <ul>[PATCH] - Change any ticket field value.
  <ul><li>note: the ticket can be patched with the addition of a message at the end if it was inputted.</li></ul></ul>
  <ul>[PUT] - Change all ticket fields values.</ul>
  <ul>[DELETE] - Delete a ticket.
  </ul>
 </li>
 <li><b>"/tickets/(int)/messages/" : </b>
  <ul>[GET] - List of messages.</ul>
  <ul>[POST] - Create a new message.</ul>
 </li>
 <li><b>"/tickets/(int)/messages/(int)" : </b>
  <ul>[GET] - Viewing a specific message.</ul>
  <ul>[PATCH] - Change some message field.</ul>
  <ul>[PUT] - Change all message fields.</ul>
  <ul>[DELETE] - Delete a message.
  </ul>
 </li>
</ul>
<b>Url kwargs:</b> <br>
<ul><li><b>kwarg "mode". </b>
 <ul>description - selects the appropriate serializer.</ul>
 <ul>choices - [basic, default, expanded, full]. The selection can be reduced, depending on the authority.</ul>
 <ul>advice - [basic, expanded] mostly designed for support workers. [default] - for users. [full] - for staff.</ul>
 <ul>example - [GET] "api/v1/users/?mode=default"</ul>
</li></ul>
<ul><li><b>kwarg "order". </b>
 <ul>description - ordering by specific field (when trying to get list).</ul>
 <ul>fields - Different for every URL. The choice is still very limited.</ul>
 <ul>advice - list ordering is optimal from the box, but You can order by id.</ul>
 <ul>example - [GET] "api/v1/users/?order=id" or [GET] "api/v1/users/?order=unanswered"</ul>
</li></ul>
<ul><li><b>kwarg "limit". </b>
 <ul>description - limits the output (when trying to get list).</ul>
 <ul>input - 0<=limit.</ul>
 <ul>advice - use if necessary.</ul>
 <ul>example - [GET] "api/v1/users/?limit=10"</ul>
</li></ul>
<ul><li><b>filtering. </b>
 <ul>description - regular filters by fields.</ul>
 <ul>fields - Different for every URL.</ul>
 <ul>advice - use if necessary.</ul>
 <ul>example - [GET] "api/v1/tickets/?is_answered=false&is_closed=false"</ul>
</li></ul>
