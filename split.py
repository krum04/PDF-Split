import os
import fnmatch
import io
import subprocess
from collections import defaultdict

from PyPDF2 import PdfFileReader, PdfFileWriter
from pdfminer.pdfpage import PDFPage
from pdfminer.pdfinterp import PDFResourceManager
from pdfminer.pdfinterp import PDFPageInterpreter
from pdfminer.converter import TextConverter
import tkinter as tk
from tkinter import ttk
from tkinter import filedialog

import fnmatch
import io
import os
import subprocess
from collections import defaultdict

from PyPDF2 import PdfFileReader, PdfFileWriter
from pdfminer.pdfpage import PDFPage
from pdfminer.pdfinterp import PDFResourceManager
from pdfminer.pdfinterp import PDFPageInterpreter
from pdfminer.converter import TextConverter


def split(pdf, teacherList, exportPath, appendText):

    name_page = defaultdict(list)
    name_list = []  # List of teachers
    splits = []  # Breakpoints in master PDF list
    teacher_list = open(teacherList, 'r')  # Import list of teachers
    teachers = teacher_list.readlines()

    for teacher in teachers:
        name_list.append(teacher.strip('\n'))

    def extract_text_by_page(pdf_path):
        with open(pdf_path, 'rb') as fh:
            for page in PDFPage.get_pages(fh,
                                          caching=True,
                                          check_extractable=True):
                resource_manager = PDFResourceManager()
                fake_file_handle = io.StringIO()
                converter = TextConverter(resource_manager, fake_file_handle)
                page_interpreter = PDFPageInterpreter(
                    resource_manager, converter)
                page_interpreter.process_page(page)

                text = fake_file_handle.getvalue()
                yield text

                # close open handles
                converter.close()
                fake_file_handle.close()

    def extract_text(pdf_path):
        page_count = 1
        for page in extract_text_by_page(pdf_path):
            for name in name_list:
                if name in page:
                    name_page[page_count].append(name)
                    print('{} - {}'.format(page_count, name))
                    statusLabel['text'] = '{} - {}'.format(page_count, name)
                    if page_count-1 not in splits:
                        splits.append(page_count-1)

            page_count = page_count+1
        print(name_page)

        print(splits)

    print(extract_text(pdf))
    pdf_count = 1

    inputpdf = PdfFileReader(open(pdf, "rb"))
    splits.append(inputpdf.numPages)
    output = PdfFileWriter()
    start = splits.pop(0)
    stop = splits.pop(0)
    files = len(splits)+1
    print('start {} stop {}'.format(start, stop))
    while files != 0:
        print('files count: {}'.format(files))
        for page in range(start, stop):
            output.addPage(inputpdf.getPage(page))

        # file_name = str(start+1)
        doc_count = str(pdf_count)
        file_name = doc_count

        for dictpage in name_page[start+1]:
            print('dictpage ' + dictpage)
            file_name = file_name + " " + dictpage

            print(file_name)

            start = stop

        os.chdir(exportPath)

        with open('{}{}.pdf'.format(exportPath+'/'+file_name, str(appendText)), "wb") as outputStream:
            print('{} stop {} written to file {}'.format(
                start, stop, pdf_count))
            output.write(outputStream)
            pdf_count = pdf_count + 1
            output = PdfFileWriter()
            start = stop

            try:
                stop = splits.pop(0)
            except IndexError:
                pass
            files = files - 1

    statusLabel['text'] = "{} PDFs Created".format(pdf_count-1)

    try:
        os.startfile(exportPath)
    except:
        subprocess.Popen(['xdg-open', exportPath])


def pdfPath():  # Create File Dialog to select PDF
    value = filedialog.askopenfilename(
        initialdir=os.getcwd(), title="Select PDF", filetypes=(("pdf files", "*.pdf"), ("all files", "*.*")))
    pdfPathVal = value
    pdfEntry.delete(0, "end")
    pdfEntry.insert(0, value)


def teacherPath():  # Create File Dialog to select TXT
    value = filedialog.askopenfilename(
        initialdir=os.getcwd(), title="Select List", filetypes=(("txt files", "*.txt"), ("all files", "*.*")))
    teacherEntry.delete(0, "end")
    teacherEntry.insert(0, value)


def savePath():  # Create File Dialog to to select export folder
    value = filedialog.askdirectory(
        initialdir=os.getcwd(), title="Export folder")
    saveEntry.delete(0, "end")
    saveEntry.insert(0, value)


# Setup Gui with Tkinter
window = tk.Tk()
window.title("PDF Split")
window.iconbitmap('bannana.ico')
window.columnconfigure(2, weight=1, minsize=75)
window.rowconfigure(5, weight=1, minsize=50)

# PDF Selction
pdfLabel = tk.Label(text='PDF File', anchor="e")
pdfLabel.grid(row=0, column=0, padx=5, pady=5)
pdfEntry = tk.Entry(width=25)
pdfEntry.grid(row=0, column=1, padx=5, pady=5)
pdfButton = tk.Button(text="Select PDF",
                      command=lambda: pdfPath())
pdfButton.grid(row=0, column=2, padx=5, pady=5)

# Teacher List Path
teacherLabel = tk.Label(text='Teacher List', anchor="e")
teacherLabel.grid(row=1, column=0, padx=5, pady=5)
teacherEntry = tk.Entry(width=25)
teacherEntry.grid(row=1, column=1, padx=5, pady=5)
teacherButton = tk.Button(
    text="Select List", command=lambda: teacherPath())
teacherButton.grid(row=1, column=2, padx=5, pady=5)

# Teacher List Path
saveLabel = tk.Label(text='Export Location', anchor="e")
saveLabel.grid(row=2, column=0, padx=5, pady=5)
saveEntry = tk.Entry(width=25)
saveEntry.grid(row=2, column=1, padx=5, pady=5)
saveButton = tk.Button(text="Select Location",
                       command=lambda: savePath())
saveButton.grid(row=2, column=2, padx=5, pady=5)

# Append filename
appendLabel = tk.Label(text="Append Text", anchor="e")
appendLabel.grid(row=3, column=0,)
appendEntry = tk.Entry(width=25)
appendEntry.grid(row=3, column=1)

# Status Label
statusLabel = tk.Label(text='')
statusLabel.grid(row=5, column=1, padx=5, pady=5)

# Split Button
splitButton = tk.Button(text="Split Now", command=lambda: split(
    pdfEntry.get(), teacherEntry.get(), saveEntry.get(), appendEntry.get()))
splitButton.grid(row=4, column=1, padx=5, pady=5)

window.mainloop()
