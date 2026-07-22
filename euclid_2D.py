from datetime import datetime
import math
from multiprocessing import Process, Queue
import os
import pygame
import random
import sys

# <--- Global variabless init
engine_is_running = True
particle_create_multi_mode = False
particle_create_static_draw_mode = False
particle_drawing = False
particle_create_static_mode = False
particle_gravity = False
gravity = 0.9
force_field_radius = 100
force = 5
particle_velocity_thermal_mode = False
night_mode = False
particle_force_field_mode = False

# <--- Check if the engine is stopping
def check_engine_events(particles: list, screen):
    global engine_is_running
    global particle_create_multi_mode
    global particle_create_static_draw_mode
    global particle_drawing
    global particle_create_static_mode
    global particle_gravity
    global particle_velocity_thermal_mode
    global night_mode
    global particle_force_field_mode
    global force_field_radius

    for event in pygame.event.get():
        if event.type == pygame.MOUSEBUTTONDOWN and engine_is_running:
            if not particle_create_multi_mode and not particle_create_static_draw_mode and not particle_create_static_mode:
                particles.append(Particle(event.pos[0], event.pos[1]))
            elif particle_create_multi_mode and not particle_create_static_draw_mode and not particle_create_static_mode:
                for _ in range(50):
                    particles.append(Particle(event.pos[0], event.pos[1]))
            elif not particle_create_multi_mode and particle_create_static_draw_mode and not particle_create_static_mode:
                particle_drawing = True
            elif not particle_create_multi_mode and not particle_create_static_draw_mode and particle_create_static_mode:
                particles.append(Particle(event.pos[0], event.pos[1], move_mode="static"))
        elif event.type == pygame.MOUSEMOTION:
            if particle_drawing:
                particles.append(Particle(event.pos[0], event.pos[1], move_mode="draw"))
            elif particle_create_static_mode:
                p.pos_x = pygame.mouse.get_pos()[0]
                p.pos_y = pygame.mouse.get_pos()[1]
                if event.rel[0] != 0 and event.rel[1] != 0:
                    p.velocity_x = event.rel[0]
                    p.velocity_y = event.rel[1]
                else:
                    p.velocity_x = 0
                    p.velocity_y = 0
        elif event.type == pygame.MOUSEBUTTONUP and particle_drawing:
            particle_drawing = False
        elif event.type == pygame.QUIT:
            print("[LOG] Stopping the engine and EXITING!")
            pygame.quit()
            sys.exit()
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                print("[LOG] Stopping the engine and EXITING!")
                pygame.quit()
                sys.exit()
            elif event.key == pygame.K_p:
                engine_is_running = not engine_is_running
                print("[LOG] Engine is RUNNING!") if engine_is_running else print("[LOG] Engine is PAUSED!")
            elif event.key == pygame.K_c:
                particles.clear()
                print("[LOG] Display is cleared! All particles DELETED!")
            elif event.key == pygame.K_m:
                particle_create_static_draw_mode = False
                particle_create_static_mode = False
                particle_force_field_mode = False
                particle_create_multi_mode = not particle_create_multi_mode
                print("[LOG] MULTIPLE Particle creation mode ENABLED") if particle_create_multi_mode else print("[LOG] MULTIPLE Particle creation mode DISABLED")
            elif event.key == pygame.K_d:
                particle_create_multi_mode = False
                particle_create_static_mode = False
                particle_force_field_mode = False
                particle_create_static_draw_mode = not particle_create_static_draw_mode
                print("[LOG] STATIC Particle draw mode ENABLED") if particle_create_static_draw_mode else print("[LOG] STATIC Particle draw mode DISABLED")
            elif event.key == pygame.K_s:
                particle_create_multi_mode = False
                particle_create_static_draw_mode = False
                particle_force_field_mode = False
                particle_create_static_mode = not particle_create_static_mode
                print("[LOG] STATIC Particle mode ENABLED") if particle_create_static_mode else print("[LOG] STATIC Particle mode DISABLED")
            elif event.key == pygame.K_g:
                particle_gravity = not particle_gravity
                print("[LOG] GRAVITY with Particle mode ENABLED") if particle_gravity else print("[LOG] GRAVITY with Particle mode DISABLED")
            elif event.key == pygame.K_t:
                particle_velocity_thermal_mode = not particle_velocity_thermal_mode
                print("[LOG] VELOCITY THERMAL mode for Particle ENABLED") if particle_velocity_thermal_mode else print("[LOG] VELOCITY THERMAL mode for Particle DISABLED")
            elif event.key == pygame.K_n:
                night_mode = not night_mode
                print("[LOG] NIGHT MODE ENABLED") if night_mode else print("[LOG] NIGHT MODE DISABLED")
            elif event.key == pygame.K_h:
                particle_create_multi_mode = False
                particle_create_static_mode = False
                particle_create_static_draw_mode = False
                particle_force_field_mode = not particle_force_field_mode
                print(f"[LOG] HOLD MODE for Particles ENABLED") if particle_force_field_mode else print(f"[LOG] HOLD MODE for Particles DISABLED")
            elif event.key == pygame.K_EQUALS:
                if particle_force_field_mode and force_field_radius < 500:
                    force_field_radius += 10
                    print(f"[LOG] FORCE FIELD radius increased by 10 ({force_field_radius})")
            elif event.key == pygame.K_MINUS:
                if particle_force_field_mode and force_field_radius > 50:
                    force_field_radius -= 10
                    print(f"[LOG] FORCE FIELD radius decreased by 10 ({force_field_radius})")
            elif event.key == pygame.K_PRINTSCREEN:
                name = f"euclid2d_screenshot_{datetime.now().strftime("%Y%m%d%H%M%S")}.png"
                pygame.image.save(screen, name)
                print(f"[LOG] SIMULATION SCREEN screenshot was made!")


