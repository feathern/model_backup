import os
from rayleigh_diagnostics import build_file_list
class output_desc:
    def __init__(self):
        self.tar = False
        self.copy=True
        self.count = -1
        self.sample = 'dense' # or 'distributed' or 'both'


def sparse_sample(ifiles,count):
    nfiles = len(ifiles)
    if (count > nfiles):
        count = nfiles
    if (nfiles > 0):
        dcount = (nfiles-1)//(count-1)
        files = [ifiles[0]]
        for i in range(dcount,nfiles,dcount):
            files.append(ifiles[i])
            lasti = i
        
        ###################################################
        # Make sure that we:
        # i) Get the first and last file
        # ii) Get no more than the number of  files 
        #     requested.
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
    else:
        ifiles = []
    return ifiles



def backup(idir,odir,qdict,imax=99999999,imin=0,check=False, verbose = False):
    dirs = ['AZ_Avgs', 'Benchmark_Reports', 'Equatorial_Slices', 'G_Avgs', 'Meridional_Slices', 'Points_Probes', 'Shell_Avgs', 'Shell_Slices', 'Shell_Spectra', 'SPH_Modes', 'Timings']

    print('Backing up from: ',idir,' to: ', odir)

    dirs = ['G_Avgs', 'Shell_Avgs', 'Shell_Slices']

    misc_files = ['equation_coefficients', 'grid_info', 'jobinfo.txt', 'main_input']
    
    mkdir1 = 'mkdir -p '+odir
    if (not check):
        os.system(mkdir1)
    
    if (check):
        print('')
        print('The "check" flag has been set to True.')
        print('Commands will be printed to the screen, but not executed.')
        print('Remove check=True flag and re-run to peform backup.')
    
    if (check or verbose):
        print('')
        print(mkdir1)
        print('')

    ####################################################################
    # (1) First copy/tar the files in misc_files (main_input etc.)
    tarfile = odir+'/misc.tar' # The tarball
    tarlist_file = os.getcwd()+'/misc_temp_list.txt' # Will contain 1 filename per line to include in tarball
    tarfiles = open(tarlist_file,"w")
    for f in misc_files:
        tarfiles.write(f+'\n')
    tarfiles.close()
    tar_cmd = 'tar -C '+ idir + ' -cf '+tarfile +' -T '+tarlist_file
    rm_cmd = 'rm '+tarlist_file    
    
    
    if (check or verbose):
        print(tar_cmd)
        print('')
    if (not check):
        os.system(tar_cmd)
        os.system(rm_cmd)       
            
            
            
            
    #####################################################################
    # (2) Next backup the data directories        
    for d in dirs:
        print('\n\nBacking up directory: ', d, end='\n\n')
        qinfo = qdict[d]
        
        data_dir = idir+'/'+d    
        ifiles = build_file_list(imin,imax,path=data_dir)
        nfiles = len(ifiles)
        
        count = qinfo.count
        if (type(count) == type(1)):
            if (count == -1) or (count > nfiles):
                count = nfiles
        else:
            #count is a two-element array [dense, sparse]
            for i in range(2):
                if ((count[i] > nfiles) or (count[i] == -1)):
                    count[i] = nfiles
                    
            dense_count = count[0]
            sparse_count = count[1]
            count=max(dense_count,sparse_count)
            
        if (count > 0):
        
            if (qinfo.sample == 'dense'):
                ifiles = ifiles[nfiles-count:nfiles]
                
            elif (qinfo.sample == 'sparse'):
                ifiles = sparse_sample(ifiles,count)
            elif (qinfo.sample == 'both'):
                dense_files = ifiles[nfiles-dense_count:nfiles]
                sparse_files = sparse_sample(ifiles,sparse_count)
                in_dense = set(dense_files)
                in_sparse = set(sparse_files)

                in_sparse_but_not_in_dense = in_sparse - in_dense

                ifiles = dense_files + list(in_sparse_but_not_in_dense)
                
            cmds = []

            
            if (qinfo.tar):
                tarfile = odir+'/'+d+'.tar' # The tarball
                tarlist_file = os.getcwd()+'/'+d+'_temp_list.txt' # Will contain 1 filename per line to include in tarball
                
                #######################################################
                # Create a list of files that we store in a txt file
                #   and pass to the tar command
                flist = []

                for ifile in ifiles:
                    ff = ifile.split(d)
                    ff = d+'/'+ff[1]
                    flist.append(ff)

                tarfiles = open(tarlist_file,"w")
                for f in flist:
                    tarfiles.write(f+'\n')
                tarfiles.close()
                tar_cmd = 'tar -C '+ idir + ' -cf '+tarfile +' -T '+tarlist_file
                rm_cmd = 'rm '+tarlist_file    
                cmds.append(tar_cmd)
                cmds.append(rm_cmd)
                
            if (qinfo.copy):
                dest_dir = odir+'/'+d
                mkdir2 = 'mkdir '+dest_dir
                cmds.append(mkdir2)
                            
                for ifile in ifiles:

                    dest = odir+'/'+d+'/.'
                    cp_cmd = 'cp -r '+ifile+' '+dest
                    cmds.append(cp_cmd)
                    
                    
            if (len(cmds) > 0):
                ending = '\n'
                if (qinfo.tar):
                    ending+='\n'
           
                for cmd in cmds:
                    if (verbose or check):
                        print(cmd, end = ending)  
                    if (not check):  
                        os.system(cmd)


    ####################################################
    # (3)  Finally, back up the checkpoint directories
    print('\n\nBacking up Checkpoints \n')
    icheckdir = idir+'/Checkpoints'
    ocheckdir = odir+'/Checkpoints'
    mkdir3 = 'mkdir '+ocheckdir
    
    if (verbose or check):
        print('')
        print(mkdir3)
        print('')
    if (not check):
        os.system(mkdir3)
        
        
    # Grab all quicksaves and the log files
    cfiles = ['checkpoint_log', 'last_checkpoint', 'quicksave*']
    numfiles = build_file_list(imin,imax,path=icheckdir,silent=True,nopath=True)
    
    qinfo = qdict['Checkpoints']
    numfiles = sparse_sample(numfiles,qinfo.count)

    cfiles = cfiles+numfiles
    
    for cfile in cfiles:
        copy_cmd = 'cp -r '+icheckdir+'/'+cfile+' '+ocheckdir+'/.'
        if (verbose or check):
            print(copy_cmd)
        if (not check):
            os.system(copy_cmd)
    
    
    # Now grab numbered checkpoints   


    


