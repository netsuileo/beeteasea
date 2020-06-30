#!/bin/sh
wait-for-it postgres:5432 -t 60;
python ./main.py
