#version 330 core
#ifdef GL_ES
#endif

in vec3 Norm;
in vec2 TexCoord;
in vec4 TruePosition;

uniform sampler2D iTexture;
uniform float iTime;

out vec4 fragColor;  

// shading 3D sphere
void main(){   
	// normailze and adjsut for ratio
    vec2 res = vec2(1,1);
    vec2 uv = (TexCoord);
	uv*=.7;
    //initilize colors
	vec4 color1 = vec4(.4,.6,.7,1.0);
    vec4 color2 = vec4(.9,.7,.6,1.0);
    
    // shade with 2 faux lights
    color1*=.8-distance(uv,vec2(-.1,-.1));
    color2*=.6-distance(uv,vec2(.25,.3));
 	vec4 sphere = color1+color2 ;
    
    //limit edges to circle shape
    float d = distance(uv, vec2(0.0));
    // smooth edges
	float t =1.0- smoothstep(.6,.61, d);
    // apply shape to colors
    sphere*=t+sin(iTime)*.2*uv.y;
    
    //output final color, and brighten
	fragColor = sphere*1.6;
    
}