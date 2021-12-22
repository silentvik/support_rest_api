# Support REST API
<b> Custom support service API. The project is still under development </b>
<br>
<br>
<b>Technologies:</b>
<br>
<ul>[Django]  [django-rest-framework]  [Docker]  [postgresSQL]  [simpleJWT] [PyTest]</ul>

<b>Requirements:</b>
<ul>Docker-compose installed</ul>

<b>Usage:</b>
<ul>1. git clone repository</ul>
<ul>2. cd support_rest_api</ul>
<ul>3. docker-compose --env-file ./.env.dev up -d --build web</ul>

<b>Run tests in a container:</b>
<ul>docker-compose --env-file ./.env.dev up -d --build tests</ul>

<b>Run tests in a web container before django:</b>
<ul>Configure .env.dev > ENTRYPOINT_RUN_TESTS=1</ul>

<br>
<b>Endpoints</b> <br>
<b>"api/v1/"</b>
