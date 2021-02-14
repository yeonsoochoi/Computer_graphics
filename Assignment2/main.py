import numpy as np
import glfw
from OpenGL.GL import *
from OpenGL.GLU import *
import ctypes

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
wire_frame = False
gouraud = False
v = np.array([0.,0.,0.],'float32')
vn = np.array([0.,0.,0.],'float32')
fn = np.array([0., 0.], 'float32')
iarr = np.array([0.,0.,0.])
gVertexArraySeparate = None
reset = None
count_all_num3 = 0


def render(camAng):
    global xp, yp, lightcolor, reset, gVertexArraySeparate
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glEnable(GL_DEPTH_TEST)

    if wire_frame:
        glPolygonMode(GL_FRONT_AND_BACK, GL_LINE)
    else:
        glPolygonMode(GL_FRONT_AND_BACK, GL_FILL)


    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()

    gluPerspective(30, 1, .1, 400)

    # viewing camera
    camera_setting(-30)

    drawFrame()
    drawPlateArray()

    glEnable(GL_LIGHTING)
    glEnable(GL_LIGHT0)
    glEnable(GL_LIGHT1)
    glEnable(GL_NORMALIZE)

    glPushMatrix()
    lightPos0 = (2., 4., 1., 0.)
    glLightfv(GL_LIGHT0, GL_POSITION, lightPos0)
    glPopMatrix()

    glPushMatrix()
    lightPos1 = (0., 100, 0., 1.)
    glLightfv(GL_LIGHT1, GL_POSITION, lightPos1)
    glPopMatrix()

    lightColor0 = (1,1,1,0)
    ambientLightColor = (.1, .1, .1, 0.)
    glLightfv(GL_LIGHT0, GL_DIFFUSE, lightColor0)
    glLightfv(GL_LIGHT0, GL_SPECULAR, lightColor0)
    glLightfv(GL_LIGHT0, GL_AMBIENT, ambientLightColor)

    lightColor1 = (1,1,1,0)
    ambientLightColor = (.1, .1, .1, 1.)
    glLightfv(GL_LIGHT1, GL_DIFFUSE, lightColor1)
    glLightfv(GL_LIGHT1, GL_SPECULAR, lightColor1)
    glLightfv(GL_LIGHT1, GL_AMBIENT, ambientLightColor)


    objectColor = (1,1,0,0)

    specularObjectColor = (1., 1., 1., 1.)
    glMaterialfv(GL_FRONT, GL_AMBIENT_AND_DIFFUSE, objectColor)
    glMaterialfv(GL_FRONT, GL_SHININESS, 5)
    glMaterialfv(GL_FRONT, GL_SPECULAR, specularObjectColor)


    glPushMatrix()
    drawObj_glDrawArray()
    glPopMatrix()

    glDisable(GL_LIGHTING)



# draw primitive and frame

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

def key_callback(window, key, scancode, action, mods):
    global wire_frame, gouraud
    if action == glfw.PRESS or action == glfw.REPEAT:
        if key == glfw.KEY_Z:
            wire_frame = not wire_frame
        elif key == glfw.KEY_S:
            gouraud = not gouraud




def drop_callback(window, path_count, **paths):
    global vn,v, gVertexArraySeparate
    gVertexArraySeparate = None
    v = np.array([0., 0., 0.], 'float32')
    vn = np.array([0., 0., 0.], 'float32')
    gVertexArraySeparate = handle_dropped_file(path_count)

