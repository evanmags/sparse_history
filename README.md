# postgres history aggrigation table

# about

This project was concerned with the following problem statement:

Given a sparse table of patch updates to an object, implement queries to do the following:
- [x] Select all users in their present state
- [x] Select a single user in their present state
- [x] Select a single user at a single point in their history
- [ ] Select a single user at every point in their history

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