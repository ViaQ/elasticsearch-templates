#!/usr/bin/env bash

rm -rf foo.test.*

make -f Makefile

ls -la
