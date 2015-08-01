

# GFX imports
#
import pygloo
from pygloo import *
from ctypes import *
from simpleShader import makeProgram


# Math
#
from math import *
import random
import numpy as np

def _flatten_list(l):
	return [e for row in l for e in row]


class Geometry(object):
	solid_shader = GLuint(0)
	wire_shader = GLuint(0)
	flat_shader = GLuint(0)

	def __init__(self, gl, v=[], vtf=[], f=[]):
		if not Geometry.solid_shader:
			Geometry.solid_shader = makeProgram(gl, "330 core", [GL_VERTEX_SHADER, GL_GEOMETRY_SHADER, GL_FRAGMENT_SHADER],
				open("shaders/solid_shader.glsl").read())

		if not Geometry.wire_shader:
			Geometry.wire_shader = makeProgram(gl, "330 core", [GL_VERTEX_SHADER, GL_GEOMETRY_SHADER, GL_FRAGMENT_SHADER],
				open("shaders/wireframe_shader.glsl").read())

		if not Geometry.flat_shader:
			Geometry.flat_shader = makeProgram(gl, "330 core", [GL_VERTEX_SHADER, GL_FRAGMENT_SHADER],
				open("shaders/flat_color_shader.glsl").read())



		self.verts = v
		self.vertToFaces = vtf
		self.faces = f
		self.selected = []
		self.constrained = []


		# Creating the VAO and VBO(s) for mesh
		# 
		self.vao = GLuint(0)
		gl.glGenVertexArrays(1, self.vao)
		gl.glBindVertexArray(self.vao)

		# Index IBO
		idx_array = pygloo.c_array(GLuint, _flatten_list(self.faces))
		self.ibo = GLuint(0)
		self.ibo_size = len(idx_array)
		gl.glGenBuffers(1, self.ibo)
		gl.glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, self.ibo);
		gl.glBufferData(GL_ELEMENT_ARRAY_BUFFER, sizeof(idx_array), idx_array, GL_STATIC_DRAW);

		# Vertex Position VBO
		self.vbo_pos = GLuint(0)
		gl.glGenBuffers(1, self.vbo_pos)
		gl.glBindVertexArray(0)



		# Creating the VAO(s) for selected/constrained points
		#

		# Selected
		self.vao_selected = GLuint(0)
		gl.glGenVertexArrays(1, self.vao_selected)
		gl.glBindVertexArray(self.vao_selected)

		self.ibo_selected = GLuint(0)
		gl.glGenBuffers(1, self.ibo_selected)

		# Constrained
		self.vao_constrained = GLuint(0)
		gl.glGenVertexArrays(1, self.vao_constrained)
		gl.glBindVertexArray(self.vao_constrained)

		self.ibo_constrained = GLuint(0)
		gl.glGenBuffers(1, self.ibo_constrained)



		# Make the update
		self.update(gl)



	# Because we are going to be changing the positions of the verticies alot
	# as well as the selected/constrained points, this is a helper method that
	# is run occasionally
	def update(self, gl):
		
		# Update vertex position information
		#
		gl.glBindVertexArray(self.vao)

		# Vertex Position VBO  (pos 0)
		pos_array = pygloo.c_array(GLfloat, _flatten_list(self.verts))
		gl.glBindBuffer(GL_ARRAY_BUFFER, self.vbo_pos)
		gl.glBufferData(GL_ARRAY_BUFFER, sizeof(pos_array), pos_array, GL_STREAM_DRAW)
		gl.glEnableVertexAttribArray(0)
		gl.glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, 0, 0)


		# Update Selected/Constrained information
		# 
		gl.glBindVertexArray(self.vao_selected)
		idx_array = pygloo.c_array(GLuint, self.selected)
		gl.glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, self.ibo_selected);
		gl.glBufferData(GL_ELEMENT_ARRAY_BUFFER, sizeof(idx_array), idx_array, GL_STREAM_DRAW);

		gl.glBindBuffer(GL_ARRAY_BUFFER, self.vbo_pos)
		gl.glEnableVertexAttribArray(0)
		gl.glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, 0, 0)


		gl.glBindVertexArray(self.vao_constrained)
		idx_array = pygloo.c_array(GLuint, self.constrained)
		gl.glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, self.ibo_constrained);
		gl.glBufferData(GL_ELEMENT_ARRAY_BUFFER, sizeof(idx_array), idx_array, GL_STREAM_DRAW);

		gl.glBindBuffer(GL_ARRAY_BUFFER, self.vbo_pos)
		gl.glEnableVertexAttribArray(0)
		gl.glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, 0, 0)

		# Cleanup
		gl.glBindVertexArray(0)







	def render(self, gl, mv, proj, wireframe=False):

		# Render Model
		# 
		gl.glUseProgram(Geometry.solid_shader)
		gl.glBindVertexArray(self.vao)
		
		gl.glUniformMatrix4fv(gl.glGetUniformLocation(Geometry.solid_shader, "modelViewMatrix"), 1, True, pygloo.c_array(GLfloat, _flatten_list(mv)))
		gl.glUniformMatrix4fv(gl.glGetUniformLocation(Geometry.solid_shader, "projectionMatrix"), 1, True, pygloo.c_array(GLfloat, _flatten_list(proj)))

		gl.glDrawElements(GL_TRIANGLES, self.ibo_size, GL_UNSIGNED_INT, 0)
		gl.glBindVertexArray(0)


		if wireframe:
			# Render
			# 
			gl.glEnable(GL_LINE_SMOOTH)
			gl.glUseProgram(Geometry.wire_shader)
			gl.glBindVertexArray(self.vao)
			
			gl.glUniformMatrix4fv(gl.glGetUniformLocation(Geometry.wire_shader, "modelViewMatrix"), 1, True, pygloo.c_array(GLfloat, _flatten_list(mv)))
			gl.glUniformMatrix4fv(gl.glGetUniformLocation(Geometry.wire_shader, "projectionMatrix"), 1, True, pygloo.c_array(GLfloat, _flatten_list(proj)))

			gl.glDrawElements(GL_TRIANGLES, self.ibo_size, GL_UNSIGNED_INT, 0)
			gl.glBindVertexArray(0)



		# Render selected and constrained points
		#
		gl.glPointSize(5.0)

		gl.glUseProgram(Geometry.flat_shader)
		gl.glBindVertexArray(self.vao_selected)
		gl.glUniform3fv(gl.glGetUniformLocation(Geometry.flat_shader, "color"), 1, pygloo.c_array(GLfloat, [1.0, 1.0, 0.0]))

		
		gl.glUniformMatrix4fv(gl.glGetUniformLocation(Geometry.flat_shader, "modelViewMatrix"), 1, True, pygloo.c_array(GLfloat, _flatten_list(mv)))
		gl.glUniformMatrix4fv(gl.glGetUniformLocation(Geometry.flat_shader, "projectionMatrix"), 1, True, pygloo.c_array(GLfloat, _flatten_list(proj)))

		gl.glDrawElements(GL_POINTS, len(self.selected), GL_UNSIGNED_INT, 0)


		gl.glBindVertexArray(self.vao_constrained)
		gl.glUniform3fv(gl.glGetUniformLocation(Geometry.flat_shader, "color"), 1, pygloo.c_array(GLfloat, [1.0, 0.0, 0.0]))

		gl.glDrawElements(GL_POINTS, len(self.constrained), GL_UNSIGNED_INT, 0)
		gl.glBindVertexArray(0)








	@staticmethod
	def from_OBJ(gl, s):
		verts = []
		vertToFaces = []
		faces = []
		for line in open(s, "r"):
			vals = line.split()
			if len(vals) > 0:
				if vals[0] == "v":
					v = map(float, vals[1:4])
					verts.append(v)
					vertToFaces.append([])
				elif vals[0] == "f":
					f = map(lambda x : int(x.split("/")[0])-1, vals[1:4])
					map(lambda x : vertToFaces[x].append(len(faces)), f)
					faces.append(f)
		return Geometry(gl, verts, vertToFaces, faces)



