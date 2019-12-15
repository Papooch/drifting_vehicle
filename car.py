import pymunk
from pymunk.pyglet_util import DrawOptions
from pymunk.vec2d import Vec2d
import math


def clamp(x, a, b):
   return max(min(b, x), a)


class Rectangle:
   def __init__(self):
      self.body = None
      self.shape = None
      self.color = (0,0,255)

   def get_boundary(self):
      boundary = []
      for v in self.shape.get_vertices():
         x = v.rotated(self.shape.body.angle)[0] + self.shape.body.position[0]
         y = v.rotated(self.shape.body.angle)[1] + self.shape.body.position[1]
         boundary.append((x, y))
      return boundary

class Car(Rectangle):
   def __init__(self, space, vehicle_chasis, tires = None, turn_tires_idx = None, driven_tires_idx = None):
      super(Car, self).__init__()
      self.tires = tires
      self.driven_tires = [tires[i] for i in driven_tires_idx]
      self.turn_tires = [tires[i] for i in turn_tires_idx]
      self.legth = 3
      self.width = 2
      self.weight = 20
      self.wheel_angle = 0
      self.turning_motors = []

      # create pymunk body and add it to the space
      self.body = pymunk.Body(self.weight, 200)
      self.shape = pymunk.Poly(self.body, vehicle_chasis)
      space.add(self.body, self.shape)

      self.color = (150, 0, 0)

      # attach tires to car
      for tire in self.tires:
         constr = pymunk.constraint.PivotJoint(self.body, tire.body, tire.body.local_to_world(tire.body.center_of_gravity))
         constr.collide_bodies = False
         constr.max_force = 1000000
         #constr.max_bias = 1000000
         space.add(constr)

      # affix non turning wheels (gear joint with chasis)
      non_turn_tires_idx = [i for i in range(len(tires)) if i not in turn_tires_idx]
      non_turn_tires = [tires[i] for i in non_turn_tires_idx]
      for tire in non_turn_tires:
         constr = pymunk.constraint.GearJoint(self.body, tire.body, 0, 1)
         space.add(constr)

      # attach turning tires
      for tire in self.turn_tires:
         motor = pymunk.constraint.GearJoint(self.body, tire.body, self.wheel_angle, 1)
         #motor.max_force = 100000
         space.add(motor)
         self.turning_motors.append(motor)


   def drive(self, force):
      for tire in self.driven_tires:
         tire.drive(force)
   
   def turn(self, speed):
      self.wheel_angle += speed/10
      self.wheel_angle = clamp(self.wheel_angle, -math.pi/4, math.pi/4)
      # for tire in self.turn_tires:
      #    tire.turn(force)


   def update(self):

      for motor in self.turning_motors:
         motor.phase = self.wheel_angle

      for tire in self.tires:
         tire.update()


class Tire(Rectangle):
   def __init__(self, space, width=20, radius = 30, position = [0, 0], skid_threshold = 100):
      super(Tire, self).__init__()
      self.width = width
      self.radius = radius
      self.angular_velocity = 0
      self.weight = 2
      self.skid = 0
      self.skidding = False
      self.skid_threshold = skid_threshold
      
      # Create pymunk body and add it to the space
      self.body = pymunk.Body(self.weight, 5)
      self.shape = pymunk.Poly.create_box(self.body, (width, radius*2))
      self.body.position = position

      space.add(self.body, self.shape)

   def turn(self, force):
      self.body.apply_impulse_at_local_point((-force/2, 0), (0, 1))
      self.body.apply_impulse_at_local_point((force/2, 0), (0, -1))

   def drive(self, force):
      force -= self.get_forward_speed()/2
      self.body.apply_force_at_local_point(Vec2d(0, force*10), (0, 0))


   def update(self):
      # Get lateral speed
      lateral_vel = self.get_lateral_speed()

      # Calculate impulse to counteract lateral speed up to certain threshold
      lateral_impulse = -clamp(lateral_vel, -self.skid_threshold, self.skid_threshold)*self.body.mass

      self.skid = lateral_impulse + lateral_vel*self.body.mass
      if abs(self.skid) < 0.00001:
         self.skidding = False
      else:
         self.skidding = True

      # Apply lateral impulse
      self.body.apply_impulse_at_local_point((lateral_impulse, 0), (0, 0))

      # Apply rolling resistance
      forward_vel = self.get_forward_speed()
      self.body.apply_force_at_local_point((0, -clamp(forward_vel*50, -100, 100)), (0, 0))
      #print(forward_vel)

      # Change color depending on the amount of skid
      self.color = (clamp(abs(self.skid)/10, 0, 255), 0, 255)


   def get_forward_speed(self):
      '''Returns the forward speed of the tire'''
      return self.body.velocity.dot(self.body._get_rotation_vector().rotated_degrees(90))

   def get_lateral_speed(self):
      '''Returns the lateral speed of the tire'''
      return self.body.velocity.dot(self.body._get_rotation_vector())