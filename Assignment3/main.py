import numpy as np
import glfw
from OpenGL.GL import *
from OpenGL.GLU import *

# for camera viewer
gCamAng = 0.
buttonpress = 0.
xpos_start = 0.
ypos_start = 0.
x_for_panning = 0.
y_for_panning = 0.
trans_store = np.identity(4)
height_store = np.identity(4)
zoom = 0

# for bvh viewer
hierarchy = []
motion = []
frame_count = 0
frame_time = 0
joint_count = 1
joint_name = []
channel_count = 0
frame_index = 0
file_check = False
do_animate = False
max_len = np.array([0., 0., 0.])
local_max = np.array([0., 0., 0.])
base_time = 1


def render(camAng):
    global lightcolor, hierarchy, file_check, channel_count
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glEnable(GL_DEPTH_TEST)

    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluPerspective(30, 1, .1, 400)

    # viewing camera
    camera_setting(-30)

    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()

    drawFrame()
    drawPlateArray()

    glEnable(GL_LIGHTING)
    glEnable(GL_LIGHT0)
    glEnable(GL_NORMALIZE)

    glPushMatrix()
    lightPos0 = (-2., 4., 1., 0.)
    glLightfv(GL_LIGHT0, GL_POSITION, lightPos0)
    glPopMatrix()

    lightColor0 = (1, 1, 1, 0)
    ambientLightColor = (.1, .1, .1, 0.)
    glLightfv(GL_LIGHT0, GL_DIFFUSE, lightColor0)
    glLightfv(GL_LIGHT0, GL_SPECULAR, lightColor0)
    glLightfv(GL_LIGHT0, GL_AMBIENT, ambientLightColor)

    objectColor = (1, 1, 1, 0)

    specularObjectColor = (1., 1., 1., 1.)
    glMaterialfv(GL_FRONT, GL_AMBIENT_AND_DIFFUSE, objectColor)
    glMaterialfv(GL_FRONT, GL_SHININESS, 5)
    glMaterialfv(GL_FRONT, GL_SPECULAR, specularObjectColor)

    if file_check:
        channel_count = 0
        draw_hierarchy(hierarchy)

    glDisable(GL_LIGHTING)




# draw primitive and frame

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





# camera setting
# manipulate the camera with mouse movement

def camera_setting(first):
    global trans_store, height_store, zoom

    glTranslate(0, 0, first + zoom)
    # move camera
    x = height_store @ trans_store
    glMultMatrixf(x.T)


# for left button click
def cursor_callback1(window, xpos, ypos):
    global xpos_start, ypos_start, gCamAng, trans_store, height_store

    gCamAng = -(np.radians(xpos_start - xpos)) / 1.5
    height = -(np.radians(ypos_start - ypos)) / 1.5
    xpos_start = xpos
    ypos_start = ypos
    rotation_matrix = np.array([[np.cos(gCamAng), 0., np.sin(gCamAng), 0.],
                                [0., 1., 0., 0.],
                                [-np.sin(gCamAng), 0., np.cos(gCamAng), 0.],
                                [0., 0., 0., 1.]])

    height_matrix = np.array([[1., 0., 0., 0.],
                              [0., np.cos(height), -np.sin(height), 0.],
                              [0., np.sin(height), np.cos(height), 0.],
                              [0., 0., 0., 1.]])
    trans_store = rotation_matrix @ trans_store
    height_store = height_matrix @ height_store


# for right button click
def cursor_callback2(window, xpos, ypos):
    global x_for_panning, y_for_panning, gCamAng, trans_store, height_store

    now_panning_x = (- x_for_panning + xpos) / 40
    now_panning_y = (- y_for_panning + ypos) / 40

    panning_matrix_x = ([[1., 0., 0., now_panning_x],
                         [0., 1., 0., 0.],
                         [0., 0., 1., 0.],
                         [0., 0., 0., 1.]])

    panning_matrix_y = ([[1., 0., 0., 0.],
                         [0., 1., 0., -now_panning_y],
                         [0., 0., 1., 0.],
                         [0., 0., 0., 1.]])
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
    zoom = zoom + yoffset / 3




# key callback for do animate.
# if put space bar, change to do animate or not
def key_callback(window, key, scancode, action, mods):
    global do_animate, base_time
    if action == glfw.PRESS or action == glfw.REPEAT:
        if key == glfw.KEY_SPACE:
            if do_animate is True:
                do_animate = False
                base_time = 1
            else:
                do_animate = True
                base_time = glfw.get_time()




