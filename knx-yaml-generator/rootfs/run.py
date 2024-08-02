#!/usr/bin/env python

from settings import Settings
from generator import Generator

generator = Generator.instance()
generator.run()
generator.saveResult()


# print(generator)
