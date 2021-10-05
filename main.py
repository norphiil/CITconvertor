import sys
import os
from pathlib import Path
from datetime import datetime

from jproperties import Properties
import shutil

import json

verbose = False

def get_usage():
    return 'Usage ->{0}\t{1} [<options>] <xlsx_file>{0}{0}Options:{0}\t-o <output_file> \t--output <output_file>\tWrite the output to the specified file (if not specified, output to the console){0}\t-v \t\t\t--verbose\t\tWite all log output to console'.format(os.linesep, sys.argv[0])

def main(input: str, output: str):
    configs = Properties()

    ## create texture pack directory
    if(os.path.exists('./minecraft') and os.path.isdir('./minecraft')):
        shutil.rmtree('./minecraft')
    
    os.mkdir('./minecraft')
    os.mkdir('./minecraft/models')
    os.mkdir('./minecraft/models/item')
    os.mkdir('./minecraft/textures')
    os.mkdir('./minecraft/textures/items')

    dir = input+'/assets/minecraft/optifine/cit/'
    counter = 0
    label = "Loading"
    Progress = ProgressBar(counter, len(os.listdir(dir)), label = label, usePercentage = True)
    for filename in os.listdir(dir):
        counter += 1
        label = ""
        Progress.updateProgress(counter, label)


        debug(filename)
        if((dir+filename).split(".")[-1] == 'properties'):
            ## read item properties
            f = open(dir+filename, 'rb')
            configs.load(f)
            f.close()

            items = configs.get("matchItems").data.split(" ")
            model = configs.get("model").data
            for item in items:
                
                if('/' in model):
                    model = model.split("/")[-1]
                if('.' not in model):
                    model = model+'.json'
                if(':' in item):
                    splitItems = (item.split(":")[-1])
                else:
                    splitItems = (item)

                if(len(splitItems.split("_")) > 1):
                    folder = splitItems.split("_")[-2]+"_"+splitItems.split("_")[-1]
                else:
                    folder = splitItems.split("_")[-1]

                itemPath = './minecraft/models/item/'+folder

                ## copy item json to owns texture pack directory
                if(not os.path.exists(itemPath) or not os.path.isdir(itemPath)):
                    os.mkdir(itemPath)
                tmpMax = 0
                for itemfilename in os.listdir(itemPath):
                    if (int(tmpMax) < int(itemfilename.split(".")[0])):
                        tmpMax = int(itemfilename.split(".")[0])
                    continue
                tmpMax += 1
                if(os.path.exists(dir+model) and os.path.isfile(dir+model)):
                    shutil.copyfile(dir+model, itemPath+'/'+str(tmpMax)+'.json')

                ## read item json
                try:
                    f = open(itemPath+'/'+str(tmpMax)+'.json', 'r')
                    data = json.load(f)
                    f.close()

                    ## Copy and link item

                    if(os.path.exists('./template/assets/minecraft/models/item/'+splitItems+'.json') and os.path.isfile('./template/assets/minecraft/models/item/'+splitItems+'.json')):
                        if(not os.path.exists('./minecraft/models/item/'+splitItems+'.json') or not os.path.isfile('./minecraft/models/item/'+splitItems+'.json')):
                            shutil.copyfile('./template/assets/minecraft/models/item/'+splitItems+'.json', './minecraft/models/item/'+splitItems+'.json')
                            # read item json
                            f = open('./minecraft/models/item/'+splitItems+'.json', 'r')
                            itemData = json.load(f)
                            f.close()
                            
                            itemData['overrides'] = []
                            itemData['overrides'].append({ "predicate": { "custom_model_data": tmpMax }, "model": "item/"+folder+"/"+str(tmpMax)+""})

                            # write item json
                            f = open('./minecraft/models/item/'+splitItems+'.json', "w")
                            json.dump(itemData, f)
                            f.close()
                        else:
                            # read item json
                            f = open('./minecraft/models/item/'+splitItems+'.json', 'r')
                            itemData = json.load(f)
                            f.close()
                            
                            itemData['overrides'].append({ "predicate": { "custom_model_data": tmpMax }, "model": "item/"+folder+"/"+str(tmpMax)+""})

                            # write item json
                            f = open('./minecraft/models/item/'+splitItems+'.json', "w")
                            json.dump(itemData, f)
                            f.close()

                    ## Copy and link parent
                    if(data.get('parent')):
                        citParentName = data.get('parent').split('/')[-1]
                        if(os.path.exists(dir+citParentName+'.json') and os.path.isfile(dir+citParentName+'.json')):
                            if(not os.path.exists('./minecraft/models/item/'+citParentName+'.json') or not os.path.isfile('./minecraft/models/item/'+citParentName+'.json')):
                                shutil.copyfile(dir+citParentName+'.json', './minecraft/models/item/'+citParentName+'.json')
                                # read item json
                                f = open('./minecraft/models/item/'+citParentName+'.json', 'r')
                                itemData = json.load(f)
                                f.close()

                                if(itemData.get('parent')):
                                    if('./' in itemData.get('parent')):
                                        itemData['parent'] = 'minecraft:item/'+itemData.get('parent').split('/')[-1]

                                # write item json
                                f = open('./minecraft/models/item/'+citParentName+'.json', "w")
                                json.dump(itemData, f)
                                f.close()
                            data['parent'] = 'minecraft:item/'+citParentName
                

                    ## Copy and link texture
                    for texture in data.get('textures'):
                        if(not os.path.exists('./minecraft/textures/block') or not os.path.isdir('./minecraft/textures/block')):
                            os.mkdir('./minecraft/textures/block')
                        if(not os.path.exists('./minecraft/textures/items') or not os.path.isdir('./minecraft/textures/items')):
                            os.mkdir('./minecraft/textures/items')
                        pngModel = data['textures'][texture].split("/")[-1]+'.png'
                        if('./' in data['textures'][texture]):
                            if(os.path.exists(dir+pngModel) and os.path.isfile(dir+pngModel)):
                                if(not os.path.exists('./minecraft/textures/block/'+folder) or not os.path.isdir('./minecraft/textures/block/'+folder)):
                                    os.mkdir('./minecraft/textures/block/'+folder)
                                jsonDir = 'block/'+folder+'/'+data['textures'][texture].split("/")[-1]
                                textureDir = './minecraft/textures/'+jsonDir
                                if(not os.path.exists(textureDir+'.png') or not os.path.isfile(textureDir+'.png')):
                                    shutil.copyfile(dir+pngModel, textureDir+'.png')
                                data['textures'][texture] = jsonDir
                        else:
                            if(os.path.exists(input+'/assets/minecraft/textures/'+data['textures'][texture]+'.png') and os.path.isfile(input+'/assets/minecraft/textures/'+data['textures'][texture]+'.png')):
                                textureDir = './minecraft/textures/'+data['textures'][texture].split("/")[0]
                                if(not os.path.exists(textureDir) or not os.path.isdir(textureDir)):
                                    os.mkdir(textureDir)
                                textureDir = textureDir+'/'+folder
                                if(not os.path.exists(textureDir) or not os.path.isdir(textureDir)):
                                    os.mkdir(textureDir)
                                jsonNewPath = data['textures'][texture].split("/")[0]+'/'+folder+'/'+data['textures'][texture].split('/')[-1]
                                newPath = './minecraft/textures/'+jsonNewPath
                                if(not os.path.exists(newPath+'.png') or not os.path.isfile(newPath+'.png')):
                                    shutil.copyfile(input+'/assets/minecraft/textures/'+data['textures'][texture]+'.png', newPath+'.png')
                                data['textures'][texture] = jsonNewPath
                    ## write item json
                    f = open(itemPath+'/'+str(tmpMax)+'.json', "w")
                    json.dump(data, f)
                    f.close()
                except FileNotFoundError as identifier:
                    warn('json file not found: {0} linked in: {1}'.format(itemPath+'/'+str(tmpMax)+'.json', dir+model))
        continue
    info("Resource Pack Generated")
    
    #     if(output is None):
    #         print(results)
    #     else:
    #         with open(output, "wb") as outfile:
    #             outfile.write(results)



