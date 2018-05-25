#version 330

in vec3 vertexPosition;
in float radius;

out vec3 color;
vec3 worldPosition;
uniform mat4 modelMatrix;
uniform mat4 modelView;
uniform mat3 modelViewNormal;
uniform mat4 mvp;
uniform mat4 projectionMatrix;
uniform mat4 viewportMatrix;

//uniform float pointSize;

void main()
{
    color = vec3(1.0, 0.0, 0.0);
    // Transform position, normal, and tangent to world coords
    //worldPosition = vec3(modelMatrix * vec4(vertexPosition, 1.0));
    // Calculate vertex position in clip coordinates
    //gl_Position = mvp * vec4(worldPosition, 1.0);
    gl_Position = mvp * vec4(vertexPosition, 1.0);
    //gl_Position = mvp * vec4(0.0, 0.0, 0.0, 1.0);
    //gl_Position = vec4(0.0, 0.0, 0.0, 1.0);
    //gl_PointSize = viewportMatrix[1][1] * projectionMatrix[1][1] * pointSize / gl_Position.w;
    gl_PointSize = viewportMatrix[1][1] * projectionMatrix[1][1] * (2.0 * radius) / gl_Position.w;
    //gl_PointSize = viewportMatrix[1][1] * projectionMatrix[1][1] * 100.0 / gl_Position.w;
    //gl_PointSize = 3.0;
}