# <--- Class: Particle
class Particle():

    def __init__(self, pos_x, pos_y, move_mode="dynamic"):
        self.colour = [random.randint(0,255), random.randint(0,255), random.randint(0,255)]
        self.radius = random.randint(5, 10)
        if move_mode == "static":
            self.radius = 15
        self.pos_x = pos_x
        self.pos_y = pos_y
        if move_mode == "dynamic":
            self.velocity_x = random.randint(3, 10)*random.choice([1, -1])
            self.velocity_y = random.randint(3, 10)*random.choice([1, -1])
        elif move_mode == "draw" or move_mode == "static":
            self.velocity_x = 0
            self.velocity_y = 0

    def p_draw(self, screen):
        pygame.draw.circle(screen, self.colour, [self.pos_x, self.pos_y], self.radius)

    def p_move(self):
        if particle_gravity:
            self.velocity_y += gravity
        # <--- Force field mode calculations
        if particle_force_field_mode:
            pos_mouse_vector = pygame.math.Vector2(pygame.mouse.get_pos())
            particle_to_mouse_vector = pos_mouse_vector - pygame.math.Vector2(p.pos_x, p.pos_y)
            particle_to_mouse_distance = particle_to_mouse_vector.length()

            if 0 < particle_to_mouse_distance < force_field_radius:
                particle_to_mouse_vector = particle_to_mouse_vector.normalize() * force
                self.velocity_x += particle_to_mouse_vector.x
                self.velocity_y += particle_to_mouse_vector.y
        
        self.pos_x += self.velocity_x
        self.pos_y += self.velocity_y
        
        # <--- X side
        if self.pos_x < self.radius: # If lesser than RIGHT (X) boundary
            self.velocity_x *= -1 if particle_gravity == False else -gravity
            self.pos_x = self.radius
        elif self.pos_x > screen_width - self.radius: # If greater than LEFT X boundary
            self.velocity_x *= -1 if particle_gravity == False else -gravity
            self.pos_x = screen_width - self.radius

        # <--- Y side
        if self.pos_y < self.radius: # If lesser than BOTTOM (Y) boundary
            self.velocity_y *= -1 if particle_gravity == False else -gravity
            self.pos_y = self.radius
        elif self.pos_y > screen_height - self.radius: # If greater than TOP (Y) boundary
            self.velocity_y *= -1 if particle_gravity == False else -gravity
            self.pos_y = screen_height - self.radius

    def p_collide(self, other: "Particle"):
        # <--- Euclidian distance calculations
        distance_x = self.pos_x - other.pos_x
        if abs(distance_x) > self.radius + other.radius:
            return
        
        distance_y = self.pos_y - other.pos_y
        if abs(distance_y) > self.radius + other.radius:
            return

        distance = math.sqrt(distance_x**2 + distance_y**2)

        if distance < self.radius + other.radius:
            # <--- Distance vector and normal vector calculations
            distance_vector = pygame.math.Vector2(distance_x, distance_y)

            if distance_vector.length() > 0:
                normal_vector = distance_vector.normalize()
            else:
                normal_vector = pygame.math.Vector2(1,0)

            relative_velocity_vector = pygame.math.Vector2(self.velocity_x, self.velocity_y) - pygame.math.Vector2(other.velocity_x, other.velocity_y)
            normal_velocity_vector = relative_velocity_vector.dot(normal_vector)

            if normal_velocity_vector > 0:
                return

            # <--- Overlapping particles prevention calculations
            overlap = (self.radius + other.radius) - distance
            self.pos_x += normal_vector.x * (overlap/2)
            self.pos_y += normal_vector.y * (overlap/2)
            other.pos_x -= normal_vector.x * (overlap/2)
            other.pos_y -= normal_vector.y * (overlap/2)

            # <--- Elastic collision physics calculations
            m_p1 = self.radius ** 2
            m_p2 = other.radius ** 2
            restitution_coeff = 0.8
            impulse = -(1+restitution_coeff) * normal_velocity_vector / (1/m_p1 + 1/m_p2)

            self.velocity_x += (impulse/m_p1) * normal_vector.x
            self.velocity_y += (impulse/m_p1) * normal_vector.y
            other.velocity_x -= (impulse/m_p2) * normal_vector.x
            other.velocity_y -= (impulse/m_p2) * normal_vector.y