##Progresse Bar from Pouknouki (https://openclassrooms.com/forum/sujet/python-barre-de-progression)
# Print iterations progress
class ProgressBar:
    iteration = 0
    total = 0
    prefix = ''
    suffix = ''
    decimals = 2
    barLength = 100
     
    usePercentage = True
     
    label = ''
     
    fillingChar = '='
    emptyChar = ' ' #-
    beginChar = '['
    endChar = ']'
     
    def __init__(self, iteration, total = 100, fillingChar = '=', emptyChar = ' ', beginChar = '[', endChar = ']', prefix = '', suffix = '', decimals = 2, barLength = 30, **kwargs):
        self.iteration = iteration
        self.total = total
        self.fillingChar = fillingChar
        self.emptyChar = emptyChar
        self.beginChar = beginChar
        self.endChar = endChar
        self.prefix = prefix
        self.suffix = suffix
        self.decimals = decimals
        self.barLength = barLength
        if kwargs.get("label") != None:
            self.label = kwargs.get("label")
 
        if kwargs.get("usePercentage") == False:
            self.usePercentage = False
        else:
            self.usePercentage = True
             
        self.updateProgress(iteration, self.label)
     
    def updateProgress(self, iteration, label):
 
        self.iteration = iteration
        self.label = label
        filledLength    = int(round(self.barLength * self.iteration / float(self.total)))
        percents        = round(100.00 * (iteration / float(self.total)), self.decimals)
        bar             = self.fillingChar * filledLength + self.emptyChar * (self.barLength - filledLength)
 
        sys.stdout.write("\r                                                                            ")
        if self.usePercentage:
            sys.stdout.write('\r%s %s%s%s %s%s %s' % (self.prefix, self.beginChar, bar, self.endChar, percents, '%', self.suffix)),
        else:
            sys.stdout.write('\r%s %s%s%s %s %s' % (self.prefix, self.beginChar, bar, self.endChar, label, self.suffix)),
        sys.stdout.flush()
        if self.iteration == self.total:
            sys.stdout.write('\n')
            sys.stdout.flush()


