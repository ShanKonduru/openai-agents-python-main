@echo off
pytest --cov=. --cov-report=html --cov-report=term --cov-report=term-missing  --html=test_reports\report.html --self-contained-html tests\
