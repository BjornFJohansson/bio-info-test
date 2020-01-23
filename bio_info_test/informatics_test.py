#!/home/bjorn/anaconda3/envs/bjorn36/bin/python
# -*- coding: utf-8 -*-

"""
informatics_test

Usage: informatics_test create_settings [<test_folder>]
       informatics_test create_folders [<test_folder>]
       informatics_test parse_students [<path_student_list_file>]
       informatics_test generate_tests
       informatics_test rename_completed_tests [<returned_exam_folder>]      
       informatics_test correct_tests [<question_numbers>...]
       informatics_test generate_spreadsheet <correction_folder>
       informatics_test -h|--help
       informatics_test -v|--version

Arguments:
    <path_student_list_file>  path to data file containing csv Name,Number of each student.


Options:
    -h, --help      Show this screen.
    -v, --version   Show version.
"""
__version__="0.01"

import re
import codecs
import string
import sys
import os
import pathlib
import docopt      # https://github.com/Infinidat/infi.docopt_completion/
import time
import subprocess
import shelve
import shutil
import secrets
import collections
import textwrap
from hashlib import md5
import chardet
from pyparsing import Literal, Word, nums, restOfLine, alphanums, Optional, LineEnd, SkipTo
from ezodf import newdoc, Sheet

def parse_student_file(filename):

    rows = sorted(codecs.open(filename,"r","utf-8").readlines()[1:])

    names, mecs = [],[]
    undefined_mec = 0

    for row in rows:
        if row.startswith("#"):
            continue
        if row.strip():
            row = "".join(x for x in row if x not in string.punctuation)
            mec=re.search("[\d|a|A|e|E]\d{4,5}",row)
            if mec:
                mec=mec.group(0)
            else:
                undefined_mec+=1
                mec="NA"+str(undefined_mec)
            name = re.sub("[\d|a|A|e|E]\d{4,5}","",row).strip()
            name = re.sub("ORD","",name).strip()
            name = re.sub("T-E","",name).strip()
            if mec in mecs:
                print(mec,names[mecs.index(mec)])
                print(mec,name)
                raise ValueError("two entries with the same number!")
            names.append(name)
            mecs.append(mec)
    assert len(mecs)==len(names)
    return mecs,names


def create_settings(directory):
    settings_path = pathlib.Path("settings.py")
    if not settings_path.exists():
        template = textwrap.dedent("""\
        #!/usr/bin/env python
        # -*- coding: utf-8 -*-
        
        shelf_folder                    = "shelf"
        exam_folder                     = "empty_exams"
        correct_exam_folder             = "correct_exams"
        returned_exam_folder            = "returned_exams"
        student_list_file               = "students.txt"
        correction_folder               = "correction_"
        
        from bioinformatics_questions import (  blunt_cloning,
                                                change_origin,
                                                change_origin_rc,
                                                circular_permutations,
                                                extract_compound_feature,
                                                extract_compound_feature_rc,
                                                find_feature,
                                                find_feature_rc,
                                                find_low_complexity,
                                                find_prosite_pattern,
                                                find_region_of_similarity,
                                                find_repeated_sequences,
                                                gibson_linear,
                                                pcr_cloning,
                                                pcr_primer_design,
                                                reverse_complement,
                                                size,
                                                tailed_primers,
                                                gel_interpretation)
        
        q = [ blunt_cloning.question(2),
              #change_origin.question(1),
              change_origin_rc.question(1),
              #circular_permutations.question(2),
              #extract_compound_feature.question(2),
              extract_compound_feature_rc.question(2),
              #find_feature.question(2),
              find_feature_rc.question(2),
              #find_low_complexity.question(2),
              #find_prosite_pattern.question(2),
              #find_region_of_similarity.question(2),
              #find_repeated_sequences.question(2),
              gibson_linear.question(4),
              pcr_cloning.question(6),
              pcr_primer_design.question(2),
              #reverse_complement.question(1),
              size.question(1),
              tailed_primers.question(2),
              #gel_interpretation.question(2)
              ]
        
        additional_included_files       = ["/home/bjorn/python_packages/bioinformatics_questions/bioinformatics_questions/files_to_be_included/pUC19.txt"]

        uuidpat                         = "[a-f0-9]{8}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{12}"
        question_separator              = "\\n*********** Question {} ***********\\n"
        endseparator                    = "\\n========== end of exame ========================================================"
        
        header = '''================================================================================
        BMA19 | Biologia Molecular Aplicada 9505N3 | 2019-12-12 | Unix timestamp {timestamp}
        Nome                       {name}
        Número mecanográfico (mec) {mec}        
        ================================================================================
        
        Instruções:
        ----------
        
        - Preencha a sua resposta, substituindo o simbolo "?" dentro neste documento.
        
        - Por favor NÂO MODIFIQUE MAIS NADA, será corrigido automaticamente.
          em particular, não modifique ou remova o QuestionID, que serve para identificar
          as respostas certas.
        
        - Quando estiver pronto, escreva a soma de verificação MD5 deste ficheiro no formulário MD5.
        
        - Envie este ficheiro para bjornjobb+test@gmail.com
        
        Instructions:
        ------------
        
        - Fill in your answers where you find the "?" symbol(s) in each question within this document.
        
        - Please do not edit anything else, as this test will be automatically corrected.
          In particular, do NOT modify the QuestionID as this is used for identifying the
          correct answer.
        
        - When you are ready, write the MD5 checksum of *this* file on the MD5 form.
        
        - Send this file to bjornjobb+test@gmail.com
        '''
        """)
       
        settings_path.write_text(template)
    else:  
        print("settings.py already exists.")