def _log(message: str, color: str = ''):
        sys.stderr.write('{0}{1}- {2}{3}{4}'.format(color, datetime.now().strftime('%Y-%m-%d %H:%M:%S'), message, bcolors.RESET, os.linesep))

def debug(message: str):
    if(verbose):
        _log('DEBUG: {0}'.format(message), bcolors.OKGREEN)

def info(message: str):
    _log('INFO: {0}'.format(message), bcolors.OKBLUE)

def warn(message: str):
    _log('WARNING: {0}'.format(message), bcolors.WARNING)

def error(message: str, code: int = -1):
    _log('ERROR: {0}'.format(message), bcolors.FAIL)
    exit(code)

class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    RESET = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

if __name__ == "__main__":
    input = None
    output = None
    if len(sys.argv) == 1:
        info(get_usage())
        exit(0)
    else:
        for arg in range(1, len(sys.argv), 1):
            if(sys.argv[arg].startswith('-')):
                if sys.argv[arg] in ['-o', '--output']:
                    arg+=1
                    output = sys.argv[arg]
                elif sys.argv[arg] in ['-v', '--verbose']:
                    verbose = True
                elif(sys.argv[arg] in ['-h', '--help']):
                    _log('HELP: {0}'.format(get_usage()), bcolors.OKBLUE)
                    exit(0)
                else:
                    error('Unkown argument {0}'.format(sys.argv[arg]), 2)
            else:
                input = sys.argv[arg]

    if(input is None):
        error('You must specify the input XLSX file.{0}\t See help for more info'.format(os.linesep))
    main(input, output)
