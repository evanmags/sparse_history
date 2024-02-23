# postgres history aggrigation table

# about

This project was concerned with the following problem statement:

Given a sparse table of patch updates to an object, implement queries to do the following:
- [x] Select all users in their present state
- [x] Select a single user in their present state
- [x] Select a single user at a single point in their history
- [x] Select a single user at every point in their history

Restrictions were placed such that:
- data must return from the database in the desired shape
- no modification should be done to the table structure



# requires
```bash
brew update && brew install docker docker-compose colima
colima start
mkdir data
docker-compose up

pip install -r requirements.txt
make seed-db
```

you are now free to explore the data and queries