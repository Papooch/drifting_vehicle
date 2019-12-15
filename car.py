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
   def __init__(self, space, tires = None, turn_tires_idx = None, driven_tires_idx = None):
      self.tires = tires
      self.driven_tires = [tires[i] for i in driven_tires_idx]
      self.turn_tires = [tires[i] for i in turn_tires_idx]
      self.legth = 3
      self.width = 2
      self.weight = 1000

   def drive(self, force):
      for tire in self.driven_tires:
         tire.drive(force)
   
   def turn(self, force):
      for tire in self.turn_tires:
         tire.turn(force)


   def update(self):
      for tire in self.tires:
         tire.update()


class Tire(Rectangle):
   def __init__(self, space, width=20, radius = 30, position = [0, 0]):
      super(Tire, self).__init__()
      self.width = width
      self.radius = radius
      self.angular_velocity = 0
      self.weight = 10
      self.skidding = False
      
      # Create pymunk body and add it to the space
      self.body = pymunk.Body(self.weight, pymunk.moment_for_box(self.weight, (width, radius*2)))
      self.shape = pymunk.Poly.create_box(self.body, (width, radius*2))
      self.body.position = position

      space.add(self.body, self.shape)

   def turn(self, force):
      self.body.apply_impulse_at_local_point((-force/2, 0), (0, 1))
      self.body.apply_impulse_at_local_point((force/2, 0), (0, -1))

   def drive(self, force):
      self.body.apply_impulse_at_local_point(Vec2d(0, force), (0, 0))


   def update(self):
      #self.body.apply_force_at_local_point(Vec2d(0, -clamp(self.body.velocity.get_length()*500, -1000, 1000)), (0, 0))
      # if self.body.velocity.get_length() < .01:
      #    self.body.velocity = (0, 0)
      #print(self.get_boundary())
      #print(self.body._get_rotation_vector())

      # Apply rolling resistance
      forward_vel = self.get_forward_speed()
      self.body.apply_force_at_local_point((0, -clamp(forward_vel*500, -1000, 1000)), (0, 0))
      #print(forward_vel)

      # Apply Skidding
      lateral_vel = self.get_lateral_speed()
      lateral_impulse = -clamp(lateral_vel, -20, 20)*self.body.mass

      skid = lateral_impulse + lateral_vel*self.body.mass
      if abs(skid) < 0.00001:
         self.skidding = False
      else:
         self.skidding = True
      self.body.apply_impulse_at_local_point((lateral_impulse, 0), (0, 0))

      # Apply turning resistance
      self.turn(-clamp(self.body.angular_velocity*100, -1000, 1000))

      # Change color depending on the amount of skid
      self.color = (clamp(abs(skid)/10, 0, 255), 0, 255)


   def get_forward_speed(self):
      '''Returns the forward speed of the tire'''
      return self.body.velocity.dot(self.body._get_rotation_vector().rotated_degrees(90))

   def get_lateral_speed(self):
      '''Returns the lateral speed of the tire'''
      return self.body.velocity.dot(self.body._get_rotation_vector())