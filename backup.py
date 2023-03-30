import os
from rayleigh_diagnostics import build_file_list
class output_desc:
    def __init__(self):
        self.tar = False
        self.copy=True
        self.count = -1
        self.sample = 'dense' # or 'sparse'



def backup(idir,odir,qdict,imax=99999999,imin=0):
    dirs = ['AZ_Avgs', 'Benchmark_Reports', 'Equatorial_Slices', 'G_Avgs', 'Meridional_Slices', 'Points_Probes', 'Shell_Avgs', 'Shell_Slices', 'Shell_Spectra', 'SPH_Modes', 'Timings']
   
    dirs = ['G_Avgs', 'Shell_Avgs', 'Shell_Slices']
    
    for d in dirs:
        qinfo = qdict[d]
        
        data_dir = idir+'/'+d    
        ifiles = build_file_list(imin,imax,path=data_dir)
        nfiles = len(ifiles)
        
        count = qinfo.count
        if (count == -1) or (count > nfiles):
            count = nfiles
            
        if (count > 0):
            if (qinfo.sample == 'dense'):
                ifiles = ifiles[nfiles-count:nfiles]
            elif (qinfo.sample == 'sparse'):
                dcount = (nfiles-1)//(count-1)
                files = [ifiles[0]]
                for i in range(dcount,nfiles,dcount):
                    files.append(ifiles[i])
                    lasti = i
                
                # Make sure that we:
                # i) Get the first and last file
                # ii) Get no more than the number of  files requested.
                if(lasti != nfiles-1):
                    nf = len(files)
                    if (nf < count):
                        files.append(ifiles[nfiles-1])
                    else:
                        files[nf-1] = ifiles[nfiles-1]
                    
                nf = len(files)
                if (nf > count):
                    files = files[0:nf]
                    files[nf-1] = ifiles[nfiles-1]
                    
                ifiles = files
                
            print(d, len(ifiles))
            print(ifiles)
            print('\n\n\n')
        


