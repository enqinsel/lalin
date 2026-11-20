shader_type canvas_item;

uniform vec2 iris_center;
uniform vec2 dimensions;
uniform float radius = 8.1;

void fragment() {
    float silhouette = texture(TEXTURE, UV).a;
    vec2 delta = (UV - iris_center) * dimensions;
    float r = length(delta / vec2(1.0, 1.05)) / radius;
    float iris = 1.0 - smoothstep(.91, 1.0, r);
    float pupil = 1.0 - smoothstep(.48, .55, r);
    vec3 sclera = mix(vec3(.72, .57, .48), vec3(.96, .90, .83), smoothstep(.04, .72, UV.y));
    vec3 inner = mix(vec3(.15, .072, .049), vec3(.46, .23, .12), (1.0 - r) * .65 + smoothstep(-6.0, 8.0, delta.y) * .30);
    inner = mix(inner, vec3(.072, .038, .025), pupil);
    float light = 1.0 - smoothstep(1.0, 1.8, length(delta - vec2(2.0, -3.4)));
    inner = mix(inner, vec3(.99, .94, .88), light);
    COLOR = vec4(mix(sclera, inner, iris), silhouette);
}
