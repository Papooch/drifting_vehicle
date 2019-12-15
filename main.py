import pymunk
import pygame
import math
import car
import graphics


COLOR_WHITE = (255, 255, 255)
COLOR_BLACK = (0, 0, 0)

def draw():
   pass


def main():

   DISPLAY_W = 800
   DISPLAY_H = 600

   dt = 1.0/60
   gamedisplay = pygame.display.set_mode((DISPLAY_W, DISPLAY_H))
   pygame.display.set_caption('Car test')
   clock = pygame.time.Clock()
   surface = pygame.display.get_surface()
   space = pymunk.Space()

   keys = []
   buttons = []

   gfx = graphics.Graphics(gamedisplay)
   gfx.zoom = .2

   tire1 = car.Tire(space, 20, 30, (-50, 30), skid_threshold=100)
   tire2 = car.Tire(space, 20, 30, (50, 30), skid_threshold=100)
   tire3 = car.Tire(space, 20, 30, (-50, -120), skid_threshold=30)
   tire4 = car.Tire(space, 20, 30, (50, -120), skid_threshold=30)
   vehicle_chasis = ((-30, -130), (30, -130), (30, 10), (-30, 10))
   vehicle = car.Car(space, vehicle_chasis, [tire1, tire2, tire3, tire4], [0, 1], [1, 2])

   quit_game = False

   while not quit_game:

      #EVENT HANDLING
      for event in pygame.event.get():
         if event.type == pygame.QUIT:
            quit_game = True
         if event.type == pygame.KEYDOWN:
            keys.append(event.key)
         if event.type == pygame.KEYUP:
            keys.remove(event.key)
         if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 4: #scroll up
               gfx.zoom *= 1.1
            elif event.button == 5: #scroll down
               gfx.zoom *= 1/1.1

         # if event.type == pygame.MOUSEBUTTONUP:
         #    buttons.remove(event.button)
         if event.type == pygame.MOUSEMOTION:
            if event.buttons[0]:
               gfx.center[0] += event.rel[0]
               gfx.center[1] += event.rel[1]
         #print(event)
      # end for event

      #GAME LOGIC
      if pygame.K_ESCAPE in keys:
         quit_game = True
      if pygame.K_UP in keys:
         vehicle.drive(1200)
      if pygame.K_DOWN in keys:
         vehicle.drive(-1200)
      if pygame.K_LEFT in keys:
         vehicle.turn(1)
      if pygame.K_RIGHT in keys:
         vehicle.turn(-1)


      #DRAWING GRAPHICS
      gamedisplay.fill(COLOR_BLACK)
      vehicle.update()

      dt_divider = 1
      for _ in range(dt_divider):
         space.step(dt*dt_divider)
      gfx.draw(vehicle)
      gfx.draw_text(f'Speed: {round(tire1.get_forward_speed(), 2)}', (20, 30))
      pygame.display.update()
      clock.tick(60)

   #end while not quit_game
   pygame.quit()
   quit()


if __name__ == "__main__":
   main()