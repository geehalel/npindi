# Copyright 2018 geehalel@gmail.com
#
# This file is part of npindi.
#
#    npindi is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    npindi is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with npindi.  If not, see <http://www.gnu.org/licenses/>.

import math
import gzip
BSC_FIELDS = {'hr': (1,4, int),
              'rahour':(76,2, int), 'ramin':(78,2,int), 'rasec':(80,4,float),
              'design':(84,1,bytes), 'dedeg': (85,2,int), 'demin': (87,2,int),
              'desec': (89,2, int), 'vmag':(103,5,float)
              }

def load_bright_star_5(filename, verbose=False):
    #f=open(filename)
    f=gzip.GzipFile(filename)
    l=f.readline()
    linecount=1
    starcount=0
    starerr=0
    catalog=[]
    while l != b'':
        #print(l)
        skipstar=False
        bscstar=dict()
        for fdesc, fuple in BSC_FIELDS.items():
            try:
                bscstar[fdesc]=fuple[2](l[fuple[0]-1:fuple[0]+fuple[1]-1])
            except:
                if verbose:
                    print("Error importing "+fdesc+"("+str(fuple[2])+") for star "+str(linecount))
                skipstar = True
                starerr+=1
        # valid id for this star
        if not(skipstar) and bscstar['hr'] != None and bscstar['hr'] != '    ':
            # copy fields
            star=dict()
            star['nom']='HR'+str(bscstar['hr'])
            star['mag']=bscstar['vmag']
            star['ra_degres']=bscstar['rahour']*15.0 + ((bscstar['ramin']*60.0+bscstar['rasec'])*15.0) / 3600.0
            star['de_degres']=bscstar['dedeg'] + (bscstar['demin']*60.0 + bscstar['desec'])/3600.0
            if bscstar['design']==b'-':
                star['de_degres']=-star['de_degres']
            star['ra'] = math.radians(star['ra_degres'])
            # pour que (0,0) soit au centre de la carte, il faut décaler les points
            # de l'intervalle ]+pi, +2*pi] vers l'intervalle ]-pi, 0.0]
            if star['ra'] > math.pi:
                star['ra'] = star['ra'] - 2.0 * math.pi
            star['de'] = math.radians(star['de_degres'])
            catalog.append(star)
            starcount+=1
        else:
            if verbose:
                print("Not a valid id for star at line "+str(linecount))
        l=f.readline()
        linecount+=1
    f.close()
    print("Bright Star 5 catalog: read "+str(linecount)+" lines, " +
          "found "+str(starcount)+" stars ("+str(starerr)+" errors)")
    return catalog
