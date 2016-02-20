#!/bin/bash
py.test --cov-report term-missing --cov=cardbox --cov-config .coveragerc tests
