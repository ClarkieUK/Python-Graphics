#version 330 core

in vec2 TexCoord;
in vec3 TexCoord0;

out vec4 FragColor;  

uniform sampler2D texture;

void main()
{
    //vec4 texel = textureCube(texture1, TexCoord0);
    //FragColor = texel;
    //FragColor = vec4(1.0f,1.0f,1.0f,1.0f);
   FragColor = texture(texture,TexCoord);
    //FragColor = texture(texture2,TexCoord);
    //FragColor =   mix(texture(texture1, TexCoord),texture(texture2,vec2(TexCoord.x,TexCoord.y)),1.0);
}