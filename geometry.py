

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
	geo_shader = GLuint(0)
	wire_shader = GLuint(0)

	def __init__(self, gl, v=[], vtf=[], f=[]):
		if not Geometry.geo_shader:
			Geometry.geo_shader = makeProgram(gl, "330 core", [GL_VERTEX_SHADER, GL_GEOMETRY_SHADER, GL_FRAGMENT_SHADER],
				open("shaders/default_shader.glsl").read())

		if not Geometry.wire_shader:
			Geometry.wire_shader = makeProgram(gl, "330 core", [GL_VERTEX_SHADER, GL_GEOMETRY_SHADER, GL_FRAGMENT_SHADER],
				open("shaders/wireframe_shader.glsl").read())



		self.verts = v
		self.vertToFaces = vtf
		self.faces = f

		# Creating the VAO and VBO(s)
		# 
		self.vao = GLuint(0)
		gl.glGenVertexArrays(1, self.vao)
		gl.glBindVertexArray(self.vao)

		# Index IBO
		idx_array = pygloo.c_array(GLuint, _flatten_list(self.faces))
		self.ibo = GLuint(0)
		self.ibo_size = len(idx_array)
		# print "ibo ", self.ibo_size
		gl.glGenBuffers(1, self.ibo)
		gl.glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, self.ibo);
		gl.glBufferData(GL_ELEMENT_ARRAY_BUFFER, sizeof(idx_array), idx_array, GL_STATIC_DRAW);

		# Vertex Position VBO
		self.vbo_pos = GLuint(0)
		gl.glGenBuffers(1, self.vbo_pos)

		self.update(gl)



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

		# Cleanup
		gl.glBindBuffer(GL_ARRAY_BUFFER, 0)
		gl.glBindVertexArray(0)





	def render(self, gl, mv, proj, wireframe=False):

		# Render
		# 
		gl.glUseProgram(Geometry.geo_shader)
		gl.glBindVertexArray(self.vao)
		
		gl.glUniformMatrix4fv(gl.glGetUniformLocation(Geometry.geo_shader, "modelViewMatrix"), 1, True, pygloo.c_array(GLfloat, _flatten_list(mv)))
		gl.glUniformMatrix4fv(gl.glGetUniformLocation(Geometry.geo_shader, "projectionMatrix"), 1, True, pygloo.c_array(GLfloat, _flatten_list(proj)))

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