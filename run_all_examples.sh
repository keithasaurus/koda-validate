#!/usr/bin/env bash

for f in examples/*.py
do
  python "$f" || exit 1
done
