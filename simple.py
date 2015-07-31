import sys

# GFX imports
#
from glfw import *
import pygloo
from pygloo import *

# Math
#
from math import *
import random
import numpy as np

from geometry import Geometry, mat4


gl = None
test_model = None


model_rotate_x = 0
model_rotate_y = 0

mouse_xpos = 0
mouse_ypos = 0

def on_key(window, key, scancode, action, mods):
	if key == GLFW_KEY_ESCAPE and action == GLFW_PRESS:
		glfwSetWindowShouldClose(window, 1)

def on_mouse(window, button, action, mods):
	pass
	

def on_mouse_move(window, xpos, ypos):
	global model_rotate_x
	global model_rotate_y
	global mouse_xpos
	global mouse_ypos
	
	rstate = glfwGetMouseButton(window, GLFW_MOUSE_BUTTON_LEFT)
	if rstate == GLFW_PRESS:
		model_rotate_y += pi*(mouse_xpos - xpos)/180
		model_rotate_x += pi*(mouse_ypos - ypos)/180
		model_rotate_x = min(max(model_rotate_x, -pi/2),pi/2)

	mouse_xpos = xpos
	mouse_ypos = ypos




def render(w,h):
	global gl
	global test_model
	global model_rotate_x
	global model_rotate_y

	zfar = 1000
	znear = 0.1

	camera = np.dot(mat4.rotateY(model_rotate_y), np.dot(mat4.rotateX(model_rotate_x), mat4.translate(0,0,10)))
	mv = np.linalg.inv(camera)
	proj = mat4.perspectiveProjection(pi / 3, float(w)/h, znear, zfar)

	test_model.render(gl, mv, proj, wireframe=True)


def main():
	global gl
	global test_model

	# Initialize the library
	if not glfwInit():
		sys.exit()

	# Initilize GL
	gl = pygloo.init()
	if not gl:
		sys.exit()


	# Create a windowed mode window and its OpenGL context
	window = glfwCreateWindow(640, 480, "Hello World", None, None)
	if not window:
		glfwTerminate()
		sys.exit()

	# Make the window's context current
	glfwMakeContextCurrent(window)

	# Install a input handlers
	glfwSetKeyCallback(window, on_key)
	glfwSetMouseButtonCallback(window, on_mouse)
	glfwSetCursorPosCallback(window, on_mouse_move)



	# Load an obj
	#
	test_model = Geometry.from_OBJ(gl, "assets/sphere.obj")


	# Loop until the user closes the window
	while not glfwWindowShouldClose(window):

		# Render
		width, height = glfwGetFramebufferSize(window)
		gl.glViewport(0, 0, width, height)

		gl.glBindFramebuffer(GL_DRAW_FRAMEBUFFER, 0);
		gl.glClearColor(1.0, 1.0, 1.0, 1.0) # white
		gl.glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
		gl.glEnable(GL_DEPTH_TEST);
		# gl.glDepthFunc(GL_LESS);
		gl.glDepthFunc(GL_LEQUAL);

		# Render
		#
		render(width, height)

		# Poll for and process events
		glfwPollEvents()

		# Swap front and back buffers
		glfwSwapBuffers(window)

	glfwTerminate()


if __name__ == '__main__':
	main()

