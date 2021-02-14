import glfw
from OpenGL.GL import *
from OpenGL.GLU import *
import numpy as np
import ctypes

gCamAng = 0.
xpos_start = 0.
ypos_start = 0.
x_for_panning = 0.
y_for_panning = 0.
trans_store = np.identity(4)
height_store = np.identity(4)
zoom = 0

gVertexArraySeparate = None
gComposedM = np.identity(4)
mode = False
rot_t=0
scale = 1


def render(camAng):

    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glEnable(GL_DEPTH_TEST)

    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()

    gluPerspective(30, 1, 1, 400)

    if mode:
        camera_setting2()
    else:
        camera_setting()


    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()

    drawFrame()
    drawPlateArray()

    glEnable(GL_LIGHTING)
    glEnable(GL_LIGHT0)
    glEnable(GL_LIGHT1)
    glEnable(GL_NORMALIZE)

    glPushMatrix()
    lightPos0 = (-2., 4., 1., 0.)
    glLightfv(GL_LIGHT0, GL_POSITION, lightPos0)
    glPopMatrix()

    glPushMatrix()
    t = glfw.get_time()
    glRotatef(t*(180/np.pi),0,1,0)  # try to uncomment: rotate light
    lightpos1 = (3., 4., 5., 1.)  # try to change 4th element to 0. or 1.
    glLightfv(GL_LIGHT1, GL_POSITION, lightpos1)
    glPopMatrix()

    lightColor0 = (1, 1, 1, 0)
    ambientLightColor = (.1, .1, .1, 0.)
    glLightfv(GL_LIGHT0, GL_DIFFUSE, lightColor0)
    glLightfv(GL_LIGHT0, GL_SPECULAR, lightColor0)
    glLightfv(GL_LIGHT0, GL_AMBIENT, ambientLightColor)


    lightColor1 = (1., 1., 1., 1.)
    ambientLightColor = (.1, .1, .1, 1.)
    glLightfv(GL_LIGHT1, GL_DIFFUSE, lightColor1)
    glLightfv(GL_LIGHT1, GL_SPECULAR, lightColor1)
    glLightfv(GL_LIGHT1, GL_AMBIENT, ambientLightColor)


    glPushMatrix()
    drawObj_glDrawArray()
    glPopMatrix()


    glDisable(GL_LIGHTING)


def drawFrame():
    glBegin(GL_LINES)
    glColor3ub(255, 0, 0)
    glVertex3fv(np.array([0., 0., 0.]))
    glVertex3fv(np.array([10., 0., 0.]))

    glColor3ub(0, 255, 0)
    glVertex3fv(np.array([0., 0., 10.]))
    glVertex3fv(np.array([0., 0., 0.]))
    glEnd()

def drawPlate():
    glBegin(GL_LINES)
    glColor3ub(255, 255, 255)
    glVertex3fv(np.array([0., 0., 0.]))
    glVertex3fv(np.array([1., 0., 0.]))

    glVertex3fv(np.array([1., 0., 0.]))
    glVertex3fv(np.array([1., 0., 1.]))

    glVertex3fv(np.array([1., 0., 1.]))
    glVertex3fv(np.array([0., 0., 1.]))

    glVertex3fv(np.array([0., 0., 1.]))
    glVertex3fv(np.array([0., 0., 0.]))
    glEnd()


def drawPlateArray():
    for i in range(20):
        for j in range(20):
            glPushMatrix()
            glTranslatef(j - 10, 0, i - 10)
            drawPlate()
            glPopMatrix()

def drawSphere(numLats=12, numLongs=12):
    for i in range(0, numLats + 1):
        lat0 = np.pi * (-0.5 + float(float(i - 1) / float(numLats)))
        z0 = np.sin(lat0)
        zr0 = np.cos(lat0)

        lat1 = np.pi * (-0.5 + float(float(i) / float(numLats)))
        z1 = np.sin(lat1)
        zr1 = np.cos(lat1)

        # Use Quad strips to draw the sphere
        glBegin(GL_QUAD_STRIP)

        for j in range(0, numLongs + 1):
            lng = 2 * np.pi * float(float(j - 1) / float(numLongs))
            x = np.cos(lng)
            y = np.sin(lng)
            glVertex3f(.2 * x * zr0, .2 * y * zr0, .2 * z0)
            glVertex3f(.2 * x * zr1, .2 * y * zr1, .2 * z1)

        glEnd()


