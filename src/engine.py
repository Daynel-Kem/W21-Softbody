import numpy as np
import pygame
import random

# Constants
GRAVITY = -9.8
DAMPING = -0.3
PYGAME_SCALE = 10

SCREEN_HEIGHT = 960 - 200
SCREEN_WIDTH = 1280 - 200

class Spring:
    def __init__(self, node1, node2):
        self.node1 = node1
        self.node2 = node2
        self.resting_length = (node1.pos - node2.pos).length()

class Point:
    def __init__(self, x, y, r):
        self.pos = pygame.Vector2(x, y)
        self.vel = pygame.Vector2(0, 0)
        self.radius = r
        
        self.colour = (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))

        self.connected_points = {}

    def add_connected_point(self, other):
        if other not in self.connected_points:
            self.connected_points[other] = Spring(self, other)
        if self not in other.connected_points:
            other.connected_points[self] = Spring(other, self)

class Shape:
    def __init__(self, points, connections):
        self.points = points
        self.connections = connections

        self.skeleton = {}


def spring_physics(point1, point2, resting_length, dt, k):
    vec = point1.pos - point2.pos
    vec_length = vec.length()
    vec_normalized = vec.normalize()

    move_length = k * (resting_length - vec_length)

    vel_diff = point1.vel - point2.vel
    dot = vec_normalized.dot(vel_diff)
    damping_force = 0.5 * dot * DAMPING
    total_force = move_length + damping_force
    total_force = np.clip(total_force, -1000, 1000)

    point1.vel += vec_normalized * total_force * dt * PYGAME_SCALE
    point2.vel -= vec_normalized * total_force * dt * PYGAME_SCALE