# <--- Menu Screen initializing
def menu_screen(data_queue: Queue):
    os.environ['SDL_VIDEO_WINDOW_POS'] = "1630, 50"
    pygame.init()
    menu_screen_bg_colour = (28, 61, 71)
    menu_screen_width = 290
    menu_screen_height = 560
    menu_screen = pygame.display.set_mode((menu_screen_width, menu_screen_height))
    font = pygame.font.SysFont("Calibri", 18)
    clock = pygame.time.Clock()

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pass
        
        while not data_queue.empty():
            sim_data = data_queue.get_nowait()

        menu_screen.fill(menu_screen_bg_colour)
        font_particles = font.render(f"Particles: {sim_data[0]}", True, (255,255,255))
        font_particle_create_multi_mode = font.render(f"Particle create multi mode: {sim_data[1]}", True, (255,255,255))
        font_particle_create_static_draw_mode = font.render(f"Particle create static draw mode: {sim_data[2]}", True, (255,255,255))
        font_particle_create_static_mode = font.render(f"Particle create static mode: {sim_data[3]}", True, (255,255,255))
        font_particle_gravity_mode = font.render(f"Particle gravity mode: {sim_data[4]}", True, (255,255,255))
        font_particle_velocity_thermal_mode = font.render(f"Particle velocity thermal mode: {sim_data[5]}", True, (255,255,255))
        font_particle_force_field_mode = font.render(f"Particle hold mode: {sim_data[6]}", True, (255,255,255))
        font_force = font.render(f"Force: {sim_data[7]}", True, (255,255,255))
        font_force_field_radius = font.render(f"Force field radius: {sim_data[8]}", True, (255,255,255))
        font_menu_help = font.render(f"--- HELP ---\nM - Particle create multi mode\nD - Particle create static draw mode\nS - Particle create static mode\nG - Particle gravity mode\nT - Particle velocity thermal mode\nP - Pause/Continue simulation\nC - Clear simulation screen\nN - Night mode on/off\nH - Force field mode on/off\n+ Force field radius increase\n- Force field radius decrease\nPRTSCRN - Create sim screenshot\nESC - Exit", True, (255,255,255))
        menu_screen.blit(font_particles, (5, 10))
        menu_screen.blit(font_particle_create_multi_mode, (5, 40))
        menu_screen.blit(font_particle_create_static_draw_mode, (5, 65))
        menu_screen.blit(font_particle_create_static_mode, (5, 90))
        menu_screen.blit(font_particle_gravity_mode, (5, 115))
        menu_screen.blit(font_particle_velocity_thermal_mode, (5, 140))
        menu_screen.blit(font_particle_force_field_mode, (5, 165))
        menu_screen.blit(font_force, (5, 190))
        menu_screen.blit(font_force_field_radius, (5, 215))
        menu_screen.blit(font_menu_help, (5, 250))
        pygame.display.flip()
        clock.tick(60)
        pygame.display.set_caption(f"Euclid 2D")


