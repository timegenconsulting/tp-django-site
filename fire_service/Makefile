env:
	pip install -r requirements/test.txt

run: env
	@echo "Running earthdata app..."
	. ./env.sh && \
	python main.py


test: env
	@echo "Running unit tests..."
	. ./env.sh && export TEST_DB="TRUE" && \
	coverage run --source=fireservice setup.py test ${module} && \
	coverage html && \
	coverage report
	@echo
	@echo "Flake8 errors in code ----------------"
	@python -m flake8 --max-line-length=180
	@echo "None"
	@echo "--------------------------------------"
	@echo "OK, no flake8 errors in code"
	@echo "--------------------------------------"