def create_folders(directory):
    settings_path = pathlib.Path("settings.py")
    if settings_path.exists():  
        vardict= {}         
        with open(settings_path) as f:
            code = compile(f.read(), settings_path.name, 'exec')
        exec(code, vardict)
        pathlib.Path(vardict["shelf_folder"]).mkdir(exist_ok=True)
        pathlib.Path(vardict["exam_folder"]).mkdir(exist_ok=True)
        pathlib.Path(vardict["correct_exam_folder"]).mkdir(exist_ok=True)
        pathlib.Path(vardict["returned_exam_folder"]).mkdir(exist_ok=True)
        students_path = pathlib.Path(vardict["student_list_file"])
        if not students_path.exists():
            students_path.write_text("Name,Number\nMax Maximus,99999")
    else:
        print("No settings.py found. run option 'create_settings'")

def parse_students(student_list_file):
    if not student_list_file:
        settings_path = pathlib.Path("settings.py")
        vardict= {}       
        with open(settings_path) as f:
            code = compile(f.read(), settings_path.name, 'exec')
        exec(code, vardict)
            
    mecs,names = parse_student_file(vardict["student_list_file"])
    print("Name,Number")
    for mec,name in zip(mecs,names):
        print(f"{name},{mec[:]}")
    print("# totally", len(mecs), "students")
    

