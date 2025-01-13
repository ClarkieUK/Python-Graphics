#version 330 
#ifdef GL_ES
#endif

#define iterations 17
#define formuparam 0.53

#define volsteps 20
#define stepsize 0.1

#define zoom   0.800
#define tile   0.850
#define speed  0.0002 

#define brightness 0.002
#define darkmatter 0.300
#define distfading 0.750
#define saturation 0.750

in vec3 Norm;
in vec4 TruePosition;

uniform float iTime;

out vec4 fragColor; 

float SCurve(float value) {
    if (value < 0.5) {
        return value * value * value * value * value * 16.0; 
    }
    value -= 1.0;
    return value * value * value * value * value * 16.0 + 1.0;
}

void main() {
    vec3 iResolution = vec3(1.0, 1.0, 1.0);

    // Normalize TruePosition to get spherical coordinates
    vec3 uv = normalize(TruePosition.xyz);

    // Get direction vector for volumetric rendering
    vec3 dir = uv * zoom;
    float time = iTime * speed + 0.25;

    // Apply rotation for dynamic effect
    float a1 = 0.5 / iResolution.x * 2.0;
    float a2 = 0.8 / iResolution.y * 2.0;
    mat2 rot1 = mat2(cos(a1), sin(a1), -sin(a1), cos(a1));
    mat2 rot2 = mat2(cos(a2), sin(a2), -sin(a2), cos(a2));
    dir.xz *= rot1;
    dir.xy *= rot2;

    vec3 from = vec3(1.0, 0.5, 0.5);
    from += vec3(time * 2.0, time, -2.0);
    from.xz *= rot1;
    from.xy *= rot2;

    // Volumetric rendering
    float s = 0.1, fade = 1.0;
    vec3 v = vec3(0.0);
    for (int r = 0; r < volsteps; r++) {
        vec3 p = from + s * dir * 0.5;
        p = abs(vec3(tile) - mod(p, vec3(tile * 2.0))); // tiling fold
        float pa, a = pa = 0.0;
        for (int i = 0; i < iterations; i++) { 
            p = abs(p) / dot(p, p) - formuparam; // the magic formula
            a += abs(length(p) - pa); // absolute sum of average change
            pa = length(p);
        }
        float dm = max(0.0, darkmatter - a * a * 0.001); // dark matter
        a = pow(a, 2.5); // add contrast
        if (r > 6) fade *= 1.0 - dm; // dark matter, don't render near
        v += fade;
        v += vec3(s, s * s, s * s * s * s) * a * brightness * fade; // coloring based on distance
        fade *= distfading; // distance fading
        s += stepsize;
    }

    v = mix(vec3(length(v)), v, saturation); // color adjust

    vec4 C = vec4(v * 0.01, 1.0);

    C.r = pow(C.r, 0.35); 
    C.g = pow(C.g, 0.36); 
    C.b = pow(C.b, 0.4); 

    vec4 L = C;   

    C.r = mix(L.r, SCurve(C.r), 1.0); 
    C.g = mix(L.g, SCurve(C.g), 0.9); 
    C.b = mix(L.b, SCurve(C.b), 0.6);     

    fragColor = vec4(C.xyz, 0.5);    
}
