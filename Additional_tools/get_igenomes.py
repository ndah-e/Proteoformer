__author__ = 'SV'

###############################################################################################
## Construct custom igenomes information structure for PROTEOFORMER based on data of Ensembl ##
###############################################################################################

###########
## USAGE ##
###########

'''
    ARGUMENTS:
    
    -d | --dir                                  Directory wherein the igenomes tree structure will be installed
    -v | --version                              Ensembl annotation version to download
                                                (Ensembl plant (for arabidopsis) has seperate annotation versions!)
    -s | --species                              Specify the desired species for which gene annotation files should be downloaded
    -r | --remove                               If any, overwrite the existing igenomes structure for that species
    -c | --cores                                The amount of cores that will be used for downloading chromosomes files
                                                (Do not use more than 15 cores as the download server can only establish 15 connections at once)
    -h | --help                                 This useful help message
    
    currently supported species:
    
    human                       |   Homo_sapiens
    mouse                       |   Mus_musculus
    rat                         |   Rattus norvegicus
    fruitfly                    |   Drosophila_melanogaster
    yeast                       |   Saccharomyces_cerevisiae
    zebrafish                   |   Danio_rerio
    arabidopsis                 |   Arabidopsis_thaliana
    c.elegans                   |   Caenorhabditis_elegans
    SL1344                      |   Salmonella enterica subsp. enterica serovar Typhimurium str. SL1344
    MYC_ABS_ATCC_19977          |   Mycobacterium abscessus atcc 19977
    
    EXAMPLE:
    
    python get_igenomes.py -v 82 -s human -d /path/to/dir -r -c 15
    
    python get_igenomes.py -v 31 -s arabidopsis -d /path/to/dir -r -c 15
    
    DEPENDENCIES:
    
    This program depends upon wget, rsync and gzip, which are normally pre-installed on any unix system
    
    '''

import os
import shutil
import getopt
import sys
import re
from multiprocessing import Pool
import datetime
import traceback

