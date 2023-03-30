import os
from rayleigh_diagnostics import build_file_list
class output_desc:
    def __init__(self):
        self.tar = False
        self.copy=True
        self.count = -1



def backup(idir,odir,qdict,imax=99999999,imin=0):
    dirs = ['AZ_Avgs', 'Benchmark_Reports', 'Equatorial_Slices', 'G_Avgs', 'Meridional_Slices', 'Points_Probes', 'Shell_Avgs', 'Shell_Slices', 'Shell_Spectra', 'SPH_Modes', 'Timings']
   
    dirs = ['G_Avgs', 'Shell_Slices']
    
    for d in dirs:
        qinfo = qdict[d]
        data_dir = idir+'/'+d    
        ifiles = build_file_list(imin,imax,path=data_dir)
        print(d, len(ifiles))
        print(ifiles)
        print('\n\n\n')
        


