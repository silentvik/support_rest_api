# Support REST API
<b> Custom API for support service. (Pet project) </b>
<br><br>
I'm creating this project just to practice.
<br>
<br>
Used:
<br>
[Django]  [django-rest-framework]  [Docker]  [postgresSQL]  [simpleJWT] [PyTest]

<br><br>
First:
1. git clone repository
2. cd support_rest_api
3. source yourvenv/bin/activate
4. pip install -r app/requirements.txt
5. docker-compose up -d --build

  
<b>Endpoints ("api/v1/")</b> <br>
    <ul>""</ul>
        <li>[GET] Info page</li>
    <ul>"obtainjwt/"</ul>
        <li>[POST] Obtain token pair.</li>
    <ul>"refreshjwt/"</ul>
        <li>[POST] Create new access token.</li>
    <ul>"users/"</ul>
        <li>[GET] Create new access token.</li>
        <li>[POST] Create new access token.</li>
