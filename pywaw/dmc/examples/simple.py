#!/usr/bin/env python2

class DMeta(type):
    
    def __new__(cls, name, bases, body):
        klass = super(DMeta, cls).__new__(cls, name, bases, body)
        return klass

