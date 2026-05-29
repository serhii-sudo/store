#!/bin/bash

black --line-length 120 --exclude protos store
ruff check store --fix-only