import pygame as pg
import sys
import numpy as np
import scipy.signal
pg.init()

WIDTH = 1280
HEIGHT = 800
FONT = pg.font.SysFont("Arial", 18, bold=True)


class Animation:
	def __init__(self):
		self.screen = pg.display.set_mode((WIDTH, HEIGHT))
		pg.display.set_caption("Slime")
		self.clock = pg.time.Clock()
		self.alpha_surf = pg.Surface(self.screen.get_size(), pg.SRCALPHA)
		self.surf = np.empty((WIDTH, HEIGHT, 3))
		self.kernel = np.ones((3, 3), float) / 9.5
		self.slime_group = pg.sprite.Group()

	def run(self):
		slimes = {}
		for i in range(1500):
			slimes[i] = Slime((np.random.randint(WIDTH), np.random.randint(HEIGHT)), self.slime_group)

		while True:
			for event in pg.event.get():
				if event.type == pg.QUIT:
					pg.quit()
					sys.exit()

			self.alpha_surf.fill((255, 255, 255, 230), special_flags=pg.BLEND_RGBA_MULT)
			self.clock.tick(30)
			self.screen.fill("black")

			Slime.array = pg.surfarray.array3d(self.alpha_surf)

			for slime in slimes.values():
				slime.turn()
			self.slime_group.update()
			for slime in self.slime_group:
				pg.draw.rect(self.alpha_surf, (255, 255, 255), slime)
			self.update_screen()
			self.screen.blit(self.alpha_surf, (0, 0))
			self.fps_counter()
			pg.display.update()
			

	def update_screen(self):
		self.surf[:, :, :] = scipy.signal.convolve2d(
								pg.surfarray.array3d(self.alpha_surf)[:, :, 0],
								self.kernel, mode="same", boundary="fill").reshape(WIDTH, HEIGHT, 1)
		
		self.alpha_surf.blit(pg.surfarray.make_surface(self.surf), (0, 0))

	def fps_counter(self):
		fps = str(int(self.clock.get_fps()))
		fps_t = FONT.render(fps, True, pg.Color("RED"))
		self.screen.blit(fps_t, (0, 0))


class Slime(pg.sprite.Sprite):
	array = None
	turn_speed = 10
	delta_time = 1
	sensor_offset_distance = 35
	sensor_size = 1
	sense_weight = 3.0

	def __init__(self, pos, group):
		super().__init__(group)
		self.image = pg.Surface((2, 2), pg.SRCALPHA)
		self.rect = self.image.get_rect(center=pos)
		self.direction = pg.math.Vector2()
		self.pos = pg.math.Vector2(pos)
		self.randomize_direction()
		self.speed = 5

	def randomize_direction(self):
		self.direction.x = np.random.randint(-100, 100)
		self.direction.y = np.random.randint(-100, 100)
		if self.direction.magnitude() != 0:
			self.direction = self.direction.normalize()
		self.angle = self.direction.as_polar()[1]

	@staticmethod
	def sense(slime, angle_offset):
		sensor_angle = slime.angle + angle_offset
		sensor_direction = pg.math.Vector2(1, 0).rotate(sensor_angle)

		sensor_position = pg.math.Vector2(slime.pos + sensor_direction * Slime.sensor_offset_distance)
		sensor_x = int(sensor_position.x)
		sensor_y = int(sensor_position.y)

		sum = 0
		for offset_x in range(-Slime.sensor_size, Slime.sensor_size+1):
			for offset_y in range(-Slime.sensor_size, Slime.sensor_size + 1):
				sample_x = min(WIDTH-1, max(0, sensor_x + offset_x))
				sample_y = min(HEIGHT-1, max(0, sensor_y + offset_y))
				sum += Slime.sense_weight * Slime.array[sample_x, sample_y, 0]
		return sum

	def turn(self):
		weight_forward = self.sense(self, 0)
		weight_left = self.sense(self, 90)
		weight_right = self.sense(self, -90)
		random_steer = np.random.uniform()
		turning_speed = Slime.turn_speed * 2 * 3.1415

		# Continue forward
		if weight_forward >= weight_left and weight_forward >= weight_right:
			self.direction = self.direction.rotate(0)
		elif weight_forward < weight_left and weight_forward < weight_right:
			self.direction = self.direction.rotate((random_steer - 0.5) * 2 * turning_speed * Slime.delta_time)
		elif weight_right > weight_left:
			self.direction = self.direction.rotate(-random_steer * turning_speed * Slime.delta_time)
		elif weight_right < weight_left:
			self.direction = self.direction.rotate(random_steer * turning_speed * Slime.delta_time)
		self.angle = self.direction.as_polar()[1]

	def update(self):
		self.pos += self.direction * self.speed
		self.rect.center = self.pos
		self.collision()

	def collision(self):
		if self.rect.centerx > WIDTH:
			self.rect.centerx = WIDTH
			self.randomize_direction()
		if self.rect.centerx < 0:
			self.rect.centerx = 0
			self.randomize_direction()
		if self.rect.centery > HEIGHT:
			self.rect.centery = HEIGHT
			self.randomize_direction()
		if self.rect.centery < 0:
			self.rect.centery = 0
			self.randomize_direction()


a = Animation()
a.run()