def generate_tests():
    settings_path = pathlib.Path("settings.py")
    vardict= {}       
    with open(settings_path) as f:
        code = compile(f.read(), settings_path.name, 'exec')
    exec(code, vardict)
    q                         =vardict["q"]                       
    shelf_folder              =vardict["shelf_folder"]       
                                                       
    student_list_file         =vardict["student_list_file"]         
    additional_included_files =vardict["additional_included_files"] 
    exam_folder               =vardict["exam_folder"]               
    correct_exam_folder       =vardict["correct_exam_folder"]       
                                                       
    header                    =vardict["header"]                    
    question_separator        =vardict["question_separator"]        
    endseparator              =vardict["endseparator"]   
    
    mecs, names = parse_student_file(vardict["student_list_file"])
    
    studentlist = list(zip(mecs,names))
    
    shelfpath = pathlib.Path(shelf_folder) / "shelf.shelf"
    
    shelf = shelve.open(str(shelfpath))
    

    alphabet = string.ascii_lowercase + string.digits
    password = ''.join(secrets.choice(alphabet) for i in range(5))
    
    for student in studentlist:
        timestamp = int(time.time())
        mec, name = student
        filename = "{}_{}".format(name.replace(" ","_"),mec)
        print(f"Preparing {filename}")
        exam_path = pathlib.Path(exam_folder)/filename
        if exam_path.with_suffix(".zip").exists():
            print(f"{exam_path} already exists, skipping.")
            continue
        
        empty_exam = header.format( name=name,
                                    mec=mec,
                                    timestamp=timestamp,
                                    question_separator=question_separator,
                                    number_of_questions=len(q) )
    
        correct_exam = empty_exam
    
        exam_included_files = []
        
        for i in q:
            i.__init__(i.points)   # https://stackoverflow.com/questions/44178162/call-method-of-type-class
    
        for index, question in enumerate(q):
            empty_exam += question_separator.format(index+1)
            correct_exam += question_separator.format(index+1)
            empty_exam += question.empty_question
            correct_exam += question.correct_answer
            shelf[question.id] = question
            exam_included_files.extend(question.included_files)
    
        empty_exam   += endseparator
        correct_exam += endseparator
    
        empty_exam   = re.sub("\r?\n", "\r\n", empty_exam)
        correct_exam = re.sub("\r?\n", "\r\n", correct_exam)
    
        tempdir = pathlib.Path("/tmp/exam")
        
        if os.path.exists("/tmp/exam"):
            shutil.rmtree("/tmp/exam")
    
        tempdir.mkdir(exist_ok=True)
    
        for path in exam_included_files + [pathlib.Path (f) for f in additional_included_files]:
            newpath = pathlib.Path("/tmp/exam").joinpath(path.name)
            if path.suffix in [".gb", ".txt"]:
                text = re.sub("\r?\n", "\r\n", path.read_text())
                newpath.write_text(text)
            else:
                shutil.copy(path, newpath)
    
        with open("{exam_folder}/correct_{filename}.txt".format(exam_folder = correct_exam_folder, filename = filename), "w", encoding="latin-1") as f:
            f.write(correct_exam)
    
        with open("/tmp/exam/test_{filename}.txt".format(filename=filename), "w", encoding="latin-1") as f:
            f.write( empty_exam)
            
        #shutil.rmtree(os.path.join(exam_folder, filename), ignore_errors=True)
        #shutil.copytree("/tmp/exam/", os.path.join(exam_folder, filename))
        
        cmd = f'/home/bjorn/anaconda3/envs/EXAM/bin/7za a -tzip "/tmp/{filename}.zip" /tmp/exam/* -p{password} -scrcSHA256'
        
        slask=subprocess.call(cmd, shell=True)
        for n in range(10):
            try:
                shutil.move(f"/tmp/{filename}.zip", exam_folder)
            except FileNotFoundError:
                time.sleep(0.1)
            else:
                break
            
    shelf.close()
    input(f"password = {password}")

 


def rename_completed_tests():

    settings_path = pathlib.Path("settings.py")
    vardict= {}       
    with open(settings_path) as f:
        code = compile(f.read(), settings_path.name, 'exec')
    exec(code, vardict)               
    returned_exam_folder  =vardict["returned_exam_folder"]         

    cw = os.getcwd()

    os.chdir(returned_exam_folder)


    
    lst =[]
    
    for filename in sorted(os.listdir(".")):
    
        f, e = os.path.splitext(filename)
        if e.lower()!=".txt":
            continue
    
        handle = codecs.open(filename,"rb", "latin-1")
        exam = handle.read()
        handle.close()
    
        md5_ = md5(exam.encode("latin-1")).hexdigest()
    
        name      = (Literal("Nome") +
                     SkipTo(LineEnd()).setResultsName("name"))
    
        id        = (Literal("(mec)") +
                     SkipTo(LineEnd()).setResultsName("mec"))
    
        for data,dataStart,dataEnd in name.scanString(exam):
            parsed_student_name = data["name"].strip()
    
        for data,dataStart,dataEnd in id.scanString(exam):
            parsed_mec  = data["mec"].strip().lower()
    
        mec_in_filename = re.search("[\d|A|a|e|E]\d{4,5}",filename)
        if mec_in_filename:
            mec_in_filename = mec_in_filename.group()
            if parsed_mec.upper().startswith("NA"):
                parsed_mec=mec_in_filename.lower()
                
        new_name = parsed_student_name.replace(" ","_")+"_"+parsed_mec+"_"+md5_+".txt"
    
        #if unicode(filename,"utf-8") != new_name:
        if not re.search("_([a-fA-F\d]{32})\.(txt|TXT)", filename):
            print("rename",filename, end=' ')
            print("to",     new_name)
            lst.append((filename, new_name))
    

    for filename, newname in lst:
        os.rename(filename, newname)
        
    os.chdir(cw)

    
