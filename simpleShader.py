import pygloo
from pygloo import *
from ctypes import *


'''
Use example:

prog = makeProgram('330 compatibility', [GL_VERTEX_SHADER, GL_GEOMETRY_SHADER, GL_FRAGMENT_SHADER], shader_source)

'''

class ShaderError(Exception):
    def __init__(self, msg = 'Generic shader error'):
        Exception.__init__(self, msg)
    # }
# }

class ShaderCompileError(ShaderError):
    def __init__(self, msg = 'Shader compilation failed'):
        ShaderError.__init__(self, msg)
    # }
# }

class ShaderLinkError(ShaderError):
    def __init__(self, msg = 'Shader program linking failed'):
        ShaderError.__init__(self, msg)
    # }
# }

def printShaderInfoLog(gl, obj):
    loglen = GLint(0)
    gl.glGetShaderiv(obj, GL_INFO_LOG_LENGTH, loglen)
    if loglen > 1:
        log = create_string_buffer(loglen.value)
        loglen2 = GLint(0)
        gl.glGetShaderInfoLog(obj, loglen, loglen2, log)
        print 'Shader:\n', log.value
    # }
# }

def printProgramInfoLog(gl, obj):
    loglen = GLint(0)
    gl.glGetProgramiv(obj, GL_INFO_LOG_LENGTH, loglen)
    if loglen > 1:
        log = create_string_buffer(loglen.value)
        loglen2 = GLint(0)
        gl.glGetProgramInfoLog(obj, loglen, loglen2, log)
        print 'Program:\n', log.value
    # }
# }

def compileShader(gl, stype, text):
    shader = gl.glCreateShader(stype)
    text = create_string_buffer(text)
    ptext = cast(pointer(text), POINTER(c_char))
    gl.glShaderSource(shader, 1, pointer(ptext), POINTER(GLint)())
    try:
        gl.glCompileShader(shader)
    except GLError:
        pass
    # }
    compile_status = GLint(0)
    gl.glGetShaderiv(shader, GL_COMPILE_STATUS, compile_status)
    printShaderInfoLog(gl, shader)
    if not compile_status.value:
        raise ShaderCompileError()
    # }
    return shader
# }

def linkProgram(gl, prog):
    try:
        gl.glLinkProgram(prog)
    except GLError:
        pass
    # }
    link_status = GLint(0)
    gl.glGetProgramiv(prog, GL_LINK_STATUS, link_status)
    printProgramInfoLog(gl, prog)
    if not link_status.value:
        raise ShaderLinkError()
    # }
# }

def makeProgram(gl, profile, stypes, source):
    prog = gl.glCreateProgram()
    defines = dict({
        (GL_VERTEX_SHADER, '_VERTEX_'),
        (GL_GEOMETRY_SHADER, '_GEOMETRY_'),
        (GL_TESS_CONTROL_SHADER, '_TESS_CONTROL_'),
        (GL_TESS_EVALUATION_SHADER, '_TESS_EVALUATION_'),
        (GL_FRAGMENT_SHADER, '_FRAGMENT_')
    })
    for stype in stypes:
        text = '#version {profile}\n#define {sdef}\n{source}'.format(profile=profile, sdef=defines[stype], source=source)
        shader = compileShader(gl, stype, text)
        gl.glAttachShader(prog, shader)
    # }
    linkProgram(gl, prog)
    print 'Shader program compiled and linked successfully'
    return prog
# }