class PhysicsEngine:
    def __init__(self):
        pygame.init()
        self.clock = pygame.time.Clock()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        self.font = pygame.font.SysFont('Arial', 20)

        self.points: list[Point] = []

        self.running = False
        self.debug = False

    def start(self):
        self.running = True
        grabbed_point = None
        while self.running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.stop()
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:
                        mouse_pos = event.pos
                        for point in self.points:
                            if (mouse_pos[0] < point.pos[0] + point.radius and mouse_pos[0] > point.pos[0] - point.radius) and (mouse_pos[1] < point.pos[1] + point.radius and mouse_pos[1] > point.pos[1] - point.radius):
                                grabbed_point = point
                                break
                elif event.type == pygame.MOUSEBUTTONUP:
                    if event.button == 1:
                        grabbed_point = None

                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_d:
                        self.toggle_debug()
                    if event.key == pygame.K_0:
                        self.clear()
                    if event.key == pygame.K_SPACE:
                        # spawn in a regular ball
                        mouse_pos = pygame.mouse.get_pos()
                        self.add_point(mouse_pos[0], mouse_pos[1], 20) # add a 20 radius point
                    if event.key == pygame.K_l:
                        # spawn in a tetris L shape
                        mouse_pos == pygame.mouse.get_pos()
                        self.add_l(mouse_pos[0], mouse_pos[1], 5) 
                        

            self.screen.fill('white')

            dt = self.clock.tick(120) / 1000

            mouse_pos = pygame.mouse.get_pos()
            if grabbed_point:
                dx = (mouse_pos[0] - prev_mouse_pos[0]) / PYGAME_SCALE
                dy = (mouse_pos[1] - prev_mouse_pos[1]) / PYGAME_SCALE

                grabbed_point.pos = pygame.Vector2(mouse_pos)
                grabbed_point.vel = pygame.Vector2(dx / dt, dy / dt)

                max_speed = 2000
                speed = np.linalg.norm(grabbed_point.vel)

                if speed > max_speed:
                    grabbed_point.vel = grabbed_point.vel / speed * max_speed
            prev_mouse_pos = mouse_pos

            # this is where the physics updates will go
            self.update(dt)
            self.render()

            pygame.display.flip()

    def stop(self):
        self.running = False
        pygame.quit()

    def update(self, dt):
        for point in self.points:

            # Check Border Collisions
            if point.pos[0] + point.radius >= SCREEN_WIDTH:
                point.pos[0] = SCREEN_WIDTH - point.radius
                point.vel[0] *= -0.8
            if point.pos[0] - point.radius <= 0:
                point.pos[0] = point.radius
                point.vel[0] *= -0.8
            if point.pos[1] + point.radius >= SCREEN_HEIGHT:
                point.pos[1] = SCREEN_HEIGHT - point.radius
                point.vel[1] *= -0.8
            if point.pos[1] - point.radius <= 0:
                point.pos[1] = point.radius
                point.vel[1] *= -0.8

            # Apply Spring Physics
            for other in self.points:
                if point == other:
                    continue
                # point.add_connected_point(other)
                # print(point.connected_points[other].resting_length)
                if other in point.connected_points:
                    resting_length = point.connected_points[other].resting_length
                    spring_physics(point, other, resting_length, dt, 10) # im changing the k constant right here for now

            # Add forces and velocity
            point.vel += pygame.Vector2(0, -1) * GRAVITY * dt * PYGAME_SCALE
            point.pos += point.vel * dt * PYGAME_SCALE

    def render(self):
        for point in self.points:
            if self.debug:
                label_surface = self.font.render(f"({round(point.pos[0])}, {round(point.pos[1])})", True, (0, 0, 0))
                label_rect = label_surface.get_rect()
                label_rect.center = (point.pos[0], point.pos[1] - point.radius * 1.6)
                self.screen.blit(label_surface, label_rect)
                pygame.display.update()
            
            for other in self.points:
                if point == other:
                    continue
                if other in point.connected_points:
                    pygame.draw.line(self.screen, 'green', point.pos, other.pos)
            pygame.draw.circle(self.screen, point.colour, point.pos, point.radius)
            
    
    def add_point(self, x, y, r):
        point = Point(x, y, r)
        self.points.append(point)

    def add_l(self, x, y, size):
        p1 = Point(x, y, r=5)
        p2 = Point(x + size * PYGAME_SCALE, y, r=5)
        p3 = Point(x, y + size * PYGAME_SCALE, r=5)
        p4 = Point(x + size * PYGAME_SCALE, y + size * PYGAME_SCALE, r=5)
        p1.add_connected_point(p2)
        p1.add_connected_point(p3)
        p1.add_connected_point(p4)
        p2.add_connected_point(p3)
        p2.add_connected_point(p4)
        p3.add_connected_point(p4)

        p5 = Point(x, y + size * 2 * PYGAME_SCALE, r=5)
        p6 = Point(x + size * PYGAME_SCALE, y + size * 2 * PYGAME_SCALE, r=5)

        p5.add_connected_point(p3)
        p5.add_connected_point(p4)
        p5.add_connected_point(p6)
        p6.add_connected_point(p3)
        p6.add_connected_point(p4)

        p7 = Point(x, y + size * 3 * PYGAME_SCALE, r=5)
        p8 = Point(x + size * PYGAME_SCALE, y + size * 3 * PYGAME_SCALE, r=5)

        p7.add_connected_point(p5)
        p7.add_connected_point(p6)
        p7.add_connected_point(p8)
        p8.add_connected_point(p5)
        p8.add_connected_point(p6)

        p9 = Point(x + size * 2 * PYGAME_SCALE, y + size * 2 * PYGAME_SCALE, r=5)
        p10 = Point(x + size * 2 * PYGAME_SCALE, y + size * 3 * PYGAME_SCALE, r=5)

        p9.add_connected_point(p6)
        p9.add_connected_point(p8)
        p9.add_connected_point(p10)
        p10.add_connected_point(p6)
        p10.add_connected_point(p8)

        self.points.append(p1)
        self.points.append(p2)
        self.points.append(p3)
        self.points.append(p4)
        self.points.append(p5)
        self.points.append(p6)
        self.points.append(p7)
        self.points.append(p8)
        self.points.append(p9)
        self.points.append(p10)

    def toggle_debug(self):
        if self.debug:
            self.debug = False
        else:
            self.debug = True

    def clear(self):
        self.points.clear()

if __name__ == "__main__":
    pygame.font.get_fonts()
    engine = PhysicsEngine()
    engine.start()
    