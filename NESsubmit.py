"""
This is a script to format and package a scientific paper written in latex for
upload to the journal (using aastex) and the arXiv (assuming emulateapj).

It will make numbered copies of all the figures, strip out latex comments, 
copy in the compiled BibTex biliography, and combine any \input latex sources 
into a single tex file.

Run this script from inside a directory with a compiled paper with the syntax: 
python NESsubmit.py myfile.tex outputdir

The outputdir is the directory where the program output will be written. 
If the directory already exists, it will be overwritten.

----

Written by Nathan Sanders, 2012
https://www.cfa.harvard.edu/~nsanders/index.htm

If you have comments or questions about this script, please leave comments at:

http://astrobites.com/2012/08/05/how-to-submit-a-paper/

or submit bug reports at:

https://github.com/nesanders/NESsubmit/issues

"""

import os,sys

print sys.argv
if len(sys.argv)>1: mainfile=sys.argv[1]
else: 
  print "You must specify a main tex file"
if len(sys.argv)>2: mainfile=sys.argv[2]
else: outdir='submit'

##Clean directory
os.system('rm -rf '+outdir)
os.system('mkdir '+outdir)

#start figure numbering at 1
global fnum
fnum=0

def ostrip(thefile):
    """
    Function to open a tex file and strip it of comments
    """
    outlines=[]
    f=open(thefile,'r')
    for line in f:
        if line[0]!='%':
            if '%' in line: outlines.append(line.split(' %')[0]+'\n')
            else: outlines.append(line)
    return outlines

def dofigure(line):
    """
    Function to take care of figures
    """
    global fnum
    imname=line.split('{')[1].split('}')[0]
    if 'onlineonlycolor' not in line: fnum+=1
    #print name and number
    print fnum,imname
    subname=imname.split('/')[-1]
    ftype=subname.split('.')[-1]
    ##rename with number if desired
    subname='f'+str(fnum)+'.'+ftype
    outname=outdir+'/'+subname
    ##copy over
    os.system("cp "+imname+" "+outname)            
    ##write out plot string
    return line.replace(imname,subname)


##do includes - only goes one level in
mainlines=ostrip(mainfile)
outlines=[]
for line in mainlines:
    if '\input' in line:
        incfile=line.split('{')[1].split('}')[0]
        ##if there is no extension, assume it is a .tex
        if len(incfile.split('.'))==1: incfile=incfile+'.tex'
        for subline in ostrip(incfile):
            ##rotate long tables
            #if 'scriptsize' in subline: outlines.append(r'\rotate'+'\n')
            if '.eps' in subline:
                outlines.append(dofigure(subline))
            else:
                outlines.append(subline)
    ##don't emulateapj
    elif '{emulateapj}' in line: outlines.append(r'\documentclass[manuscript]{aastex}'+'\n')
    elif r'\LongTables' in line: outlines.append('')
    ##input bibliography
    elif r'\bibliography{' in line:
        bibname=line.split('{')[1].split('}')[0].replace('.bib','')+'.bbl'
        biblines=ostrip(bibname)
        for subline in biblines:
            outlines.append(subline)
    ##figures
    elif r'.eps' in line or '.ps' in line:
        outlines.append(dofigure(line))
    else:
        outlines.append(line)


###Write out ApJ version
outfile=outdir+'/apj.tex'
f=open(outfile,'w')
for line in outlines:
    ##don't need two-column deluxetables for apJ
    line=line.replace('deluxetable*','deluxetable')
    if 'aas_macros' not in line: f.write(line)

f.close()

###Write out arXiv version
outfile=outdir+'/arxiv.tex'
f=open(outfile,'w')
for line in outlines:
    if '{aastex}' in line: newline=r'\documentclass{emulateapj}'+'\n'
    else: newline=line
    f.write(newline)

f.close()


##tar up
os.chdir(outdir)
os.system('tar -czf '+'ApJ.tar *.tex *.eps --exclude "arxiv.tex"')
##readme
os.system('echo "For ApJ, simply upload the tarball.  For the arXiv, upload all the figures plus the arxiv.tex file, NOT the apj.tex" > README')
os.chdir('..')