# put all v in v[] and put all vn in vn[]
# following f, put vn and v in varr
# if polygon has 3 vertices, put vn and v in varr
# elif polygon has more vertices,
# split it to several triangles and put vn and v in varr
def handle_dropped_file(path_count):
    global vn, v, glVertexArrayForGouraud, iarr, fn , reset, count_all_num3
    varr = np.array([0, 0, 0], 'float32')
    f = open(path_count[0], 'r')
    face_count=0
    face_3_count = 0
    face_4_count = 0
    face_more_count = 0
    v_count = 0
    count_all_num3 = 0
    while True:
        line = f.readline()
        if not line: break
        if line == '\n':
            continue
        division = line.split()
        if division[0] == 'v':
            v = np.vstack((v, np.array([float(division[1]), float(division[2]), float(division[3])],'float32')))
            v_count += 1
        elif division[0] == 'vn':
            vn = np.vstack((vn, np.array([float(division[1]), float(division[2]), float(division[3])],'float32')))
        elif division[0] == 'f':
            face_count += 1
            f_len = len(division)
            f_division = division[1].split('/')
            f_v0 = int(f_division[0])
            f_vn0 = int(f_division[2])
            if f_len-1 > 3: # if f has more than 3 vertices
                va = f_v0
                vb = 0
                vc = 0
                if f_len == 5: # if vertices are 4
                    face_4_count += 1
                else:
                    face_more_count += 1
                for i in range(2, f_len-1):
                    varr = np.vstack((varr, vn[f_vn0]))
                    varr = np.vstack((varr, v[f_v0]))
                    fn = np.vstack((fn, np.array([float(f_v0), float(f_vn0)], 'float32')))
                    for j in range(i, i+2):
                        f_division = division[j].split('/')
                        f_v = int(f_division[0])
                        f_vn = int(f_division[2])
                        varr = np.vstack((varr, vn[f_vn]))
                        varr = np.vstack((varr, v[f_v]))
                        fn = np.vstack((fn, np.array([float(f_division[0]), float(f_division[2])], 'float32')))
                        if j == i:
                            vb = int(f_division[0])
                        elif j == i+1:
                            vc = int(f_division[0])
                    iarr = np.vstack((iarr, np.array([int(va), vb, vc])))
                    count_all_num3 += 1
            else:
                face_3_count += 1
                va = 0
                vb = 0
                vc = 0
                for i in range(1, f_len):
                    f_division = division[i].split('/')
                    f_v = int(f_division[0])
                    f_vn = int(f_division[2])
                    varr = np.vstack((varr, vn[f_vn]))
                    varr = np.vstack((varr, v[f_v]))
                    fn = np.vstack((fn, np.array([float(f_division[0]), float(f_division[2])], 'float32')))
                    if i == 1:
                        va = int(f_division[0])
                    elif i == 2:
                        vb = int(f_division[0])
                    elif i == 3:
                        vc = int(f_division[0])
                iarr = np.vstack((iarr, np.array([va,vb,vc])))
                count_all_num3 += 1
    f.close()

    iarr = np.delete(iarr, (0), axis=0)
    varr = np.delete(varr, (0), axis=0)
    path_division = path_count[0].split('/')
    print("#############################################")
    print("File name: " + path_division[len(path_division)-1])
    print("Total number of faces : " , face_count)
    print("Number of faces with 3 vertices : ", face_3_count)
    print("Number of faces with 4 vertices : ", face_4_count)
    print("Number of faces with more than 4 vertices : ", face_more_count)
    reset = varr
    return varr


def for_gouraud():
    global iarr, v, count_all_num3

    if v is None:
        return
    narr = []
    normal = []
    for x in range(len(v)):
        normal.append([])

    for i in range(count_all_num3):
        p1 = v[int(iarr[i][0])]
        p2 = v[int(iarr[i][1])]
        p3 = v[int(iarr[i][2])]
        tmp_normal = np.cross(p1-p2, p1-p3)
        tmp_normal = tmp_normal / np.sqrt(np.dot(tmp_normal, tmp_normal))

        for j in range(3):
            normal[int(iarr[i][j])].append(tmp_normal)
    for i in range(len(normal)):
        tmp_sum =[0, 0, 0]
        for j in range(len(normal[i])):
            for k in range(3):
                tmp_sum[k] += np.float32(normal[i][j][k])
        tmp = np.array(tmp_sum)
        tmp = tmp / (np.sqrt(np.dot(tmp, tmp)))
        narr.append(np.float32(tmp))
    return np.array(narr)