class mat4:
	@staticmethod
	def identity():
		return np.asarray([
			[1, 0, 0, 0,],
			[0, 1, 0, 0,],
			[0, 0, 1, 0,],
			[0, 0, 0, 1]])

	@staticmethod
	def translate(tx, ty, tz):
		return np.asarray([
			[1, 0, 0, tx,],
			[0, 1, 0, ty,],
			[0, 0, 1, tz,],
			[0, 0, 0, 1]])

	@staticmethod
	def scale(sx, sy, sz):
		return np.asarray([
			[sx, 0, 0, 0,],
			[0, sy, 0, 0,],
			[0, 0, sz, 0,],
			[0, 0, 0, 1]])

	@staticmethod
	def rotateX(a):
		return np.asarray([
			[1,		0,		0,		0,],
			[0,		cos(a),	-sin(a),0,],
			[0,		sin(a),	cos(a),	0,],
			[0,		0,		0,		1]])

	@staticmethod
	def rotateY(a):
		return np.asarray([
			[cos(a),0,		sin(a),	0,],
			[0,		1,		0,		0,],
			[-sin(a),0,		cos(a),	0,],
			[0,		0,		0,		1]])

	@staticmethod
	def rotateZ(a):
		return np.asarray([
			[cos(a),	-sin(a),0,		0,],
			[sin(a),	cos(a),	0,		0,],
			[0,		0,		1,		0,],
			[0,		0,		0,		1]])

	@staticmethod
	def perspectiveProjection(fovy, aspect, zNear, zFar):
		f = cos(fovy / 2) / sin(fovy / 2);

		return np.asarray([
			[f / aspect,0,		0,		0,],
			[0,			f,		0,		0,],
			[0,			0,		(zFar + zNear) / (zNear - zFar),	(2 * zFar * zNear) / (zNear - zFar),],
			[0,			0,		-1,		0]])