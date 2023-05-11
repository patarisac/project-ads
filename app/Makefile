run-db:
	docker run --name studybuddy_db -p 5432:5432 -e POSTGRES_PASSWORD=passwordterkuat -e POSTGRES_DB=db -v ${PWD}/database_data:/var/lib/postgresql/data -d postgres

stop-db:
	docker stop studybuddy_db
	docker rm studybuddy_db

restart-db:
	docker restart studybuddy_db

reset-db:
	docker stop studybuddy_db
	docker rm studybuddy_db
	sudo rm -rf database_data
	mkdir database_data
	rm -rf alembic/versions/*
	# Now you should do alembic revision and upgrade

run-app:
	sudo chmod -R g+rwx database_data
	uvicorn main:app --reload
