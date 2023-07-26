# particles/wave.py

import pymunk
import uuid
from scenes.constants import WAVE_LAYER, WAVE_COLLISION, MOLECULES_LAYER


class Wave:
    def __init__(self, game_scene, space, radius, impulse_strength, velocity=(0, 0), position=(0, 0)):
        self.id = uuid.uuid4()

        self.radius = radius
        self.game_scene = game_scene
        self.impulse_strength = impulse_strength
        self.space = space
        self.position = position

        moment = pymunk.moment_for_circle(1, 0, radius)
        self.body = pymunk.Body(1, moment, pymunk.Body.KINEMATIC)
        self.body.position = position
        self.body.velocity = pymunk.Vec2d(*velocity)
        self.rate = 1
        self.influenced_molecules = []
        self.body.wave = self

        self.shape = pymunk.Circle(self.body, radius)
        self.shape.sensor = True  # set shape as a sensor to avoid physical collision
        self.shape.collision_type = WAVE_COLLISION
        self.shape.filter = pymunk.ShapeFilter(categories=WAVE_LAYER, mask=MOLECULES_LAYER)
        self.influence_range = 10

        space.add(self.body, self.shape)

    def update_physics(self, dt):
        """This can be used to update the wave, like making it move, grow, or disappear"""
        # Define constants for wave's growth rate and slowdown rate
        GROWTH_RATE = 100  # The amount of pixels the wave grows per second
        SLOWDOWN_RATE = 0.98  # The fraction of current speed the wave maintains per second

        # Slow the wave down
        self.rate *= 1 - (1 - SLOWDOWN_RATE) * dt

        # Apply the rate to all components that need to be slowed down
        self.body.velocity *= self.rate
        self.impulse_strength *= self.rate
        self.influence_range *= self.rate

        # Make the wave grow
        self.radius += GROWTH_RATE * dt  # Now this is per second and frame-rate independent

        # Change the shape's radius to match
        self.shape.unsafe_set_radius(self.radius)

        # Define thresholds for removing the wave
        VELOCITY_THRESHOLD = 0.1
        IMPULSE_THRESHOLD = 1

        # Check if the wave should be removed
        if abs(self.body.velocity.x) < VELOCITY_THRESHOLD and abs(
                self.body.velocity.y) < VELOCITY_THRESHOLD or self.impulse_strength < IMPULSE_THRESHOLD:
            self.remove()

    def remove(self):
        """Remove the wave from the game and reset the wave of all molecules it was influencing"""
        self.space.remove(self.body, self.shape)
        self.influenced_molecules.clear()
        self.game_scene.waves_active.remove(self)


    @staticmethod
    def setup_wave_collision(wave_collision_handler):
        MAX_IMPULSE = 1000  # Adjust this as needed

        def begin(arbiter, space, data):
            wave_shape, molecule_shape = arbiter.shapes
            wave = wave_shape.body.wave
            molecule = molecule_shape.body.molecule

            # Calculate direction and distance from the wave to the molecule
            diff = molecule.body.position - wave.body.position
            direction = diff.normalized()
            distance = diff.length

            # Only apply the impulse if the molecule is within a certain range of the wave's edge
            # and the molecule hasn't been influenced by this wave yet
            if wave.radius - 5 <= distance <= wave.radius + 5 and molecule not in wave.influenced_molecules:
                # Calculate the impulse
                impulse = direction * wave.impulse_strength
                # Limit the maximum impulse
                if impulse.length > MAX_IMPULSE:
                    impulse = impulse.normalized() * MAX_IMPULSE

                molecule.set_impulse_wave(impulse)
                # Add the molecule to the list of influenced molecules
                wave.influenced_molecules.append(molecule)

            return False

        wave_collision_handler.begin = begin
