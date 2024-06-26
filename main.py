import pygame
import pymunk
import pymunk.pygame_util
import math

pygame.init()
info = pygame.display.Info()
WIDTH, HEIGHT = info.current_w, info.current_h
window = pygame.display.set_mode((WIDTH, HEIGHT), pygame.FULLSCREEN)


def draw(space, window, draw_options, line, font, text_surface):
    window.fill('#DFB8F2')

    text_width, text_height = text_surface.get_size()
    window.blit(text_surface, ((WIDTH - text_width) // 2, 50))

    if line:
        pygame.draw.line(window, (96, 62, 115, 45), line[0], line[1], 3)

    space.debug_draw(draw_options)

    pygame.display.update()


def calculate_distance(p1, p2):
    return math.sqrt((p2[1] - p1[1]) ** 2 + (p2[0] - p1[0]) ** 2)


def calculate_angle(p1, p2):
    return math.atan2(p2[1] - p1[1], p2[0] - p1[0])


def create_boundaries(space, width, height):
    rects = [
        [(width / 2, height), (width, 0)],
        [(width / 2, 0), (width, 0)],
        [(0, height / 2), (0, height)],
        [(width, height / 2), (0, height)],
    ]

    for pos, size in rects:
        body = pymunk.Body(body_type=pymunk.Body.STATIC)
        body.position = pos

        shape = pymunk.Poly.create_box(body, size)
        shape.elasticity = 0.4
        shape.friction = 0.5

        space.add(body, shape)


def create_structure(space, width, height):
    COLOR = (11, 154, 157, 62)

    rects = [
        [(600, height - 120), (40, 200), COLOR, 100],
        [(900, height - 120), (40, 200), COLOR, 100],
        [(750, height - 240), (340, 40), COLOR, 150]
    ]

    for pos, size, color, mass in rects:
        body = pymunk.Body()
        body.position = pos

        shape = pymunk.Poly.create_box(body, size)
        shape.color = color
        shape.mass = mass
        shape.elasticity = 0.4
        shape.friction = 0.4

        space.add(body, shape)


def create_pendulum(space):
    rotation_center_body = pymunk.Body(body_type=pymunk.Body.STATIC)
    rotation_center_body.position = (1000, 200)

    body = pymunk.Body()
    body.position = (1000, 300)

    line = pymunk.Segment(body, (0, 0), (255, 0), 5)
    line.color = (229, 242, 184, 95)
    circle = pymunk.Circle(body, 40, (255, 0))
    circle.color = (229, 242, 184, 95)

    line.friction = 1
    circle.friction = 1
    line.mass = 8
    circle.mass = 30
    circle.elasticity = 0.95

    rotation_center_joint = pymunk.PinJoint(body, rotation_center_body,
                                            (0, 0), (0, 0))
    space.add(circle, line, body, rotation_center_joint)


def create_static_ball(space):
    body = pymunk.Body(1, 100, body_type=pymunk.Body.STATIC)
    body.position = (300, 300)

    shape = pymunk.Circle(body, 50)
    shape.elasticity = 0.2
    shape.friction = 2
    shape.color = (157, 130, 111, 62)

    space.add(body, shape)


def create_ball(space, radius, mass, pos):
    body = pymunk.Body(body_type=pymunk.Body.STATIC)
    body.position = pos

    shape = pymunk.Circle(body, radius)
    shape.mass = mass
    shape.elasticity = 0.9
    shape.friction = 0.4
    shape.color = (180, 239, 242, 95)

    space.add(body, shape)

    return shape


def run(window, width, height):
    running = True
    clock = pygame.time.Clock()
    fps = 240
    dt = 1 / fps

    space = pymunk.Space()
    space.gravity = (0, 981)

    create_boundaries(space, width, height)
    create_structure(space, width, height)
    create_pendulum(space)
    create_static_ball(space)

    draw_options = pymunk.pygame_util.DrawOptions(window)

    pressed_pos = None
    ball = None
    simulate = True

    font = pygame.font.Font(None, 36)
    text_surface = font.render(
        'Click to place a ball. '
        'Drag to apply the force. '
        'Click to launch the ball. '
        'Click again to delete the ball. [Space] to pause. [Q] ot quit.',
        True, '#613E73')

    while running:
        line = None
        if ball and pressed_pos:
            line = [pressed_pos, pygame.mouse.get_pos()]

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                break

            if event.type == pygame.MOUSEBUTTONDOWN:
                if not ball:
                    pressed_pos = pygame.mouse.get_pos()
                    ball = create_ball(space, 30, 10, pressed_pos)
                elif pressed_pos:
                    ball.body.body_type = pymunk.Body.DYNAMIC

                    angle = calculate_angle(*line)
                    force = calculate_distance(*line) * 50
                    fx = math.cos(angle) * force
                    fy = math.sin(angle) * force

                    ball.body.apply_impulse_at_local_point((-fx, -fy), (0, 0))
                    pressed_pos = None
                else:
                    space.remove(ball, ball.body)
                    ball = None

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_q:
                    running = False
                    break

                if event.key == pygame.K_SPACE:
                    simulate = not simulate

        draw(space, window, draw_options, line, font, text_surface)
        if simulate:
            space.step(dt)
        clock.tick(fps)

    pygame.quit()


if __name__ == "__main__":
    run(window, WIDTH, HEIGHT)
