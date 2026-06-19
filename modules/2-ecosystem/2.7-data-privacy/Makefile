.PHONY: run run-with-disabled clean

run:
	python3 main.py

run-with-disabled:
	CLAUDE_CODE_DISABLE_NONESSENTIAL_TRAFFIC=1 \
	CLAUDE_CODE_SUBPROCESS_ENV_SCRUB=1 \
	python3 main.py

clean:
	rm -rf __pycache__ *.pyc
