# version 330

layout(location = 0) in vec3 a_position;

uniform mat4 view;
uniform mat4 projection;
uniform float iTime;

void main()
{
    
    gl_Position =  projection * view * vec4(a_position, 1.0);
}

