.PHONY: help verify apply

TARGET ?= $(HOME)/sources/course-project

help:
	@echo "Lecture 11.3 — minimal observability and post-deploy agent"
	@echo ""
	@echo "make verify                 validate the distributed files"
	@echo "make apply TARGET=/path     copy the kit into a clean 11.2 course-project"

verify:
	@./scripts/verify-materials.sh

apply:
	@./apply-to-course-project.sh "$(TARGET)"
