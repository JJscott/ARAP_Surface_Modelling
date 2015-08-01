/*
 *
 * Shader program drawing really basic geometry
 *
 */

uniform mat4 projectionMatrix;
uniform mat4 modelViewMatrix;
uniform vec3 color;

#ifdef _VERTEX_

layout(location = 0) in vec3 m_pos;

out VertexData
{
	vec3 pos;
} v_out;

void main() {
	vec4 p = modelViewMatrix * vec4(m_pos, 1.0);
	v_out.pos = p.xyz;
	gl_Position = projectionMatrix * p;
}

#endif

//-------------------------------------------------------------
//-------------------------------------------------------------
//-------------------------------------------------------------

#ifdef _FRAGMENT_

in VertexData
{
	vec3 pos;
} v_in;

out vec3 frag_color;

void main() {
	frag_color = color;
}

#endif