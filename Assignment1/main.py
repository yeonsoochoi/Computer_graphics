import numpy as np
import glfw
from OpenGL.GL import *
from OpenGL.GLU import *

gCamAng = 0.
buttonpress = 0.
xpos_start = 0.
ypos_start = 0.
xp = 0
yp = 0
x_for_panning = 0.
y_for_panning = 0.
trans_store = np.identity(4)
height_store = np.identity(4)
zoom = 0
duck_pos = 0


def render(camAng):
    global xp, yp
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glEnable(GL_DEPTH_TEST)
    glPolygonMode(GL_FRONT_AND_BACK, GL_LINE)

    glLoadIdentity()
    gluPerspective(30, 1, .1, 100)

    # viewing camera
    camera_setting(-30)

    drawFrame()
    drawPlateArray()

    glColor3ub(255, 255, 255)

    draw_duck()



# draw primitive and frame

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
            glVertex3f(x * zr0, y * zr0, z0)
            glVertex3f(x * zr1, y * zr1, z1)

        glEnd()


def drawCube():
     glBegin(GL_QUADS)
     glVertex3f( 1.0, 1.0,-1.0)
     glVertex3f(-1.0, 1.0,-1.0)
     glVertex3f(-1.0, 1.0, 1.0)
     glVertex3f( 1.0, 1.0, 1.0)

     glVertex3f( 1.0,-1.0, 1.0)
     glVertex3f(-1.0,-1.0, 1.0)
     glVertex3f(-1.0,-1.0,-1.0)
     glVertex3f( 1.0,-1.0,-1.0)

     glVertex3f( 1.0, 1.0, 1.0)
     glVertex3f(-1.0, 1.0, 1.0)
     glVertex3f(-1.0,-1.0, 1.0)
     glVertex3f( 1.0,-1.0, 1.0)

     glVertex3f( 1.0,-1.0,-1.0)
     glVertex3f(-1.0,-1.0,-1.0)
     glVertex3f(-1.0, 1.0,-1.0)
     glVertex3f( 1.0, 1.0,-1.0)

     glVertex3f(-1.0, 1.0, 1.0)
     glVertex3f(-1.0, 1.0,-1.0)
     glVertex3f(-1.0,-1.0,-1.0)
     glVertex3f(-1.0,-1.0, 1.0)

     glVertex3f( 1.0, 1.0,-1.0)
     glVertex3f( 1.0, 1.0, 1.0)
     glVertex3f( 1.0,-1.0, 1.0)
     glVertex3f( 1.0,-1.0,-1.0)
     glEnd()


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
            glTranslatef(j-10, 0, i-10)
            drawPlate()
            glPopMatrix()



# manipulate the camera with mouse movement

def camera_setting(first):
    global trans_store, height_store, zoom

    glTranslate(0, 0, first + zoom)
    # move camera
    x = height_store @ trans_store
    glMultMatrixf(x.T)



# for left button click
def cursor_callback1(window, xpos, ypos):
    global xp, yp, xpos_start, ypos_start, gCamAng, trans_store, height_store

    gCamAng = -(np.radians(xpos_start - xpos))/1.5
    height = -(np.radians(ypos_start - ypos))/1.5
    xpos_start = xpos
    ypos_start = ypos
    rotation_matrix = np.array([[ np.cos(gCamAng), 0., np.sin(gCamAng), 0.],
                                [              0., 1.,              0., 0.],
                                [-np.sin(gCamAng), 0., np.cos(gCamAng), 0.],
                                [              0., 0.,              0., 1.]])

    height_matrix = np.array([[1.,              0.,             0., 0.],
                              [0., np.cos(height), -np.sin(height), 0.],
                              [0., np.sin(height),  np.cos(height), 0.],
                              [0.,              0.,             0., 1.]])
    trans_store = rotation_matrix @ trans_store
    height_store = height_matrix @ height_store


# for right button click
def cursor_callback2(window, xpos, ypos):
    global x_for_panning, y_for_panning, gCamAng, trans_store, height_store

    now_panning_x = (- x_for_panning + xpos) / 40
    now_panning_y = (- y_for_panning + ypos) / 40

    panning_matrix_x = ([[1., 0., 0., now_panning_x],
                         [0., 1., 0.,            0.],
                         [0., 0., 1.,            0.],
                         [0., 0., 0.,            1.]])

    panning_matrix_y = ([[1., 0., 0.,             0.],
                         [0., 1., 0., -now_panning_y],
                         [0., 0., 1.,             0.],
                         [0., 0., 0.,             1.]])
    x_for_panning = xpos
    y_for_panning = ypos

    trans_store = panning_matrix_x @ trans_store
    height_store = panning_matrix_y @ height_store

# after release, do nothing
def cursor_callback_end(window, xpos, ypos):
    pass

# mouse click event callback
def button_callback(window, button, action, mod):
    global xpos_start, ypos_start, x_for_panning, y_for_panning

    if button == glfw.MOUSE_BUTTON_LEFT:
        if action == glfw.PRESS:
            (xpos_start, ypos_start) = glfw.get_cursor_pos(window)
            glfw.set_cursor_pos_callback(window, cursor_callback1)
        elif action == glfw.RELEASE:
            glfw.set_cursor_pos_callback(window, cursor_callback_end)

    if button == glfw.MOUSE_BUTTON_RIGHT:
        if action == glfw.PRESS:
            (x_for_panning, y_for_panning) = glfw.get_cursor_pos(window)
            glfw.set_cursor_pos_callback(window, cursor_callback2)
        elif action == glfw.RELEASE:
            glfw.set_cursor_pos_callback(window, cursor_callback_end)


