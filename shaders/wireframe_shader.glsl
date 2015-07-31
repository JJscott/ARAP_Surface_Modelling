/*
 *
 * Shader program drawing really basic geometry
 *
 */

uniform mat4 projectionMatrix;
uniform mat4 modelViewMatrix;

#ifdef _VERTEX_

layout(location = 0) in vec3 m_pos;

out VertexData
{
	vec3 pos;
} v_out;

void main() {
	v_out.pos = m_pos;
}

#endif

//-------------------------------------------------------------
//-------------------------------------------------------------
//-------------------------------------------------------------

#ifdef _GEOMETRY_

layout(triangles) in;
layout(line_strip, max_vertices=3) out;

in VertexData
{
	vec3 pos;
} v_in[];

out VertexData
{
	vec3 pos;
	vec3 norm;
} v_out;

void main() {
	vec3 ab = normalize(v_in[1].pos - v_in[0].pos);
	vec3 ac = normalize(v_in[2].pos - v_in[0].pos);

	vec3 norm = normalize(cross(ab, ac));

	for (int i = 0; i < 3; i++) {
		vec4 p = modelViewMatrix * vec4(v_in[i].pos, 1.0);
		v_out.pos = p.xyz;
		v_out.norm = (modelViewMatrix * vec4(norm, 0.0)).xyz;
		gl_Position = projectionMatrix * p;
		EmitVertex();
	}
}

#endif

//-------------------------------------------------------------
//-------------------------------------------------------------
//-------------------------------------------------------------

#ifdef _FRAGMENT_

in VertexData
{
	vec3 pos;
	vec3 norm;
} v_in;

out vec3 frag_color;

void main(){
	// vec3 grey = vec3(0.1, 0.1, 0.1);
	// frag_color = grey * abs(normalize(v_in.norm).z);
	frag_color = vec3(0.1, 0.1, 0.1);
}

#endif