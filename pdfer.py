
from pypdf import PdfReader, PdfWriter, Transformation
from datetime import datetime
from reportlab.pdfgen.canvas import Canvas
import os, io
from db_lib import get_res_info
from pathlib import Path


TMP_DIR = Path("/tmp")

# Credit to Author of following class
# https://medium.com/@sarumathyprabakaran
class GenerateFromTemplate:
    def __init__(self,template):
        self.template_pdf = PdfReader(open(template, "rb"))
        self.template_page= self.template_pdf.pages[0]

        self.packet = io.BytesIO()
        self.c = Canvas(self.packet,pagesize=(self.template_page.mediabox.width,self.template_page.mediabox.height))


    def addText(self,text,point):
        self.c.drawString(point[0],point[1],text)

    def merge(self):
        self.c.save()
        self.packet.seek(0)
        result_pdf = PdfReader(self.packet)
        result = result_pdf.pages[0]

        self.output = PdfWriter()

        op = Transformation().rotate(0).translate(tx=0, ty=0)
        result.add_transformation(op)
        self.template_page.merge_page(result)
        self.output.add_page(self.template_page)

    def generate(self,dest):
        outputStream = open(dest,"wb")
        self.output.write(outputStream)
        outputStream.close()



def esign(id, renter_name, date):
    print('Hello')

# generate new rental agreement for a given reservation/booking id
# should only be done once... probably
def gen(id, renter_name, eq_dict, signed=False):

    gen_date = datetime.today()
    gen = GenerateFromTemplate("pdf_templates/ERA-1.0-TEMPLATE.pdf")

    res_info = get_res_info(id)

    # add day
    gen.addText(str(gen_date.day),(260, 671))

    # add month
    gen.addText(gen_date.strftime('%B'),(335, 671))

    # add year (last 2 digits)
    gen.addText(gen_date.strftime('%y'),(109, 656))

    # add renter name
    gen.addText(renter_name,(260, 656))


    eq = res_info['equipment'].split('_')
    i=480
    for p in eq:
         # add equipment
        gen.addText(p,(90, i))
        i -= 16

     # add rental location
    gen.addText(res_info['address1'],(163, 465))
    gen.addText(res_info['city'] + ',  ' + res_info['state'] ,(163, 449))
    gen.addText(res_info['zip'],(163, 433))

    n_days = res_info['n_days']
    n_weeks = res_info['n_weeks']

    if n_weeks != 0:
         # add duration
        gen.addText(str(n_weeks),(255, 465))
         # add rental rate per article
        gen.addText(str(eq_dict[res_info['equipment']]['ppw']),(335, 465))
        # add rental rate unit
        gen.addText("Weekly",(425, 465))
        
    if n_days != 0:
         # add duration
        gen.addText(str(n_days),(255, 480))
         # add rental rate per article
        gen.addText(str(eq_dict[res_info['equipment']]['ppd']),(335, 480))
        # add rental rate unit
        gen.addText("Daily",(425, 480))

    # lessor Print name
    gen.addText("Ryan McClellan, VP",(140, 271))

    # lessee Print name
    gen.addText(renter_name,(140, 215))

    if signed == True:
        # lessee signed name
        gen.addText(renter_name + ' (e-sig ' + datetime.now().strftime("%Y-%m-%d %H:%M:%S") + ')',(140, 187))

    gen.merge()

    fname = id + ".pdf"

    gen.generate(TMP_DIR / fname)
    append_content(id)



def append_content(id):
    merger = PdfWriter()

    fname = id + ".pdf"

    for pdf in [ TMP_DIR / fname, "pdf_templates/ERA-1.0-TEMPLATE_CONTENT.pdf"]:
        merger.append(pdf)

    merger.write(TMP_DIR / fname)
    merger.close()