def sphere1():
    t = glfw.get_time()
    xang = np.radians(0)
    yang = np.radians(90)
    zang = np.radians(100*t)
    M = np.identity(4)
    Rx = np.array([[np.cos(xang), -np.sin(xang), 0],
                   [np.sin(xang), np.cos(xang), 0],
                   [0, 0, 1]])
    Ry = np.array([[1, 0, 0],
                   [0, np.cos(yang), -np.sin(yang)],
                   [0, np.sin(yang), np.cos(yang)]])
    Rz = np.array([[np.cos(zang), -np.sin(zang), 0],
                   [np.sin(zang), np.cos(zang), 0],
                   [0, 0, 1]])
    M[:3,:3] = Rx @ Ry @ Rz
    glPushMatrix()
    glTranslate(0,1,0)
    glMultMatrixf(M.T)
    glTranslate(0,2,0)
    drawSphere()
    glPopMatrix()

def sphere2():
    t = glfw.get_time()
    xang = np.radians(100 * t)
    yang = np.radians(0)
    zang = np.radians(0)
    M = np.identity(4)
    Rx = np.array([[np.cos(xang), -np.sin(xang), 0],
                   [np.sin(xang), np.cos(xang), 0],
                   [0, 0, 1]])
    Ry = np.array([[1, 0, 0],
                   [0, np.cos(yang), -np.sin(yang)],
                   [0, np.sin(yang), np.cos(yang)]])
    Rz = np.array([[np.cos(zang), -np.sin(zang), 0],
                   [np.sin(zang), np.cos(zang), 0],
                   [0, 0, 1]])
    M[:3, :3] = Rx @ Ry @ Rz
    glPushMatrix()
    glTranslate(0, 1, 0)
    glMultMatrixf(M.T)
    glTranslate(0, 2, 0)
    drawSphere()
    glPopMatrix()

def sphere3():
    t = glfw.get_time()
    xang = np.radians(-100 * t)
    yang = np.radians(0)
    zang = np.radians(0)
    M = np.identity(4)
    Rx = np.array([[np.cos(xang), -np.sin(xang), 0],
                   [np.sin(xang), np.cos(xang), 0],
                   [0, 0, 1]])
    Ry = np.array([[1, 0, 0],
                   [0, np.cos(yang), -np.sin(yang)],
                   [0, np.sin(yang), np.cos(yang)]])
    Rz = np.array([[np.cos(zang), -np.sin(zang), 0],
                   [np.sin(zang), np.cos(zang), 0],
                   [0, 0, 1]])
    M[:3, :3] = Rx @ Ry @ Rz
    glPushMatrix()
    glTranslate(0, 1, 0)
    glMultMatrixf(M.T)
    glTranslate(0, 2, 0)
    drawSphere()
    glPopMatrix()

def sphere4():
    t = glfw.get_time()
    xang = np.radians(0)
    yang = np.radians(100 * t)
    zang = np.radians(0)
    M = np.identity(4)
    Rx = np.array([[np.cos(xang), -np.sin(xang), 0],
                   [np.sin(xang), np.cos(xang), 0],
                   [0, 0, 1]])
    Ry = np.array([[1, 0, 0],
                   [0, np.cos(yang), -np.sin(yang)],
                   [0, np.sin(yang), np.cos(yang)]])
    Rz = np.array([[np.cos(zang), -np.sin(zang), 0],
                   [np.sin(zang), np.cos(zang), 0],
                   [0, 0, 1]])
    M[:3, :3] = Rx @ Ry @ Rz
    glPushMatrix()
    glTranslate(0, 1, 0)
    glMultMatrixf(M.T)
    glTranslate(0, -2, 0)
    drawSphere()
    glPopMatrix()

def sphere5():
    t = glfw.get_time()
    xang = np.radians(0)
    yang = np.radians(-100 * t)
    zang = np.radians(0)
    M = np.identity(4)
    Rx = np.array([[np.cos(xang), -np.sin(xang), 0],
                   [np.sin(xang), np.cos(xang), 0],
                   [0, 0, 1]])
    Ry = np.array([[1, 0, 0],
                   [0, np.cos(yang), -np.sin(yang)],
                   [0, np.sin(yang), np.cos(yang)]])
    Rz = np.array([[np.cos(zang), -np.sin(zang), 0],
                   [np.sin(zang), np.cos(zang), 0],
                   [0, 0, 1]])
    M[:3, :3] = Rx @ Ry @ Rz
    glPushMatrix()
    glTranslate(0, 1, 0)
    glMultMatrixf(M.T)
    glTranslate(0, -2, 0)
    drawSphere()
    glPopMatrix()


