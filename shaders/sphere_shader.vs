#version 330 core

layout (location = 0) in vec3 iPos;          // the position variable has attribute position 0
layout (location = 1) in vec2 iTexCoord;
layout (location = 2) in vec3 iNorm;

out vec2 TexCoord;        
out vec3 TexCoord0;

uniform mat4 model;
uniform mat4 view;
uniform mat4 projection;

void main()
{
    gl_Position = projection * view * model * vec4(iPos.x,iPos.y,iPos.z, 1.0);

    TexCoord = iTexCoord;
    TexCoord0 = iNorm;
}  