def main():

    try:
        myopts, args = getopt.getopt(sys.argv[1:],"d:s:v:rc:h",["dir=","version=","species=","remove","cores=","help"])
    except getopt.GetoptError as err:
        print(err)
        sys.exit()

    #################################
    # o == option                   #
    # a == argument passed to the o #
    #################################

    #
    # Catch arguments
    #

    removeExisting=False
    for o, a in myopts:
        if o in ('-h', '--help'):
            print_help()
            sys.exit()
        if o in ('-d','--dir'):
            instalDir=os.path.abspath(a);
        if o in ('-s','--species'):
            species=a
        if o in ('-v','--version'):
            stringEns_v=a
            try:
                ens_v=int(stringEns_v)
            except:
                print "Error: could not parse the Ensembl version argument into an int"
                sys.exit()
        if o in ('-r','--remove'):
            removeExisting=True
        if o in ('-c', '--cores'):
            stringCores=a
            try:
                 cores=int(stringCores)
            except:
                print "Error: could not parse the cores argument into an int"
                sys.exit()

    #
    # Check for correct arguments
    #

    if(instalDir == ''):
        print("Error: do not forget to pass the directory where the igenomes structure should be installed!")
        sys.exit()
    if(species == ''):
        print("Error: do not forget to pass the species argument!")
        sys.exit()
    if(stringEns_v == ''):
        print("Error: do not forget to pass the ensembl version argument!")
        sys.exit()
    if(cores == ''):
        print("Error: do no forget to pass the amount of cores!")
        sys.exit()
    elif(int(cores)>15):
        print("Error: the amount of cores cannot be larger than 15!")
        sys.exit()
    if(species == 'arabidopsis'):
        if(ens_v>31):
            print("Error: latest Ensembl Plants version is 29!")
            sys.exit()
    elif(species =='SL1344' or species =='MYC_ABS_ATCC_19977'):
        if(ens_v>40):
            print("Error: latest Ensembl Bacteria version is 40!")
            sys.exit()
    else:
        if(ens_v>89):
            print("Error: latest Ensembl version is 84!")
            sys.exit()
    #Remove last "/" from instal dir path
    pattern=re.compile('^(\S+)/$')
    m = pattern.match(instalDir)
    if(m):
        instalDir=m.group(1)
    #Report on input
    print("The igenomes structure will be installed in : " + instalDir)
    print("Ensembl version used                        : " + stringEns_v)
    print("Selected species                            : " + species)
    print("Amount of cores                             : " + stringCores)

    #Convert species and construct additional info. New assemblies can be modified here.
    if(species=='human'):
        speciesLong='Homo_sapiens'
        if(ens_v>75):
            assembly='GRCh38'
            ucscCode='hg38'
        else:
            assembly='GRCh37'
            ucscCode='hg19'
    elif(species=='mouse'):
        speciesLong='Mus_musculus'
        if(ens_v>67):
            assembly='GRCm38'
            ucscCode='mm10'
        else:
            assembly='NCBIM37'
            ucscCode='mm9'
    elif(species=='rat'):
        speciesLong='Rattus_norvegicus'
        if(ens_v>79):
            assembly='Rnor_6.0'
            ucscCode='rn6'
        else:
            assembly='Rnor_5.0'
            ucscCode='rn5'
    elif(species=='fruitfly'):
        speciesLong='Drosophila_melanogaster'
        if(ens_v>78):
            assembly='BDGP6'
            ucscCode='dm6'
        else:
            assembly='BDGP5'
            ucscCode='dm3'
    elif(species=='yeast'):
        speciesLong='Saccharomyces_cerevisiae'
        if(ens_v>74):
            assembly='R64-1-1'
            ucscCode='sacCer3'
        else:
            assembly='EF2'
            ucscCode='sacCer2'
    elif(species=='zebrafish'):
        speciesLong='Danio_rerio'
        if(ens_v>79):
            assembly='GRCz10'
            ucscCode='danRer10'
        else:
            assembly='Zv9'
            ucscCode='danRer7'
    elif(species=='arabidopsis'):
        speciesLong='Arabidopsis_thaliana'
        assembly='TAIR10'
    elif(species=='c.elegans'):
        speciesLong='Caenorhabditis_elegans'
        assembly='WBcel235'
        ucscCode='ce10'
    elif(species=='SL1344'):
        speciesLong='SL1344'
        assembly='ASM21085v2'
    elif(species=='MYC_ABS_ATCC_19977'):
        speciesLong='mycobacterium_abscessus_atcc_19977'
        assembly='ASM6918v1'
    else:
        print("Species has to be one of the following list: human, mouse, fruitfly, yeast, zebrafish, arabidopsis, c.elegans, mycobacterium_abscessus_atcc_19977, SL1344")
        sys.exit()

    print("Assembly                                    : " + assembly)
    if(species!='arabidopsis' and species!='SL1344' and species!='MYC_ABS_ATCC_19977'):
        print("UCSC code                                   : " + ucscCode)
    print("")

    os.chdir(instalDir)

    #Check if the igenomes folder already exists
    if os.path.isdir("igenomes"):
        if os.path.isdir("igenomes/"+speciesLong+"/Ensembl/"+assembly):
            if(removeExisting==False):
                print("There is already a folder called igenomes/"+speciesLong+"/Ensembl/"+assembly+" for "+species+" in "+instalDir)
                print("If you want to overwrite the existing structure for that species in "+instalDir+", please use the -r or --remove option.")
                sys.exit()
            else:
                print("Overwriting existing igenomes folder for "+species)
                shutil.rmtree("igenomes/"+speciesLong+"/Ensembl/"+assembly)
    else:
        os.system("mkdir igenomes")



    #construct the basic folder structure
    if(not os.path.isdir("igenomes/"+speciesLong)):
        os.system("mkdir igenomes/"+speciesLong)
    if(not os.path.isdir("igenomes/"+speciesLong+"/Ensembl")):
        os.system("mkdir igenomes/"+speciesLong+"/Ensembl")
    if(not os.path.isdir("igenomes/"+speciesLong+"/Ensembl/"+assembly)):
        os.system("mkdir igenomes/"+speciesLong+"/Ensembl/"+assembly)
    os.system("mkdir igenomes/"+speciesLong+"/Ensembl/"+assembly+"/Annotation")
    os.system("mkdir igenomes/"+speciesLong+"/Ensembl/"+assembly+"/Sequence")

    os.chdir(instalDir+"/igenomes/"+speciesLong+"/Ensembl/"+assembly+"/Annotation")



    ## Chr sizes files
    print("")
    print("Get Chromosome lengths from UCSC")
    chromList = {}
    os.system("mkdir Genes")
    os.chdir(instalDir+"/igenomes/"+speciesLong+"/Ensembl/"+assembly+"/Annotation/Genes")

    #Fetch data from UCSC except for arabidopsis (not included in UCSC)
    if(species=='arabidopsis'):
        #For arabidopsis, chromosome sizes can be fetched out of the files where the Ensembl DB is build from
        canEns_v=str(ens_v+53) #Arabidopsis Ensembl releases are 53 less than the other species.
        os.system("wget -q ftp://ftp.ensemblgenomes.org/pub/release-"+stringEns_v+"/plants/mysql/"+speciesLong.lower()+"_core_"+stringEns_v+"_"+canEns_v+"_10/seq_region.txt.gz")
        os.system("gzip -d seq_region.txt.gz")
        input = open('seq_region.txt', 'r')
        for line in input:
            pattern = re.compile('^\d+\t(\w+)\t4\t(\d+)')
            m = pattern.search(line)
            if m:
                if(m.group(1)=='Mt'):
                    chromList['MT']=m.group(2)
                else:
                    chromList[m.group(1)]=m.group(2)
    elif(species=='SL1344' or species=='MYC_ABS_ATCC_19977'):
        #For bacteria, chromosome sizes can be fetched out of the files where the Ensembl DB is build from
        if (species=='SL1344'):
            collection = '23'
        elif (species=='MYC_ABS_ATCC_19977'):
            collection = '16'
        canEns_v=str(ens_v+53) #Bacteria Ensembl releases are 53 less than the other species.
        #first, search coord system id
        os.system("wget -q ftp://ftp.ensemblgenomes.org/pub/release-"+stringEns_v+"/bacteria/mysql/bacteria_"+collection+"_collection_core_"+stringEns_v+"_"+canEns_v+"_1/coord_system.txt.gz")
        os.system("gzip -d coord_system.txt.gz")
        coord_system_id=0
        input = open('coord_system.txt', 'r')
        if (species=='SL1344'):
            for line in input: #For SL1344 we take the chromosome as coord_system (corresponds to "1" as last field)
                pattern = re.compile('^(\d+)\t\d+\t\w+\t(\w+)\t1')
                m = pattern.search(line)
                if m:
                    if(m.group(2)==assembly):
                        coord_system_id=m.group(1)
        elif (species=='MYC_ABS_ATCC_19977'):
            for line in input: #For MYC_ABS_ATCC_19977 we take the supercontig as coord_system (corresponds to "3" as last field)
                pattern = re.compile('^(\d+)\t\d+\t\w+\t(\w+)\t3')
                m = pattern.search(line)
                if m:
                    if(m.group(2)==assembly):
                        coord_system_id=m.group(1)
        #Then search for the chromosome in seq_region.txt
        os.system("wget -q ftp://ftp.ensemblgenomes.org/pub/release-"+stringEns_v+"/bacteria/mysql/bacteria_"+collection+"_collection_core_"+stringEns_v+"_"+canEns_v+"_1/seq_region.txt.gz")
        os.system("gzip -d seq_region.txt.gz")
        input = open('seq_region.txt', 'r')
        regex = r"\b(?=\w)^\d+\t(\w+)\t"+re.escape(coord_system_id)+r"\t(\d+)\b(?!\w)"
        for line in input:
            pattern = re.compile(regex)
            m = pattern.search(line)
            if m:
                chromList[m.group(1)]=m.group(2)
    else:
        #Other species: download from UCSC
        os.system("wget -q ftp://hgdownload.cse.ucsc.edu/goldenPath/"+ucscCode+"/database/chromInfo.txt.gz")
        os.system("gzip -d chromInfo.txt.gz")
        os.system("mv chromInfo.txt tmpChromInfo.txt")
        #Retain only the standard chromosomes
        with open('tmpChromInfo.txt') as inFile:
            for line in inFile:
                pattern = re.compile('^chr(\w{1,4})\t(\d+)\t\S+\n$') #chrVIII (yeast) is the longest one to capture
                m = pattern.match(line)
                if m:
                    if(species=='fruitfly'):
                        chromList[m.group(1)]=m.group(2) #For fruitfly we want to use 'M' as mitochondrial symbol
                    else:
                        if(m.group(1)=='M'):#Ensembl uses MT instead of M for mitochondrial genome in UCSC, except for fruitfly
                            chromList['MT']=m.group(2)
                        else:
                            chromList[m.group(1)]=m.group(2)
    #Write standard chromosomes to chromosome sizes file
    outFile = open('ChromInfo.txt','w')
    for key in chromList:
        outFile.write(key+"\t"+chromList[key]+"\n")
    outFile.close()
    if(species=='arabidopsis'):
        os.system("rm -rf seq_region.txt")
    elif(species=='SL1344' or species=='MYC_ABS_ATCC_19977'):
        os.system("rm -rf coord_system.txt")
        os.system("rm -rf seq_region.txt")
    else:
        os.system("rm -rf tmpChromInfo.txt")



    ## Download chromosome files
    print("\n")
    print("Get chromosome fasta files")
    os.chdir(instalDir+"/igenomes/"+speciesLong+"/Ensembl/"+assembly+"/Sequence")
    os.system("mkdir Chromosomes")
    os.chdir(instalDir+"/igenomes/"+speciesLong+"/Ensembl/"+assembly+"/Sequence/Chromosomes")

    #Multithreading chromosome downloads
    pool = Pool(processes=cores)
    [pool.apply_async(downloadChromosomeFasta, args=(key,species,speciesLong,ens_v,stringEns_v,assembly,instalDir)) for key in chromList]
    pool.close()
    pool.join()



    ## Make whole genome fasta
    print("\n")
    print("Make whole genome fasta file as a concatenation of the seperate chromosome files")
    os.chdir(instalDir+"/igenomes/"+speciesLong+"/Ensembl/"+assembly+"/Sequence")
    os.system("mkdir WholeGenomeFasta")
    os.chdir(instalDir+"/igenomes/"+speciesLong+"/Ensembl/"+assembly+"/Sequence/WholeGenomeFasta")

    #Whole genome fasta file is a concatenation of all chromosome fasta files: first, construct command
    command = ""
    for chr in chromList:
        command=command+" "+instalDir+"/igenomes/"+speciesLong+"/Ensembl/"+assembly+"/Sequence/Chromosomes/"+chr+".fa"
    #Do concatenation
    os.system("cat"+command+"> genome.fa")





    ## Download genes.gtf file
    print("\n")
    print("Download genes.gtf file")
    os.chdir(instalDir+"/igenomes/"+speciesLong+"/Ensembl/"+assembly+"/Annotation/Genes")
    if(species=='arabidopsis'):#Arabidopsis from Ensembl Plants
        os.system("wget -q ftp://ftp.ensemblgenomes.org/pub/release-"+stringEns_v+"/plants/gtf/"+speciesLong.lower()+"//"+speciesLong+"."+assembly+"."+stringEns_v+".gtf.gz")
        os.system("mv "+speciesLong+"."+assembly+"."+stringEns_v+".gtf.gz genesTmp.gtf.gz")
    elif(species=='SL1344'):
        os.system("wget -q ftp://ftp.ensemblgenomes.org:21//pub/release-"+stringEns_v+"/bacteria/gtf/bacteria_23_collection/salmonella_enterica_subsp_enterica_serovar_typhimurium_str_sl1344/Salmonella_enterica_subsp_enterica_serovar_typhimurium_str_sl1344."+assembly+"."+stringEns_v+".gtf.gz")
        os.system("mv Salmonella_enterica_subsp_enterica_serovar_typhimurium_str_sl1344."+assembly+"."+stringEns_v+".gtf.gz genesTmp.gtf.gz")
    elif(species=='MYC_ABS_ATCC_19977'):
        os.system("wget -q ftp://ftp.ensemblgenomes.org:21//pub/release-"+stringEns_v+"/bacteria/gtf/bacteria_16_collection/mycobacterium_abscessus_atcc_19977/Mycobacterium_abscessus_atcc_19977."+assembly+"."+stringEns_v+".gtf.gz")
        os.system("mv Mycobacterium_abscessus_atcc_19977."+assembly+"."+stringEns_v+".gtf.gz genesTmp.gtf.gz")
    else:
        os.system("rsync -avq rsync://ftp.ensembl.org/ensembl/pub/release-"+stringEns_v+"/gtf/"+speciesLong.lower()+"//"+speciesLong+"."+assembly+"."+stringEns_v+".gtf.gz genesTmp.gtf.gz")
    os.system("gunzip genesTmp.gtf.gz")

    #The first lines are comments and are unwanted: delete them
    genesFile = open('genes.gtf','w')
    with open('genesTmp.gtf') as genesTmp:
        for line in genesTmp:
            pattern = re.compile('^#!')
            m = pattern.match(line)
            if(m==None):
                genesFile.write(line)
    genesFile.close()
    os.system("mv genes.gtf genes_"+stringEns_v+".gtf")
    os.system("rm -rf genesTmp.gtf")



    ##Download supplemental abundant sequences
    print("\n")
    print("PhiX fasta file downloading in "+instalDir+"/igenomes/"+speciesLong+"/Ensembl/"+assembly+"/Sequence/AbundantSequences. Other abundant sequences (e.g. rRNA) can be added in this folder too.")
    os.chdir(instalDir+"/igenomes/"+speciesLong+"/Ensembl/"+assembly+"/Sequence")
    os.system("mkdir AbundantSequences")
    os.chdir(instalDir+"/igenomes/"+speciesLong+"/Ensembl/"+assembly+"/Sequence/AbundantSequences")
    os.system("wget -q ftp://ftp.ncbi.nih.gov//genomes/Viruses/enterobacteria_phage_phix174_sensu_lato_uid14015/NC_001422.fna")
    os.system("mv NC_001422.fna phix.fa")





    ## Make README.txt file
    os.chdir(instalDir+"/igenomes/"+speciesLong+"/Ensembl/"+assembly+"/Annotation")
    readmeFile = open('README.txt','w')
    #Get date
    downloadDate = datetime.date.today()
    year=downloadDate.year
    monthinteger=downloadDate.month
    month=datetime.date(1900, monthinteger, 1).strftime('%B')
    day=downloadDate.day
    readmeFile.write("The contents of the annotation directories were downloaded from Ensembl on: "+month+" "+str(day)+", "+str(year)+".\n")
    if(species=='arabidopsis'):
        readmeFile.write("Gene annotation files were downloaded from Ensembl Plants release "+stringEns_v+".")
    elif(species=='SL1344' or species=='MYC_ABS_ATCC_19977'):
        readmeFile.write("Gene annotation files were downloaded from Ensembl Bacteria release "+stringEns_v+".")
    else:
        readmeFile.write("Gene annotation files were downloaded from Ensembl release "+stringEns_v+".")
    readmeFile.close()






    ##Change permissions for free consultation
    os.chdir(instalDir)
    os.system("chmod 777 igenomes")
    os.system("chgrp biobix igenomes")
    os.chdir(instalDir+"/igenomes")
    os.system("chmod -R 777 "+speciesLong)
    os.system("chgrp -R biobix "+speciesLong)

    print("\n")
    print("   (***) igenomes folder download complete (***)")
    print("\n")

    return