def correct_tests(question_numbers):
    settings_path = pathlib.Path("settings.py")
    vardict= {}       
    with open(settings_path) as f:
        code = compile(f.read(), settings_path.name, 'exec')
    exec(code, vardict)
    
    returned_exam_folder = vardict["returned_exam_folder"]
    shelf_folder         = vardict["shelf_folder"]        
    uuidpat              = vardict["uuidpat"]             
    endseparator         = vardict["endseparator"]        
    correction_folder    = vardict["correction_folder"]  
    
    now = time.strftime("%Y-%m-%dT%H:%M:%S", time.localtime())
    
    correction_folder = correction_folder + "_" + now
    
    # all files ending with md5.txt or .TXT
    files  = sorted([f for f in sorted(os.listdir(returned_exam_folder)) if re.search("_([a-fA-F\d]{32})\.(txt|TXT)$",f)])
    
    print("{} files out of {} in {} identified".format(len(files), len(os.listdir(returned_exam_folder)), returned_exam_folder))
    
    #import sys;sys.exit(42)
    
    shelf  = shelve.open(str(pathlib.Path(shelf_folder)/"shelf.shelf"))
    matrix = collections.defaultdict(list)
    point_matrix = collections.defaultdict(list)
    
    #files = [f for f in sorted(os.listdir(returned_exam_folder)) if f.endswith(("c00f675244144ebcc4fcaa28ca16fbeb.txt"))]
    
    names=[]
    
    for f in files:
        print(f)
        with open(os.path.join(returned_exam_folder,f), "rb") as f:
            test = f.read()
        encoding = chardet.detect(test)["encoding"]
        test = test.decode(encoding)

        #test = codecs.open(os.path.join(returned_exam_folder,f),"r","utf8").read()
        header, rest = re.split(uuidpat,test, maxsplit=1)
        rest = rest.split(endseparator)[0]
        name_from_header = re.search("(Name|Nome)(.*?)$",header,re.M).group(2).strip()
        mec_from_header  = re.search("^(Número mecanográfico \(mec\))(.*?)$",header,re.M).group(2).strip()
        exame = list((f.group(1),f.group(2)) for f in re.finditer("({uuidpat})(.*?)(?=({uuidpat}|$))".format(uuidpat=uuidpat),test,re.DOTALL))
        
        names.append((name_from_header, mec_from_header,))
    
        for question_no, (id, answer) in enumerate(exame):
    
            if question_numbers and not str(question_no+1) in question_numbers:
                print("\tquestion {} skipped".format(question_no+1))
                continue
    
            questionobj = shelf[str(id)]
            print("\t{} points {}".format(questionobj.__class__.__module__, questionobj.points))
            grade, comment = questionobj.correct(answer)
            point_matrix[question_no].append(questionobj.points)
            matrix[mec_from_header].append(textwrap.dedent('''
                    {sep1}
                    {correct_answer}
                    {sep2}
                    {students_answer}
                    {sep3}
    
                    automatic comments:
                    {comment}
                    manual comment:
    
                    question..........: {question_no:03d}
                    points............: {points}
                    name..............: {name}
                    mec...............: {mec}
                    automatic grade(%): {grade}
                    manual grade(%)...:
                    {sep4}
                    ''').format( question_no     = question_no+1,
                                 points          = questionobj.points,
                                 mec             = mec_from_header,
                                 name            = name_from_header,
                                 correct_answer  = questionobj.correct_answer,
                                 students_answer = answer,
                                 grade           = grade,
                                 comment         = comment,
                                 sep1            = "^"*(79-15)+" CORRECT ANSWER",
                                 sep2            = "="*(79-16)+" students answer",
                                 sep3            = "_"*(79-11)+" correction",
                                 sep4            = "~"*79,
                                 ))
    
    lengths=[]
    
    for key in sorted(matrix.keys()):
        lengths.append(len(matrix[key]))
    lengths = list(set(lengths))
    
    if len(lengths) != 1: # The same number of questions found in all exams!
        print(lengths)
        input()
    
    length = lengths.pop()
    
    points=[]
    for key in point_matrix:
        point = list(set(point_matrix[key]))
        assert len(point) == 1
    
    for q in range(length):
    
        text = "".join([matrix[key][q] for key in [m for n,m in sorted(names)]])
        text = text.replace( '\r\n', '\n'   )
        text = text.replace( '\n',   '\r\n' )
    
        os.makedirs(correction_folder, exist_ok=True)
        codecs.open(os.path.join(correction_folder, "question{0:03d}.txt".format(q+1)),"w","utf-8").write(text)
    
    shelf.close()
    input("press return")
    

