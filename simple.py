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

from geometry import Geometry, mat4, _flatten_list


gl = None
test_model = None

model_distance = 10
model_rotate_x = 0
model_rotate_y = 0

mouse_xpos = 0
mouse_ypos = 0

mouse_down_xpos = 0
mouse_down_ypos = 0

class Action:
    none, select, add_select, camera, translate, rotate = range(6)

user_action = Action.none



def on_key(window, key, scancode, action, mods):
	global test_model

	if action is GLFW_PRESS:
		if key is GLFW_KEY_ESCAPE:
			glfwSetWindowShouldClose(window, 1)

		if key is GLFW_KEY_C:
			test_model.constrained = list(set(test_model.constrained + test_model.selected))

		if key is GLFW_KEY_X:
			test_model.constrained = [i for i in test_model.constrained if i not in test_model.selected]



def on_mouse(window, button, action, mods):
	global user_action
	global test_model
	global mouse_xpos
	global mouse_ypos
	global mouse_down_xpos
	global mouse_down_ypos

	if button is GLFW_MOUSE_BUTTON_LEFT:
		if (user_action in [Action.select, Action.add_select, Action.translate]) and action is GLFW_RELEASE:
			if user_action in [Action.select, Action.add_select]:

				# do the selection
				w, h = glfwGetFramebufferSize(window)
				x1 = (2*mouse_xpos/w)-1
				x2 = (2*mouse_down_xpos/w)-1
				y1 = -((2*mouse_ypos/h)-1)
				y2 = -((2*mouse_down_ypos/h)-1)

				xmin = min(x1, x2)
				ymin = min(y1, y2)
				xmax = max(x1, x2)
				ymax = max(y1, y2)

				screen_mat = np.dot(get_projmatrix(w, h), get_viewmatrix())
				screen_vert = [[v[0]/v[3], v[1]/v[3], v[2]/v[3]] for v in
					[np.dot(screen_mat, [v[0], v[1], v[2], 1.0]) for v in test_model.verts]]
				screen_select = [i for i in range(len(screen_vert)) if
					screen_vert[i][0] > xmin and screen_vert[i][0] < xmax and
					screen_vert[i][1] > ymin and screen_vert[i][1] < ymax]

				if user_action is Action.select:
					test_model.selected = screen_select
				else:
					test_model.selected = list(set(test_model.selected + screen_select))

			user_action = Action.none

		elif user_action is Action.none and action is GLFW_PRESS:
			if glfwGetKey(window, GLFW_KEY_LEFT_CONTROL) is GLFW_PRESS:
				user_action = Action.translate
			else:
				user_action = Action.add_select if glfwGetKey(window, GLFW_KEY_LEFT_SHIFT) is GLFW_PRESS else Action.select
				mouse_down_xpos = mouse_xpos
				mouse_down_ypos = mouse_ypos


	elif button is GLFW_MOUSE_BUTTON_RIGHT:
		if (user_action in [Action.camera, Action.rotate]) and action is GLFW_RELEASE:
			user_action = Action.none

		elif user_action is Action.none and action is GLFW_PRESS:
			if glfwGetKey(window, GLFW_KEY_LEFT_CONTROL) is GLFW_PRESS:
				user_action = Action.rotate
			else:
				user_action = Action.camera



def on_scroll(window, xoffset, yoffset):
	global model_distance
	model_distance = max(model_distance * (1.0 - (0.1 * yoffset)), 0)



def on_mouse_move(window, xpos, ypos):
	global model_rotate_x
	global model_rotate_y
	global mouse_xpos
	global mouse_ypos
	global user_action

	if user_action is Action.select:
		pass

	elif user_action is Action.camera:
		model_rotate_y += pi*(mouse_xpos - xpos)/180
		model_rotate_x += pi*(mouse_ypos - ypos)/180
		model_rotate_x = min(max(model_rotate_x, -pi/2),pi/2)

	elif user_action is Action.translate:
		pass

	elif user_action is Action.rotate:
		pass

	mouse_xpos = xpos
	mouse_ypos = ypos



def render(w,h):
	global gl
	global test_model
	global model_rotate_x
	global model_rotate_y
	global user_action

	# render model
	test_model.update(gl)
	test_model.render(gl, get_viewmatrix(), get_projmatrix(w,h), wireframe=True)

	# Draw the seelection box
	if user_action in [Action.select, Action.add_select]:
		gl.glUseProgram(Geometry.flat_shader)
		i = pygloo.c_array(GLfloat, _flatten_list(mat4.identity()))
		gl.glUniformMatrix4fv(gl.glGetUniformLocation(Geometry.flat_shader, "modelViewMatrix"), 1, True, i)
		gl.glUniformMatrix4fv(gl.glGetUniformLocation(Geometry.flat_shader, "projectionMatrix"), 1, True, i)
		gl.glUniform3fv(gl.glGetUniformLocation(Geometry.flat_shader, "color"), 1, pygloo.c_array(GLfloat, [0.0, 0.0, 0.0]))

		global mouse_xpos
		global mouse_ypos
		global mouse_down_xpos
		global mouse_down_ypos

		x1 = (2*mouse_xpos/w)-1
		x2 = (2*mouse_down_xpos/w)-1
		y1 = -((2*mouse_ypos/h)-1)
		y2 = -((2*mouse_down_ypos/h)-1)

		gl.glColor3f(0.1, 0.1, 0.1);
		gl.glBegin(GL_LINE_LOOP)
		gl.glVertex3f( x1, y1, 0.0)
		gl.glVertex3f( x1, y2, 0.0)
		gl.glVertex3f( x2, y2, 0.0)
		gl.glVertex3f( x2, y1, 0.0)
		gl.glEnd()



def get_viewmatrix():
	camera = np.dot(mat4.rotateY(model_rotate_y), np.dot(mat4.rotateX(model_rotate_x), mat4.translate(0,0,model_distance)))
	return np.linalg.inv(camera)



def get_projmatrix(w, h):
	zfar = 1000
	znear = 0.1
	return mat4.perspectiveProjection(pi / 3, float(w)/h, znear, zfar)



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
	glfwSetScrollCallback(window, on_scroll)



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