# draw obj using box
#
def drawCube(offset, normal):
    glBegin(GL_QUADS)
    glNormal3f(0, normal[1], 0)
    glVertex3f(offset[0], offset[1], - offset[2])
    glVertex3f(- offset[0], offset[1], - offset[2])
    glVertex3f(- offset[0], offset[1], offset[2])
    glVertex3f(offset[0], offset[1], offset[2])

    glNormal3f(0, -normal[1], 0)
    glVertex3f(offset[0], - offset[1], offset[2])
    glVertex3f(- offset[0], - offset[1], offset[2])
    glVertex3f(- offset[0], - offset[1], - offset[2])
    glVertex3f(offset[0], - offset[1], - offset[2])

    glNormal3f(0, 0, normal[2])
    glVertex3f(offset[0], offset[1], offset[2])
    glVertex3f(- offset[0], offset[1], offset[2])
    glVertex3f(- offset[0], - offset[1], offset[2])
    glVertex3f(offset[0], - offset[1], offset[2])

    glNormal3f(0, 0, -normal[2])
    glVertex3f(offset[0], - offset[1], - offset[2])
    glVertex3f(- offset[0], - offset[1], - offset[2])
    glVertex3f(- offset[0], offset[1], - offset[2])
    glVertex3f(offset[0], offset[1], - offset[2])

    glNormal3f(-normal[0], 0, 0)
    glVertex3f(- offset[0], offset[1], offset[2])
    glVertex3f(- offset[0], offset[1], - offset[2])
    glVertex3f(- offset[0], - offset[1], - offset[2])
    glVertex3f(- offset[0], - offset[1], offset[2])

    glNormal3f(normal[0], 0, 0)
    glVertex3f(offset[0], offset[1], - offset[2])
    glVertex3f(offset[0], offset[1], offset[2])
    glVertex3f(offset[0], - offset[1], offset[2])
    glVertex3f(offset[0], - offset[1], - offset[2])
    glEnd()


# get offset and normal for drawing cube
def get_offset(offset):
    temp = [0., 0., 0.]
    if offset[0] > 0:
        temp[0] = offset[0] + 0.02
    elif offset[0] < 0:
        temp[0] = offset[0] - 0.02
    else:
        temp[0] = 0.02

    if offset[1] > 0:
        temp[1] = offset[1] + 0.02
    elif offset[1] < 0:
        temp[1] = offset[1] - 0.02
    else:
        temp[1] = 0.02

    if offset[2] > 0:
        temp[2] = offset[2] + 0.02
    elif offset[2] < 0:
        temp[2] = offset[2] - 0.02
    else:
        temp[2] = 0.02
    normal = [temp[0] / abs(temp[0]), temp[1] / abs(temp[1]), temp[2] / abs(temp[2])]

    return temp, normal




# drawing obj
# parsing BVH file
#
# divide hierarchy part and store it
def set_hierarchy(f, head):
    global joint_count, joint_name, local_max, max_len

    local_max = np.array([0., 0., 0.])
    joint = []
    joint.append(head)
    current_head = head

    while True:
        line = f.readline()
        if not line:
            break
        line = line.strip()
        line = line.replace('\t', ' ')
        tag = line.split(' ', 1)

        if tag[0] == 'ROOT':
            current_head = 'R'
        elif tag[0] == 'JOINT':
            current_head = 'J'
            joint_count += 1
            joint_name.append(tag[1])
        elif tag[0] == 'End':
            current_head = 'E'
        elif tag[0] == 'OFFSET':
            offset = tag[1].split(' ')
            offset_arr = np.array([np.float32(offset[0]), np.float32(offset[1]), np.float32(offset[2])])
            local_max += offset_arr
            joint.append(offset_arr)
        elif tag[0] == 'CHANNELS':
            num = tag[1].split(' ', 1)
            channels = num[1].split(' ')
            joint.append(channels)
        elif tag[0] == '{':
            child = set_hierarchy(f, current_head)
            joint.append(child)
        elif tag[0] == '}':
            max_len += abs(local_max)
            return joint

# store motion part
def set_motion(f):
    motions = []
    while True:
        temp = []
        line = f.readline()
        if not line:
            break
        line = line.rstrip()
        line = line.replace('\t', ' ')
        line = line.replace('\n', ' ')
        frame_motion = line.split(' ')
        for i in range(len(frame_motion)):
            temp.append(np.float32(frame_motion[i]))
        motions.append(temp)
    return motions


