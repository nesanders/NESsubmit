mainfile='ps112sk.tex'
outdir='NESsubmit'

import os

##Clean directory
os.system('rm -rf '+outdir)
os.system('mkdir '+outdir)

#star figure numbering at 1
global fnum
fnum=0

##Function to open a tex file and strip it of comments
def ostrip(thefile):
    outlines=[]
    f=open(thefile,'r')
    for line in f:
        if line[0]!='%':
            if '%' in line: outlines.append(line.split(' %')[0]+'\n')
            else: outlines.append(line)
    return outlines

# function to take care of figures
def dofigure(line):
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
            if '.eps' in subline or '.pdf' in subline:
                outlines.append(dofigure(subline))
            else:
                outlines.append(subline)
    ##don't emulateapj
    elif '{emulateapj}' in line: outlines.append(r'\documentclass[manuscript]{aastex}'+'\n')
    elif r'\LongTables' in line: outlines.append('')
    ##input bibliography
    elif r'\bibliography{' in line:
        bibname=mainfile.replace('.tex','')+'.bbl'  #line.split('{')[1].split('}')[0]
        biblines=ostrip(bibname)
        for subline in biblines:
            outlines.append(subline)
    ##figures
    elif r'.eps' in line or '.ps' in line or '.pdf' in line:
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



##identify eps figures and bibliography
#f=open(outfile,'r')
#for line in f:
    #if '.eps' in line:
        #imname=line.split('{')[1].split('}')[0]
        #if 'onlineonlycolor' not in line: fnum+=1
        ##print name and number
        #print fnum,imname
        #outname=outdir+'/'+imname.split('/')[-1]
        ###copy over
        #os.system("cp "+imname+" "+outname)
    ##if r'\bibliography{' in line:
        ##bibname=line.split('{')[1].split('}')[0]+'.bib'
        ##outname=outdir+'/'+bibname.split('/')[-1]
        ##os.system("cp "+bibname+" "+outname)
#f.close()

##tar up
os.chdir(outdir)
os.system('tar -czf '+'ApJ.tar *.tex *.eps *.pdf --exclude "arxiv.tex"')
##readme
os.system('echo "For ApJ, simply upload the tarball.  For the arXiv, upload all the figures plus the arxiv.tex file, NOT the apj.tex" > README')
os.chdir('..')