########
# SUBS #
########

#Defenition of one download process
def downloadChromosomeFasta(chr, species, speciesLong, ens_v, stringEns_v, assembly, instalDir):
    if(species=='arabidopsis'):#Arabidopsis is on the site of ensembl Plants instead of normal Ensembl. This site cannot use rsync yet.
        if(chr=='MT'):#Ensembl uses 'Mt' for Arabidopsis mitochondrial genome
            os.system("wget -q ftp://ftp.ensemblgenomes.org/pub/plants/release-"+stringEns_v+"/fasta/"+speciesLong.lower()+"/dna//"+speciesLong+"."+assembly+"."+stringEns_v+".dna.chromosome.Mt.fa.gz")
            os.system("gunzip "+speciesLong+"."+assembly+"."+stringEns_v+".dna.chromosome.Mt.fa.gz")
            os.system("mv "+speciesLong+"."+assembly+"."+stringEns_v+".dna.chromosome.Mt.fa MT.fa")
        else:
            os.system("wget -q ftp://ftp.ensemblgenomes.org/pub/plants/release-"+stringEns_v+"/fasta/"+speciesLong.lower()+"/dna//"+speciesLong+"."+assembly+"."+stringEns_v+".dna.chromosome."+chr+".fa.gz")
            os.system("gunzip "+speciesLong+"."+assembly+"."+stringEns_v+".dna.chromosome."+chr+".fa.gz")
            os.system("mv "+speciesLong+"."+assembly+"."+stringEns_v+".dna.chromosome."+chr+".fa "+chr+".fa")
        print("\t\t*) Chromosome "+chr+" finished")
    elif(species=='SL1344'):
        os.system("wget -q ftp://ftp.ensemblgenomes.org/pub/release-"+stringEns_v+"/bacteria/fasta/bacteria_23_collection/salmonella_enterica_subsp_enterica_serovar_typhimurium_str_sl1344/dna/Salmonella_enterica_subsp_enterica_serovar_typhimurium_str_sl1344."+assembly+".dna.chromosome."+chr+".fa.gz")
        os.system("gunzip Salmonella_enterica_subsp_enterica_serovar_typhimurium_str_sl1344."+assembly+".dna.chromosome."+chr+".fa.gz")
        os.system("mv Salmonella_enterica_subsp_enterica_serovar_typhimurium_str_sl1344."+assembly+".dna.chromosome."+chr+".fa "+chr+".fa")
    elif(species=='MYC_ABS_ATCC_19977'):
            # For Mycobacterium ABS ATCC 19977 no chromosome is assembled, so we go for the toplevel assembly (noticeable at the end of the name of the downloaded file)
            os.system("wget -q ftp://ftp.ensemblgenomes.org/pub/release-"+stringEns_v+"/bacteria/fasta/bacteria_16_collection/mycobacterium_abscessus_atcc_19977/dna/Mycobacterium_abscessus_atcc_19977."+assembly+".dna.toplevel.fa.gz")
            print("test\n")
            os.system("gunzip Mycobacterium_abscessus_atcc_19977."+assembly+".dna.toplevel.fa.gz")
            print(chr+"\n")
            os.system("mv Mycobacterium_abscessus_atcc_19977."+assembly+".dna.toplevel.fa "+chr+".fa")
    else:#use rsync for other species
        if(chr=='MT' or chr=='M'):
            if(species=='fruitfly'):#Other name 'dmel_mitochondrion_genome' for fruitfly
                if(ens_v>75):
                    os.system("rsync -avq rsync://ftp.ensembl.org/ensembl/pub/release-"+stringEns_v+"/fasta/"+speciesLong.lower()+"/dna//"+speciesLong+"."+assembly+".dna.chromosome.dmel_mitochondrion_genome.fa.gz "+instalDir+"/igenomes/"+speciesLong+"/Ensembl/"+assembly+"/Sequence/Chromosomes/M.fa.gz")
                else:
                    os.system("rsync -avq rsync://ftp.ensembl.org/ensembl/pub/release-"+stringEns_v+"/fasta/"+speciesLong.lower()+"/dna//"+speciesLong+"."+assembly+"."+stringEns_v+".dna.chromosome.dmel_mitochondrion_genome.fa.gz "+instalDir+"/igenomes/"+speciesLong+"/Ensembl/"+assembly+"/Sequence/Chromosomes/M.fa.gz")
                os.system("gunzip M.fa.gz")
            elif(species=='yeast'):#Other name 'Mito' for yeast
                if(ens_v>75):
                    os.system("rsync -avq rsync://ftp.ensembl.org/ensembl/pub/release-"+stringEns_v+"/fasta/"+speciesLong.lower()+"/dna//"+speciesLong+"."+assembly+".dna.chromosome.Mito.fa.gz "+instalDir+"/igenomes/"+speciesLong+"/Ensembl/"+assembly+"/Sequence/Chromosomes/MT.fa.gz")
                else:
                    os.system("rsync -avq rsync://ftp.ensembl.org/ensembl/pub/release-"+stringEns_v+"/fasta/"+speciesLong.lower()+"/dna//"+speciesLong+"."+assembly+"."+stringEns_v+".dna.chromosome.Mito.fa.gz "+instalDir+"/igenomes/"+speciesLong+"/Ensembl/"+assembly+"/Sequence/Chromosomes/MT.fa.gz")
                os.system("gunzip MT.fa.gz")
            elif(species=='c.elegans'):#Other name 'MtDNA' for c elegans
                if(ens_v>75):
                    os.system("rsync -avq rsync://ftp.ensembl.org/ensembl/pub/release-"+stringEns_v+"/fasta/"+speciesLong.lower()+"/dna//"+speciesLong+"."+assembly+".dna.chromosome.MtDNA.fa.gz "+instalDir+"/igenomes/"+speciesLong+"/Ensembl/"+assembly+"/Sequence/Chromosomes/MT.fa.gz")
                else:
                    os.system("rsync -avq rsync://ftp.ensembl.org/ensembl/pub/release-"+stringEns_v+"/fasta/"+speciesLong.lower()+"/dna//"+speciesLong+"."+assembly+"."+stringEns_v+".dna.chromosome.MtDNA.fa.gz "+instalDir+"/igenomes/"+speciesLong+"/Ensembl/"+assembly+"/Sequence/Chromosomes/MT.fa.gz")
                os.system("gunzip MT.fa.gz")
            else:#MT for other species
                if(ens_v>75):
                    os.system("rsync -avq rsync://ftp.ensembl.org/ensembl/pub/release-"+stringEns_v+"/fasta/"+speciesLong.lower()+"/dna//"+speciesLong+"."+assembly+".dna.chromosome.MT.fa.gz "+instalDir+"/igenomes/"+speciesLong+"/Ensembl/"+assembly+"/Sequence/Chromosomes/MT.fa.gz")
                else:
                    os.system("rsync -avq rsync://ftp.ensembl.org/ensembl/pub/release-"+stringEns_v+"/fasta/"+speciesLong.lower()+"/dna//"+speciesLong+"."+assembly+"."+stringEns_v+".dna.chromosome.MT.fa.gz "+instalDir+"/igenomes/"+speciesLong+"/Ensembl/"+assembly+"/Sequence/Chromosomes/MT.fa.gz")
                os.system("gunzip MT.fa.gz")
        else:
            if(ens_v>75):
                os.system("rsync -avq rsync://ftp.ensembl.org/ensembl/pub/release-"+stringEns_v+"/fasta/"+speciesLong.lower()+"/dna//"+speciesLong+"."+assembly+".dna.chromosome."+chr+".fa.gz "+instalDir+"/igenomes/"+speciesLong+"/Ensembl/"+assembly+"/Sequence/Chromosomes/"+chr+".fa.gz")
            else:
                os.system("rsync -avq rsync://ftp.ensembl.org/ensembl/pub/release-"+stringEns_v+"/fasta/"+speciesLong.lower()+"/dna//"+speciesLong+"."+assembly+"."+stringEns_v+".dna.chromosome."+chr+".fa.gz "+instalDir+"/igenomes/"+speciesLong+"/Ensembl/"+assembly+"/Sequence/Chromosomes/"+chr+".fa.gz")
            os.system("gunzip "+chr+".fa.gz")
        print("\t\t*) Chromosome "+chr+" finished")
    return

