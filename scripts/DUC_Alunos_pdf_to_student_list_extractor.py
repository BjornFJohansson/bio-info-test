#!/home/bjorn/anaconda3/envs/bjorn36/bin/python
# -*- coding: utf-8 -*-

import PyPDF2
import sys
import subprocess
import re
import time
pdf = sys.argv[1]
from pdfrw import PdfReader
x = PdfReader(pdf)
from pdfrw import PdfWriter
y = PdfWriter()
y.addpages(x.pages)
y.write(pdf)    
pdf = PyPDF2.PdfFileReader(open(pdf, "rb"))
text = ""
for i in range(0, pdf.getNumPages()):
    extractedText = pdf.getPage(i).extractText()
    text +=  extractedText
    
#print(text)
#Number 65027
#Name Bárbara Filipa Cerqueira Bernardino
#Email A65027@alunos.uminho.pt
#Course Engenharia Biológica
#Enrolled SAUM No
#regex = u"Number(.+?)Name(.+?)Email(.+?)Course(.+?)Enrolled SAUM(Yes|No)"
#regex = "Número(.+?)Nome(.+?)Email(.+?)Curso(.+?)Inscrito SAUM(Sim|Não)"
regex = u"Number(?:[^0-9])*([0-9]+?)Name(.+?)Email(.+?)Course(.+?)Enrolled SAUM(Yes|No)"
match = re.findall(regex, text)
print("Name,Number")
for m in match:
    print("{}, {}".format(m[1], m[0]))
