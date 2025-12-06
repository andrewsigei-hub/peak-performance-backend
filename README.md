# Movies App

## Description
- This is the backend that powers our movies app, we use fastapi as the framework and sqlalchemy for db management
- At the beginning, we will use sqlite and if we host the application, we will switch to postgres

## Project setup

1. Install the required packages with `pipenv install sqlalchemy alembic "fastapi[standard]"`
2. Active the virtual environment with `pipenv shell`
3. Initialize migrations with the command `alembic init migrations`. We only run this command once
4. Update the alembic.ini file and set sqlalchemy.url to whatever the database should be i.e `sqlite:///movies.db`
5. Create the two necessary python files with `touch models.py app.py`
6. After setting up at least one model, we need to modify the env.py inside the migrations folder and update the target_metadata
```py
from models import Base
target_metadata = Base.metadata
```

- To start the backend use the command ```fastapi dev app.py```

## Handling migrations using alembic
- To generate a migration file we run `alembic revision --autogenerate -m "the message"`
- To apply the migration, we run `alembic upgrade head`
