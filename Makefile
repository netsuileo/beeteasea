run:
	docker-compose -f docker-compose.yml -f docker-compose.dev.yml up

lint:
	flake8 api tests --exclude=migrations 

test:
	docker-compose -f docker-compose.yml -f docker-compose.test.yml up