def draw_hierarchy(input):
    global hierarchy, channel_count, motion, frame_index, do_animate, frame_count, max_len, frame_time, base_time

    model_len = max_len
    tag = input[0]
    offset = input[1]
    offset = offset / model_len

    glPushMatrix()

    temp = [offset[0]/2, offset[1]/2, offset[2]/2]
    temp_offset, normal = get_offset(temp)
    glTranslate(offset[0]/2, offset[1]/2, offset[2]/2)
    drawCube(temp_offset, normal)
    glTranslate(offset[0]/2, offset[1]/2, offset[2]/2)

    frame_index = int(((glfw.get_time() - base_time) / frame_time) % frame_count)

    if tag != 'E':
        child_num = len(input) - 3
        channel = input[2]
        if do_animate:
            for i in range(len(channel)):
                if channel[i].upper() == 'XPOSITION':
                    xpos = motion[frame_index][channel_count]
                    xpos = xpos / model_len[0]
                    channel_count += 1
                    glTranslate(xpos, 0, 0)
                elif channel[i].upper() == 'YPOSITION':
                    ypos = motion[frame_index][channel_count]
                    ypos = ypos / model_len[1]
                    channel_count += 1
                    glTranslate(0, ypos, 0)
                elif channel[i].upper() == 'ZPOSITION':
                    zpos = motion[frame_index][channel_count]
                    zpos = zpos / model_len[2]
                    channel_count += 1
                    glTranslate(0, 0, zpos)
                elif channel[i].upper() == 'XROTATION':
                    xrot = motion[frame_index][channel_count]
                    channel_count+= 1
                    glRotate(xrot, 1, 0, 0)
                elif channel[i].upper() == 'YROTATION':
                    yrot = motion[frame_index][channel_count]
                    channel_count += 1
                    glRotate(yrot, 0, 1, 0)
                elif channel[i].upper() == 'ZROTATION':
                    zrot = motion[frame_index][channel_count]
                    channel_count += 1
                    glRotate(zrot, 0, 0, 1)
        for i in range(child_num):
            draw_hierarchy(input[i + 3])

    glPopMatrix()




# handle drop file
# initialize
# divide hierarchy part and motion part
def drop_callback(window, path_count, **paths):
    global hierarchy, motion, frame_count, frame_time, joint_count, joint_name, file_check, max_len, base_time

    path_division = path_count[0].split('/')
    file_name = path_division[len(path_division) - 1]
    f = open(path_count[0], 'r')
    file_check = True
    hierarchy = []
    motion = []
    frame_count = 0
    frame_time = 0
    joint_count = 1
    joint_name = []
    max_len = np.array([0., 0., 0.])

    while True:
        line = f.readline()
        if not line:
            break
        line = line.rstrip()

        tag = line.split(' ', 1)
        if tag[0] == 'HIERARCHY':
            line = f.readline()
            line = line.rstrip()
            line = line.replace('\t', ' ')
            root = line.split(' ', 1)
            joint_name.append(root[1])
            f.readline()
            hierarchy = set_hierarchy(f, 'R')
        elif tag[0] == 'MOTION':
            line = f.readline()
            line = line.rstrip()
            line = line.replace('\t', ' ')
            tag = line.split(' ', 1)
            frame_count = int(tag[1])

            line = f.readline()
            line = line.rstrip()
            line = line.replace('\t', ' ')
            tag = line.split(' ', 2)
            frame_time = np.float32(tag[2])
            motion = set_motion(f)

    print("#############################################")
    print("File name : ", file_name)
    print("Number of frames : ", frame_count)
    print("FPS (which is 1/FrameTime) : ", 1 / frame_time)
    print("Number of joints (including root) : ", joint_count)
    print("List of all joint names : ", joint_name)
    base_time = glfw.get_time()




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

    glfw.set_mouse_button_callback(window, button_callback)
    glfw.set_scroll_callback(window, scroll_callback)
    glfw.set_drop_callback(window, drop_callback)
    glfw.set_key_callback(window, key_callback)

    # Loop until the user closes the window
    while not glfw.window_should_close(window):
        # Poll for and process events
        glfw.poll_events()
        render(gCamAng)
        glfw.swap_interval(1)

        # Swap front and back buffers
        glfw.swap_buffers(window)

    glfw.terminate()


if __name__ == "__main__":
    main()