def createVertexArraySeparate():
    varr = np.array([
            (0,0,1),         # v0 normal
            ( -1 ,  2 ,  1 ), # v0 position
            (0,0,1),         # v2 normal
            (  1 ,  0 ,  1 ), # v2 position
            (0,0,1),         # v1 normal
            (  1 ,  2 ,  1 ), # v1 position

            (0,0,1),         # v0 normal
            ( -1 ,  2 ,  1 ), # v0 position
            (0,0,1),         # v3 normal
            ( -1 ,  0 ,  1 ), # v3 position
            (0,0,1),         # v2 normal
            (  1 ,  0 ,  1 ), # v2 position

            (0,0,-1),
            ( -1 ,  2 , -1 ), # v4
            (0,0,-1),
            (  1 ,  2 , -1 ), # v5
            (0,0,-1),
            (  1 ,  0 , -1 ), # v6

            (0,0,-1),
            ( -1 ,  2 , -1 ), # v4
            (0,0,-1),
            (  1 ,  0 , -1 ), # v6
            (0,0,-1),
            ( -1 ,  0 , -1 ), # v7

            (0,1,0),
            ( -1 ,  2 ,  1 ), # v0
            (0,1,0),
            (  1 ,  2 ,  1 ), # v1
            (0,1,0),
            (  1 ,  2 , -1 ), # v5

            (0,1,0),
            ( -1 ,  2 ,  1 ), # v0
            (0,1,0),
            (  1 ,  2 , -1 ), # v5
            (0,1,0),
            ( -1 ,  2 , -1 ), # v4

            (0,-1,0),
            ( -1 ,  0 ,  1 ), # v3
            (0,-1,0),
            (  1 ,  0 , -1 ), # v6
            (0,-1,0),
            (  1 ,  0 ,  1 ), # v2

            (0,-1,0),
            ( -1 ,  0 ,  1 ), # v3
            (0,-1,0),
            ( -1 ,  0 , -1 ), # v7
            (0,-1,0),
            (  1 ,  0 , -1 ), # v6

            (1,0,0),
            (  1 ,  2 ,  1 ), # v1
            (1,0,0),
            (  1 ,  0 ,  1 ), # v2
            (1,0,0),
            (  1 ,  0 , -1 ), # v6

            (1,0,0),
            (  1 ,  2 ,  1 ), # v1
            (1,0,0),
            (  1 ,  0 , -1 ), # v6
            (1,0,0),
            (  1 ,  2 , -1 ), # v5

            (-1,0,0),
            ( -1 ,  2 ,  1 ), # v0
            (-1,0,0),
            ( -1 ,  0 , -1 ), # v7
            (-1,0,0),
            ( -1 ,  0 ,  1 ), # v3

            (-1,0,0),
            ( -1 ,  2 ,  1 ), # v0
            (-1,0,0),
            ( -1 ,  2 , -1 ), # v4
            (-1,0,0),
            ( -1 ,  0 , -1 ), # v7
            ], 'float32')
    return varr


