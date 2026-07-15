.PHONY: verify apply help

TARGET ?= /path/to/course-project

verify:
	@bash scripts/verify-materials.sh

apply:
	@bash apply-to-course-project.sh "$(TARGET)"

help:
	@echo "Lecture 11.2 — VPS deploy"
	@echo "  make verify                  перевірити матеріали без deploy"
	@echo "  make apply TARGET=/path      скопіювати kit у course-project"
