#!/bin/sh

coverage run --source='.' manage.py test 
coverage report -m
coverage html

