import numpy as np
import pygame as pg

class Point:
    def __init__(self):
        self.position: list[float]
        self.velocity: list[float]


class Engine:
    def __init__(self):
        pass

    def start(self):
        pg.init()
        self.running = True

    def stop():
        pass