def generate_spreadsheet(correction_folder):
   
    now = time.strftime("%Y-%m-%d %H_%M_%S", time.localtime())
    
    files = sorted(f for f in  os.listdir(correction_folder) if re.match("^question\d{3}\.txt$",f))
    
    rmat = collections.defaultdict(dict)
    
    grade =(Literal("question..........:").suppress() + Word(nums+"."+",").setResultsName("Q#") +
            Literal("points............:").suppress() + Word(nums+"."+",").setResultsName("points") +
            Literal("name..............:").suppress() + restOfLine.setResultsName("name") +
            Literal("mec...............:").suppress() + Word(alphanums).setResultsName("mec") +
            Literal("automatic grade(%):").suppress() + Word(nums+"."+",").setResultsName("autgrade") +
            Literal("manual grade(%)...:").suppress() + Optional(Word(nums+"."+",")).setResultsName("mangrade"))
    
    question_number_list = []
    name_list            = []
    points               = []
    
    
    names=[]
    
    for file_ in files:
        weight=[]
        print("processing: ", file_)
        content = open(os.path.join(correction_folder, file_),"r").read()
        for data, dataStart, dataEnd in grade.scanString(content):
            name = str(data["name"].strip())
            try:
                mec  = int(data["mec"])
            except ValueError:
                mec  = str(data["mec"])
            if not rmat[mec]:
                rmat[mec] = [name, mec]
                names.append((name, mec))
            question_number_list.append(data["Q#"])
            weight.append(data["points"])
            if "mangrade" in data:
                rmat[mec].append(float( data["mangrade"]))
            else:
                rmat[mec].append(float( data["autgrade"]))
        points.extend(list(set(weight)))
    
    

    doc = newdoc(doctype='ods', filename='grades_bioinformatics_{}.ods'.format(now))
    
    doc.sheets.append(Sheet(name="grades", size=(1, 20)))
    
    sheet = doc.sheets['grades']

    def write_row(sheet, row):
        for i,v in enumerate(row):
            sheet[(sheet.nrows()-1, i)].set_value(v)
        sheet.append_rows()

    headers = (['name','mec']+
               ["Q{}".format(no) for no in sorted(set(question_number_list))]+
               ['grade(0-20)'])
    
    write_row(sheet, headers)
    write_row(sheet, ["",""] + points)
    
    from string import ascii_uppercase as letters
    
    formula="=20*("
    #print(points)
    for c in range(len(points)):
        formula += "${letter}$2*{letter}3+".format(letter = letters[c+2])
    formula = formula.rstrip("+")
    formula +=")/{} \n".format(sum([100*int(x) for x in points]))
    
    write_row(sheet, ["Max Maximus", 99999] + [100]*len(points) + [formula]+['=IF({}3<9.5,"R","")'.format(letters[c+3])])
    
    for mec in [m for n, m in sorted(names)]:
        write_row(sheet, rmat[mec])
    
    doc.save()
    input("press return")
    
    
   
def main():
    try:
        arguments = docopt.docopt(__doc__, version=__version__)
    except docopt.DocoptExit as e:
        sys.exit(e)

    if arguments['create_settings']:
        directory = arguments["<test_folder>"] or pathlib.Path.cwd()
        create_settings(directory)      

    if arguments['create_folders']:
        directory = arguments["<test_folder>"] or pathlib.Path.cwd()
        create_folders(directory)
        
    elif arguments['parse_students']:
        parse_students(arguments["<path_student_list_file>"])
        
    elif arguments['generate_tests']:        
        generate_tests()
        
    elif arguments['rename_completed_tests']:
        rename_completed_tests()      
        
    elif arguments['correct_tests']:
        correct_tests(arguments["<question_numbers>"])
        
    elif arguments['generate_spreadsheet']:
        generate_spreadsheet(arguments["<correction_folder>"])


if __name__ == '__main__':
    main()