def print_help():

    help = """
    ARGUMENTS:

    -d | --dir                                  Directory wherein the igenomes tree structure will be installed
    -v | --version                              Ensembl annotation version to download
                                                (Ensembl plant (for arabidopsis) and bacteria have seperate annotation versions!)
    -s | --species                              Specify the desired species for which gene annotation files should be downloaded
    -r | --remove                               If any, overwrite the existing igenomes structure for that species
    -c | --cores                                The amount of cores that will be used for downloading chromosomes files
                                                (Do not use more than 15 cores as the download server can only establish 15 connections at once)
    -h | --help                                 This useful help message

    currently supported species:

    human                       |   Homo_sapiens
    mouse                       |   Mus_musculus
    rat                         |   Rattus norvegicus
    fruitfly                    |   Drosophila_melanogaster
    yeast                       |   Saccharomyces_cerevisiae
    zebrafish                   |   Danio_rerio
    arabidopsis                 |   Arabidopsis_thaliana
    c.elegans                   |   Caenorhabditis_elegans
    SL1344                      |   Salmonella enterica subsp. enterica serovar Typhimurium str. SL1344
    MYC_ABS_ATCC_19977          |   Mycobacterium abscessus atcc 19977

    EXAMPLE:

    python get_igenomes.py -v 82 -s human -d /path/to/dir -r -c 15

    python get_igenomes.py -v 31 -s arabidopsis -d /path/to/dir -r -c 15

    DEPENDENCIES:

    This program depends upon wget, rsync and gzip, which are normally pre-installed on any unix system

    """

    print help
    print

    return


###### DIRECT TO MAIN ############
if __name__ == "__main__":
    try:
        main()
    except Exception, e:
        traceback.print_exc()
##################################
