#version 330 core

layout (location = 0) in vec3 aPos;          // the position variable has attribute position 0
layout (location = 1) in vec2 aTexCoord;
layout (location = 2) in vec3 aNorm;

out vec2 TexCoord;        
out vec3 TexCoord0;

uniform mat4 model;
uniform mat4 view;
uniform mat4 projection;

void main()
{
    gl_Position = projection * view * model * vec4(aPos.x,aPos.y,aPos.z, 1.0);

    TexCoord = aTexCoord;
    TexCoord0 = aNorm;
}  