def gouraud_shading():
    global fn,v, gVertexArraySeparate, count_all_num3
    if count_all_num3 == 0:
        return
    new_arr = np.array([0., 0., 0], 'float32')
    tmp = for_gouraud()
    print(tmp)
    for i in range(1,len(fn)):
        v_arr = v[int(fn[i][0])]
        n_arr = tmp[int(fn[i][1])]
        new_arr = np.vstack((new_arr, np.array([n_arr[0], n_arr[1], n_arr[2]],'float32')))
        new_arr = np.vstack((new_arr, np.array([v_arr[0], v_arr[1], v_arr[2]],'float32')))
    new_arr = np.delete(new_arr, (0), axis=0)
    gVertexArraySeparate = new_arr




def createVertexArraySeparate():
    varr = np.array([
            (0,0,1),         # v0 normal
            ( -1 ,  1 ,  1 ), # v0 position
            (0,0,1),         # v2 normal
            (  1 , -1 ,  1 ), # v2 position
            (0,0,1),         # v1 normal
            (  1 ,  1 ,  1 ), # v1 position

            (0,0,1),         # v0 normal
            ( -1 ,  1 ,  1 ), # v0 position
            (0,0,1),         # v3 normal
            ( -1 , -1 ,  1 ), # v3 position
            (0,0,1),         # v2 normal
            (  1 , -1 ,  1 ), # v2 position

            (0,0,-1),
            ( -1 ,  1 , -1 ), # v4
            (0,0,-1),
            (  1 ,  1 , -1 ), # v5
            (0,0,-1),
            (  1 , -1 , -1 ), # v6

            (0,0,-1),
            ( -1 ,  1 , -1 ), # v4
            (0,0,-1),
            (  1 , -1 , -1 ), # v6
            (0,0,-1),
            ( -1 , -1 , -1 ), # v7

            (0,1,0),
            ( -1 ,  1 ,  1 ), # v0
            (0,1,0),
            (  1 ,  1 ,  1 ), # v1
            (0,1,0),
            (  1 ,  1 , -1 ), # v5

            (0,1,0),
            ( -1 ,  1 ,  1 ), # v0
            (0,1,0),
            (  1 ,  1 , -1 ), # v5
            (0,1,0),
            ( -1 ,  1 , -1 ), # v4

            (0,-1,0),
            ( -1 , -1 ,  1 ), # v3
            (0,-1,0),
            (  1 , -1 , -1 ), # v6
            (0,-1,0),
            (  1 , -1 ,  1 ), # v2

            (0,-1,0),
            ( -1 , -1 ,  1 ), # v3
            (0,-1,0),
            ( -1 , -1 , -1 ), # v7
            (0,-1,0),
            (  1 , -1 , -1 ), # v6

            (1,0,0),
            (  1 ,  1 ,  1 ), # v1
            (1,0,0),
            (  1 , -1 ,  1 ), # v2
            (1,0,0),
            (  1 , -1 , -1 ), # v6

            (1,0,0),
            (  1 ,  1 ,  1 ), # v1
            (1,0,0),
            (  1 , -1 , -1 ), # v6
            (1,0,0),
            (  1 ,  1 , -1 ), # v5

            (-1,0,0),
            ( -1 ,  1 ,  1 ), # v0
            (-1,0,0),
            ( -1 , -1 , -1 ), # v7
            (-1,0,0),
            ( -1 , -1 ,  1 ), # v3

            (-1,0,0),
            ( -1 ,  1 ,  1 ), # v0
            (-1,0,0),
            ( -1 ,  1 , -1 ), # v4
            (-1,0,0),
            ( -1 , -1 , -1 ), # v7
            ], 'float32')
    return varr


def drawObj_glDrawArray():
    global gVertexArraySeparate
    varr = gVertexArraySeparate
    glEnableClientState(GL_VERTEX_ARRAY)
    glEnableClientState(GL_NORMAL_ARRAY)
    glNormalPointer(GL_FLOAT, 6*varr.itemsize, varr)
    glVertexPointer(3, GL_FLOAT, 6*varr.itemsize, ctypes.c_void_p(varr.ctypes.data + 3*varr.itemsize))
    glDrawArrays(GL_TRIANGLES, 0, int(varr.size/6))



def main():
    global  gVertexArraySeparate,reset
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
    glfw.set_drop_callback(window, drop_callback)
    glfw.set_key_callback(window, key_callback)
    gVertexArraySeparate = createVertexArraySeparate()
    reset = createVertexArraySeparate()

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