if __name__ == "__main__":
    # <--- Simulation Screen initializing
    os.environ['SDL_VIDEO_WINDOW_POS'] = "20, 50"
    pygame.init()
    screen_width = 1600
    screen_height = 800
    screen = pygame.display.set_mode((screen_width, screen_height))
    clock = pygame.time.Clock()

    # <--- Menu screen Process and Queue initializing for receiving data from simulation screen
    data_queue = Queue()
    menu_screen_process = Process(target=menu_screen, daemon=True, args=(data_queue,))
    menu_screen_process.start()

    particles = []
    fps_diff = 0
    # <--- Main game engine loop
    while True:
        check_engine_events(particles=particles, screen=screen)
        # <--- Night mode for GUI on/off
        if night_mode:
            screen_bg_colour = (22, 25, 28)
        else:
            screen_bg_colour = (255, 255, 255)

        if engine_is_running == True:
            # <--- Moving, Grid Hashing and Collision
            grid_cell = {}

            for p in particles:
                # <--- Thermal colouring based on particle velocity
                if particle_velocity_thermal_mode:
                    velocity_magnitude = math.sqrt(p.velocity_x**2 + p.velocity_y**2)
                    velocity_normalized = min(velocity_magnitude/10, 1)
                    p.colour[0] = int(255*velocity_normalized)
                    p.colour[1] = 0
                    p.colour[2] = int(255*(1-velocity_normalized))
                p.p_move()
                cell_p = (int(p.pos_x//60), int(p.pos_y//60))
                if cell_p not in grid_cell:
                    grid_cell[cell_p] = []
                grid_cell[cell_p].append(p)

            for cell_particles in grid_cell.values():
                if len(cell_particles) > 1:
                    for i in range(len(cell_particles)):
                        for j in range(i+1, len(cell_particles)):
                            cell_particles[i].p_collide(cell_particles[j])
            # <--- Rendering and Updating
            screen.fill(screen_bg_colour)

            for p in particles:
                p.p_draw(screen)
            if particle_force_field_mode:
                pygame.draw.circle(screen, [0, 128, 0], [pygame.mouse.get_pos()[0], pygame.mouse.get_pos()[1]], force_field_radius, 1)

            pygame.display.flip()
            clock.tick(60)
            # <--- Send data to Menu window process through queue
            data_queue.put([len(particles), particle_create_multi_mode, particle_create_static_draw_mode, particle_create_static_mode, particle_gravity, particle_velocity_thermal_mode, particle_force_field_mode, force, force_field_radius])
            # <--- Simulation window header info
            pygame.display.set_caption(f"Euclid 2D Simulation FPS: {round(clock.get_fps(), 3)}, Max FPS Diff: {round(fps_diff, 3)}% Particles: {len(particles)}")
            # <--- FPS diff info in the Simulation window header
            if clock.get_fps() < 60:
                fps_diff = ((clock.get_fps() - 60)/60)*100
            else:
                fps_diff = 0