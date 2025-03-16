## Frontend: vite+react javaScript+swc, tailwind
to run the front end, simple install vite+react and tailwind, and run 
```
npm install
npm run dev
```
    
## Backend: Django, drf, for api calls
we are not using backend to serve html and it only serves data to frontend through api calls. this means only run backend simultaneously when you want to receive data from these apis.
```
python manage.py migrate
python manage.py runserver
```

## database
currently, after runniing 'python manage.py migrate' you will get a 'db.sqlite3' file, this is our temporary database. We are not using mysql from the get go, but it not difficult to switch to that if we want to in the future.

## ml_models:
documentation to be added
