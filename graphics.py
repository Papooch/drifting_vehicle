import pygame
import math
import car

class Graphics:
   def __init__(self, window):
      self.window = window
      self.center = [0, 0]
      self.zoom = 1
      pygame.font.init() 
      self.font = pygame.font.Font(pygame.font.get_default_font(), 12)
      #(window.get_width()/2, window.get_height()/2)

   def draw(self, obj):
      if isinstance(obj, car.Car):
         for tire in obj.tires:
            self.draw(tire)

      if isinstance(obj, car.Rectangle):
         boundary = obj.get_boundary()
         polygon = []
         for v in boundary:
            x = v[0]*self.zoom + self.center[0] + self.window.get_width()/2
            y = -v[1]*self.zoom + self.center[1] + self.window.get_height()/2
            polygon.append((x, y))
         pygame.draw.polygon(self.window, obj.color, polygon)

         if isinstance(obj, car.Tire):
            if obj.skidding:
               pygame.draw.lines(self.window, (255, 0, 0), True, polygon)

   def draw_text(self, text, position = (0, 0), color = (255, 255, 255)):
      text_surface = self.font.render(text, True, color)
      self.window.blit(text_surface, position)