def drawObj_glDrawArray():
    global gVertexArraySeparate, gComposedM
    varr = gVertexArraySeparate
    glEnableClientState(GL_VERTEX_ARRAY)
    glEnableClientState(GL_NORMAL_ARRAY)
    glPushMatrix()
    objectColor = (1, 1, 0, 0)

    specularObjectColor = (1., 1., 1., 1.)
    glMaterialfv(GL_FRONT, GL_AMBIENT_AND_DIFFUSE, objectColor)
    glMaterialfv(GL_FRONT, GL_SHININESS, 5)
    glMaterialfv(GL_FRONT, GL_SPECULAR, specularObjectColor)
    glPopMatrix()

    glPushMatrix()
    glMultMatrixf(gComposedM.T)
    glNormalPointer(GL_FLOAT, 6*varr.itemsize, varr)
    glVertexPointer(3, GL_FLOAT, 6*varr.itemsize, ctypes.c_void_p(varr.ctypes.data + 3*varr.itemsize))
    glDrawArrays(GL_TRIANGLES, 0, int(varr.size/6))

    glPushMatrix()
    objectColor = (1, 0, 0, 0)
    specularObjectColor = (1., 1., 1., 1.)
    glMaterialfv(GL_FRONT, GL_AMBIENT_AND_DIFFUSE, objectColor)
    glMaterialfv(GL_FRONT, GL_SHININESS, 5)
    glMaterialfv(GL_FRONT, GL_SPECULAR, specularObjectColor)
    sphere1()
    glPopMatrix()

    glPushMatrix()
    objectColor = (0, 1, 0, 0)
    specularObjectColor = (1., 1., 1., 1.)
    glMaterialfv(GL_FRONT, GL_AMBIENT_AND_DIFFUSE, objectColor)
    glMaterialfv(GL_FRONT, GL_SHININESS, 5)
    glMaterialfv(GL_FRONT, GL_SPECULAR, specularObjectColor)
    sphere2()
    glPopMatrix()

    glPushMatrix()
    objectColor = (0, 0, 1, 0)
    specularObjectColor = (1., 1., 1., 1.)
    glMaterialfv(GL_FRONT, GL_AMBIENT_AND_DIFFUSE, objectColor)
    glMaterialfv(GL_FRONT, GL_SHININESS, 5)
    glMaterialfv(GL_FRONT, GL_SPECULAR, specularObjectColor)
    sphere3()
    glPopMatrix()

    glPushMatrix()
    objectColor = (1, 0, 1, 0)
    specularObjectColor = (1., 1., 1., 1.)
    glMaterialfv(GL_FRONT, GL_AMBIENT_AND_DIFFUSE, objectColor)
    glMaterialfv(GL_FRONT, GL_SHININESS, 5)
    glMaterialfv(GL_FRONT, GL_SPECULAR, specularObjectColor)
    sphere4()
    glPopMatrix()

    glPushMatrix()
    objectColor = (0, 1, 1, 0)
    specularObjectColor = (1., 1., 1., 1.)
    glMaterialfv(GL_FRONT, GL_AMBIENT_AND_DIFFUSE, objectColor)
    glMaterialfv(GL_FRONT, GL_SHININESS, 5)
    glMaterialfv(GL_FRONT, GL_SPECULAR, specularObjectColor)
    sphere5()
    glPopMatrix()
    glPopMatrix()




