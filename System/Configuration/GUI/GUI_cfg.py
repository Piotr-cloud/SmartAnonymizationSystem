'''
Created on Jun 25, 2022

@author: piotr
'''
from NonPythonFiles import editorOptions_dir
from pathlib import Path


_version_ = (1,0)
debug = False


############################################################################
#  Gui pannel options
############################################################################

options_fn = editorOptions_dir / "Prcessing_configuration_editor_options.json"

defaultOpt = {
    'dir': str(Path(__file__).parent.parent.parent.parent / "userFiles/cfg"), # last seen directory
    'geometry': "1475x860+120+60",
    'save_position': True, # save the geometry and position of the window and restore on next load
    'MS_format_output': True, # convert output to microsoft .NET style
    'formats': '.editConfig .xml', # extensions of DefaultFiles to be listed; space delimited
    'entrybox_width': 25,  # width of the entry boxes
    'output_encoding': 'autodetect', # any valid encoding ('utf-8', 'utf-16le', etc) or autodetect.
    'backup_ext': '.bak', # extension of backed up DefaultFiles. Use something not in 'formats' to prevent backups from showing in the dropdown list.
    }


############################################################################
#  Pixels positioning
############################################################################

# Line
LINE_ELEMENTS_DISTANCE = 20
LINE_HEIGHT = 50
DISTANCE_LINE_HEIGHT = 40

# Ascii sign
ASCII_SIGN_WIDTH    =  25
ASCII_SIGN_HEIGHT   =  25


# Dummies
EMPTY_LINE_WIDTH = 1


# Frame
FRAME_BASELINE_TO_SUBELEMENTS_DISTANCE = 20 
FRAME_SUBELEMENTS_VERTICAL_DISTANCE = 10

FRAME_TOP_PADDING = 10
FRAME_BOTTOM_PADDING = 10

FRAME_LEFT_PADDING = 5
FRAME_RIGHT_PADDING = 5


# Indent
CONTEXT_INDENT_WIDTH = 20


# Entry
ENTRY_MIN_WIDTH = 200


# Main window px start position
MAIN_WINDOW_START_X = 120
MAIN_WINDOW_START_Y = 120


# Button
BUTTON_HEIGHT  = 150
BUTTON_WIDTH   = 300

############################################################################
#  Signs
############################################################################


# Segment label
SEGMENT_LABEL_OPEN_STATEMENT_SIGN  =  "<"
SEGMENT_LABEL_END_STATEMENT_SIGN   =  ">"





# Special signs

SQUARE_EMPTY    =  '\u25fb'
SQUARE_FILLED   =  '\u25fc'

SQUARE_EMPTY_2  =  '\u25fd'
SQUARE_FILLED_2 =  '\u25fe'

CIRCLE_EMPTY    =  '\u25cb'
CIRCLE_FILLED   =  '\u25cf'
CIRCLE_DOTTED   =  '\u25ce'

BULLET          =  '\u2022'
ARROW           =  '\u2794'




############################################################################
#  icon as a base64 encoded gif.
############################################################################
icondata = """
R0lGODlhgACAAOf/AAABAAYDCQAFCAMKDQkMCA4LEAMOFQsMFQsQExARGQoTGQ4SHRAXHRIWIg4Y
IhYYFhUYGhYaJRoeKRYgKh4fIh4gHRggMBwjLhsjMyIjISElJyElLCclKR8nNyYnJSMqOiQsNyEt
QiktMiwtKycuPyYyRzAyLyk0SS41PDM2OC44Qyw4TTE4Sjc5Nio7VTA7US4+WTY/SjQ/VT0/PD4/
QkBCPzNDXkFCSjZGYUVHREBHWDVKajtKZj9KYUhKR0dLTUdLUz5OaTpPb0RPZlBOUE5QTT5Tc0tS
WUJWd05WYlRWU0hXcVRXWUVZek5YakBagERehFtcWkpef1VecFBffFxfYkhiiEZijlhgbVlhaGBi
X1hje0xmjEhnk09lk2dlaVBpkFZoiWZnZWNoamJqcWNqeE5tml9rfVNtlFhtnF9tiWttampucVdw
l3BtcVNynm5wbWhxf1Z0oV5zoll0qHJ0cV12nnZzd1p4pnZ3dGh5k117qHl6d2Z7ql99q2F8sHx6
fm18mnR8i3t8eWh9rGKArWR/s3l+gX1+fF6CtYF+gmSCsIN+fX6AfWaDsWGEt3+BfnSDoWmEuYGD
gIeCgWOHum+FrIWDh32FjICFh2aJvW2IvX6Hl4aIhWmMwHGLwImLiGuPw4aNlY2NkG6RxnSSwXaR
x46QjYKRsHuUvXOWym6X0XaV0ZOVkpaUmYmWrHGa1HiY1HeZzpaYlXSd13ub14+ap3qgzneg2n+e
2pudmp+doXqj3YKh3pyhpJ+hnn6m4Yal4pulsIKq5YSp66amqqWnpICv8Imt8KqsqYiw64ux36+t
saivtIWz9I2x9LCyr4y37I628Ym3+JG1+JO3+q62vrG2uI+5/7e1uZW5/LW3tJC9/5i+7ZbB9ry9
urm+wb+9wcDCv8fCwaHN+MvGxMbIxMnIzMnLyNDSz87S1dvX2Nja197g3ePg5d3i5enj4uPl4ujp
5uvp7ezu6/Dy7/Ty9vH2+fX28/759/n79/b8/v77//z++/7//P///yH5BAEKAP8ALAAAAACAAIAA
AAj+AP8JHEiwoMGDCBMqXMiwocOHECNKnEixosWLGC9isGAho8ePICV+CNEBA4aQKFOq/OfCRYgV
NkKsnElzYggbT3Ag8SRHZs2fQBGG+GDFzJtctMAEXfqRI0McDWC82USs1iobTLNW7FByo0IrISZY
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
277928Ad3MI93MRd3AEBADs=
"""