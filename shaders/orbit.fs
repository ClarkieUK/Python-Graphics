# version 330


uniform vec3 bodyColor;
uniform float iTime;

out vec4 fragColor;


void main()
{
    fragColor = vec4(bodyColor,0.4);
}
