#!/usr/bin/env python

price = int(input("How much was your meal?"))
tip_precentage = int(input("How would you like to tip them in percent?"))
tip = (tip_precentage / 100) * price

print(tip)