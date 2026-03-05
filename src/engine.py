import numpy as np
import pygame
import random

# Constants
GRAVITY = -9.8
DAMPING = -0.3
PYGAME_SCALE = 10

SCREEN_HEIGHT = 960
SCREEN_WIDTH = 1280

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
                        mouse_pos = pygame.mouse.get_pos()
                        self.add_point(mouse_pos[0], mouse_pos[1], 20) # add a 20 radius point

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
                point.add_connected_point(other)
                print(point.connected_points[other].resting_length)
                resting_length = point.connected_points[other].resting_length
                spring_physics(point, other, resting_length, dt, 0.5)

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
            
            pygame.draw.circle(self.screen, point.colour, point.pos, point.radius)
            for other in self.points:
                if point == other:
                    continue
                pygame.draw.line(self.screen, 'green', point.pos, other.pos)
            
    
    def add_point(self, x, y, r):
        point = Point(x, y, r)
        self.points.append(point)

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
    