def key_callback(window, key, scancode, action, mods):
    global gCamAng, gComposedM, trans_store, height_store, mode, rot_t, scale
    if action==glfw.PRESS or action==glfw.REPEAT:
        if key==glfw.KEY_D:       # translate x positive
            T = np.array([[1, 0, 0,  .1],
                          [0, 1, 0,   0],
                          [0, 0, 1,   0],
                          [0, 0, 0,   1]])
            gComposedM = gComposedM @ T
            panning_matrix_x = ([[1., 0., 0., -.1*np.cos(rot_t)*scale],
                                 [0., 1., 0., 0],
                                 [0., 0., 1., .1*np.sin(rot_t)*scale],
                                 [0., 0., 0., 1.]],)
            trans_store = panning_matrix_x @ trans_store

        elif key==glfw.KEY_A: # translate x negative
            T = np.array([[1, 0, 0, -.1],
                          [0, 1, 0,   0],
                          [0, 0, 1,   0],
                          [0, 0, 0,   1]])
            gComposedM = gComposedM @ T
            panning_matrix_x = ([[1., 0., 0., .1*np.cos(rot_t)*scale],
                                 [0., 1., 0., 0.],
                                 [0., 0., 1., -.1*np.sin(rot_t)*scale],
                                 [0., 0., 0., 1.]])
            trans_store = panning_matrix_x @ trans_store

        elif key==glfw.KEY_S: # translate z positive
            T = np.array([[1, 0, 0,  0],
                          [0, 1, 0,  0],
                          [0, 0, 1, .1],
                          [0, 0, 0,  1]])
            gComposedM = gComposedM @ T
            theta = (3*(np.pi/2))/180
            theta = rot_t + theta
            panning_matrix_z = ([[1., 0., 0., -.1*np.sin(theta)*scale],
                                 [0., 1., 0., 0],
                                 [0., 0., 1., -.1*np.cos(theta)*scale],
                                 [0., 0., 0., 1.]])
            trans_store = panning_matrix_z @ trans_store

        elif key==glfw.KEY_W: # translate z negative
            T = np.array([[1, 0, 0,  0],
                          [0, 1, 0,  0],
                          [0, 0, 1, -.1],
                          [0, 0, 0,  1]])
            gComposedM = gComposedM @ T
            theta = 3*(np.pi/2)
            theta = rot_t + (theta / 180)
            panning_matrix_z = ([[1., 0., 0., .1*np.sin(theta)*scale],
                                 [0., 1., 0., 0],
                                 [0., 0., 1., .1*np.cos(theta)*scale],
                                 [0., 0., 0., 1.]])
            trans_store = panning_matrix_z @ trans_store

        elif key == glfw.KEY_R:  # rotate y positive
            t = 10 * (np.pi / 180)
            rot_t += t
            c = np.cos(t)
            s = np.sin(t)
            R = np.array([[c, 0, s, 0],
                          [0, 1, 0, 0],
                          [-s, 0, c, 0],
                          [0, 0, 0, 1]])
            gComposedM = gComposedM @ R

        elif key == glfw.KEY_F:  # rotate y negative
            t = -10 * (np.pi / 180)
            rot_t += t
            c = np.cos(t)
            s = np.sin(t)
            R = np.array([[c, 0, s, 0],
                          [0, 1, 0, 0],
                          [-s, 0, c, 0],
                          [0, 0, 0, 1]])
            gComposedM = gComposedM @ R

        elif key == glfw.KEY_T: # shear on xz plane to +x
            if mode:
                pass
            else:
                S = np.array([[1, .1, 0, 0],
                              [0,  1, 0, 0],
                              [0,  0, 1, 0],
                              [0,  0, 0, 1]])
                gComposedM = gComposedM @ S

        elif key == glfw.KEY_G: # shear based on xz plane to -x
            if mode:
                pass
            else:
                S = np.array([[1,-.1, 0, 0],
                              [0,  1, 0, 0],
                              [0,  0, 1, 0],
                              [0,  0, 0, 1]])
                gComposedM = gComposedM @ S

        elif key == glfw.KEY_Y: # shear based on xz plane to +z
            if mode:
                pass
            else:
                S = np.array([[1,  0,  0, 0],
                              [0,  1,  0, 0],
                              [0, .1,  1, 0],
                              [0,  0,  0, 1]])
                gComposedM = gComposedM @ S

        elif key == glfw.KEY_H: # shear based on xz plane to -z
            if mode:
                pass
            else:
                S = np.array([[1,  0,  0,  0],
                              [0,  1,  0,  0],
                              [0,-.1,  1,  0],
                              [0,  0,  0,  1]])
                gComposedM = gComposedM @ S

        elif key == glfw.KEY_X: # scale positive
            if mode:
                pass
            else:
                S = np.array([[1.5,  0,  0,  0],
                              [  0,1.5,  0,  0],
                              [  0,  0,1.5,  0],
                              [  0,  0,  0,  1]])
                scale = scale * 1.5
                gComposedM = gComposedM @ S

        elif key == glfw.KEY_C: # scale negative
            if mode:
                pass
            else:
                a = 10/15
                S = np.array([[ a, 0, 0, 0],
                              [ 0, a, 0, 0],
                              [ 0, 0, a, 0],
                              [ 0, 0, 0, 1]])
                scale = scale * a
                gComposedM = gComposedM @ S

        elif key == glfw.KEY_V: # reflect xz plane
            if mode:
                pass
            else:
                S = np.array([[ 1, 0, 0, 0],
                              [ 0,-1, 0, 0],
                              [ 0, 0, 1, 0],
                              [ 0, 0, 0, 1]])
                gComposedM = gComposedM @ S

        elif key == glfw.KEY_Z: # reset
            gComposedM = np.identity(4)
            trans_store = np.identity(4)
            height_store = np.identity(4)
            rot_t = 0
            scale = 1

        elif key == glfw.KEY_M: # view mode
            if mode is True:
                mode = False
            else:
                mode = True

def camera_setting():
    global trans_store, scale
    glTranslate(0, -3.5, -40)
    glRotatef(25,1,1,0)
    x = trans_store
    glMultMatrixf(x.T)

def camera_setting2():
    global trans_store, rot_t, scale
    glTranslate(0,-1,1)
    c = scale * np.cos(-rot_t)
    s = scale * np.sin(-rot_t)
    R = np.array([[c, 0, s, 0],
                  [0, 1, 0, 0],
                  [-s, 0, c, 0],
                  [0, 0, 0, 1]])
    x = R @ trans_store
    glMultMatrixf(x.T)


def main():
    global gVertexArraySeparate
    if not glfw.init():
        return
    window = glfw.create_window(720, 720, '2015005141', None, None)
    if not window:
        glfw.terminate()
        return
    glfw.make_context_current(window)

    gVertexArraySeparate = createVertexArraySeparate()
    glfw.set_key_callback(window, key_callback)
    glfw.swap_interval(1)

    while not glfw.window_should_close(window):
        glfw.poll_events()
        render(gCamAng)
        glfw.swap_interval(1)

        glfw.swap_buffers(window)

    glfw.terminate()


if __name__ == "__main__":
    main()