def scroll_callback(window, xoffset, yoffset):
    global zoom
    zoom = zoom + yoffset/3



# draw_obj

def draw_duck():

    t = glfw.get_time()

    # body transformation
    glPushMatrix()
    glRotatef((t/7) * (180 / np.pi), 0., 1., 0.)
    glTranslatef(0., 1., 4.)


    # draw body
    glPushMatrix()
    glScalef(1., .5, .5)  # x is front & rare
    drawSphere()
    glPopMatrix()


    # right leg transformation
    glPushMatrix()
    glRotatef(25 * np.cos(1.5 * t)+3, 0., 0., 1.)
    glTranslatef(0., -.5, .25)
    glRotatef(-15,0,0,1)

    # draw right leg
    draw_leg()
    draw_foot()

    glPopMatrix() # right leg pop


    # left leg transformation
    glPushMatrix()
    glRotatef(-25 * np.cos(1.5 * t)+3, 0., 0., 1.)
    glTranslatef(0., -.5, -.25)
    glRotatef(-15,0,0,1)


    # draw left leg
    draw_leg()
    draw_foot()

    glPopMatrix() # left leg pop

    # draw neck & head
    glPushMatrix()
    glTranslatef(.5, 0., 0.)
    glRotatef(20 * (np.sin(3 * t) + 3), 0., 0., 1.)

    # neck translation
    glPushMatrix()
    glTranslatef(.4, 0., 0.)
    # draw neck
    glPushMatrix()
    glScalef(.6, .1, .1)
    drawCube()
    glPopMatrix()

    # head translation
    glPushMatrix()
    glTranslatef(.5, 0., 0.)
    glRotatef(-30 * np.sin(3 * t), 0., 0., 1.)

    # draw head_part

    # draw head
    glPushMatrix()
    glScalef(.35, .35, .35)
    drawSphere()
    glPopMatrix()

    # right eye translation
    glPushMatrix()
    glTranslatef(.35*np.cos(45), -.35*np.cos(45), .2)
    # draw right eye
    glScalef(.05, .05, .05)
    drawSphere()
    glPopMatrix() # right eye pop

    # left eye translation
    glPushMatrix()
    glTranslatef(.35*np.cos(45), -.35*np.cos(45), -.2)
    # draw left eye
    glScalef(.05, .05, .05)
    drawSphere()
    glPopMatrix() # left eye pop

    # upper beak translation
    glPushMatrix()
    glTranslatef(0., -.25, 0.)
    glRotatef(abs(30 * np.cos(3 * t)), 0., 0., 1.)
    # draw upper beak
    draw_beak()
    glPopMatrix() # upper beak pop

    # under beak translation
    glPushMatrix()
    glTranslate(0., -.25, 0.)
    glRotatef(-abs(30 * np.cos(3 * t)), 0., 0., 1.)
    # draw under beak
    draw_beak()
    glPopMatrix() # under beak pop

    glPopMatrix() # head pop
    glPopMatrix() # neck pop
    glPopMatrix() # neck & head pop

    # tail translation
    glPushMatrix()
    glTranslatef(-1., 0., 0.)
    glRotatef(-20., 0., 0., 1.)
    # draw tail
    glScalef(.2, .1, .1)
    drawSphere()
    glPopMatrix() # tail pop

    # right wing translation
    glPushMatrix()
    glTranslatef(-.12, 0., .5)
    glRotatef(-20., 0., 0., 1.)
    # draw right wing
    glScalef(.7, .3, .05)
    drawSphere()
    glPopMatrix() # right wing pop
    
    # left wing translation
    glPushMatrix()
    glTranslatef(-.12, 0., -.5)
    glRotatef(-20., 0., 0., 1.)
    # draw left wing
    glScalef(.7, .3, .05)
    drawSphere()
    glPopMatrix() # left wing pop

    glPopMatrix() # last body pop


def draw_leg():
    glPushMatrix()
    glScalef(.05, .5, .05)
    drawCube()
    glPopMatrix()

def draw_toe():
    glPushMatrix()
    glScalef(.2, .05, .05)
    drawSphere()
    glPopMatrix()

def draw_foot():
    glPushMatrix()
    glTranslatef(.15, -.5, 0.)
    draw_toe()
    glPopMatrix()

    glPushMatrix()
    glTranslatef(.15, -.5, .1)
    glRotatef(-45, 0., 1., 0.)
    draw_toe()
    glPopMatrix()

    glPushMatrix()
    glTranslatef(.15, -.5, -.1)
    glRotatef(45, 0., 1., 0.)
    draw_toe()
    glPopMatrix()

def draw_beak():
    glPushMatrix()
    glTranslatef(0., -.07, 0.)
    glScalef(.02, .1, .2)
    drawSphere()
    glPopMatrix()




def main():
    # Initialize the library
    if not glfw.init():
        return
    # Create a windowed mode window and its OpenGL context
    window = glfw.create_window(720, 720, "2015005141", None, None)
    if not window:
        glfw.terminate()
        return

    # Make the window's context current
    glfw.make_context_current(window)
    glfw.swap_interval(1)
    glfw.set_mouse_button_callback(window, button_callback)
    glfw.set_scroll_callback(window, scroll_callback)

    # Loop until the user closes the window
    while not glfw.window_should_close(window):
        # Poll for and process events
        glfw.poll_events()
        render(gCamAng)
        # Swap front and back buffers
        glfw.swap_buffers(window)

    glfw.terminate()


if __name__ == "__main__":
    main()
