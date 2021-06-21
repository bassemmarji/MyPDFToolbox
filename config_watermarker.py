#The configuration parameters of our watermark
###############################################

#The size of the page supposedly A4
from reportlab.lib.pagesizes import A4
#The color of the watermark
from reportlab.lib.colors import red

PAGESIZE = A4
FONTNAME = 'Helvetica-Bold'
FONTSIZE = 40
COLOR = red

#The position attributes of the watermark
X = 250
Y = 10

#The rotation angle in order to display the watermark diagonally if needed
ROTATION_ANGLE=45