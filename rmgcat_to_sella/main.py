import os
import time
import shutil
from pathlib import Path
try:
    import inputR2S
    '''
    User defined parameters. Here we only read them. They are set up in inputR2S.py (submit directory)
    '''
    facetpath = inputR2S.facetpath
    slab_name = inputR2S.slab_name
    surface_type = inputR2S.surface_type
    symbol = inputR2S.symbol
    a = inputR2S.a
    vacuum = inputR2S.vacuum
    pseudo_dir = inputR2S.pseudo_dir
    pseudopotentials = inputR2S.pseudopotentials
    slabopt = inputR2S.slabopt
    yamlfile = inputR2S.yamlfile
    repeats = inputR2S.repeats
    repeats_surface = inputR2S.repeats_surface
    rotAngle = inputR2S.rotAngle
    scfactor = inputR2S.scfactor
    scfactor_surface = inputR2S.scfactor_surface
    # sp1 = inputR2S.sp1
    # sp2 = inputR2S.sp2
    scaled1 = inputR2S.scaled1
    scaled2 = inputR2S.scaled2
    # species_list = [sp1, sp2]
    species_list = inputR2S.species_list
    slab_opt = inputR2S.slab_opt_script
    SurfaceAdsorbate = inputR2S.SurfaceAdsorbateScript
    TSxtb = inputR2S.TSxtbScript
    TS = inputR2S.TSScript
    IRC = inputR2S.IRCScript
    IRCopt = inputR2S.IRCoptScript

except ImportError:
    print('Missing input file. You cannot run calculations but will be able to use most of the workflow.')

# These template and pytemplate scripts can be modified by users to tune
# them to given calculation setup, i.e. calculator, method, queue menager,
# etc. The current version works for SLURM and Quantum Espresso.

path = os.path.abspath(__file__)
dir_path = os.path.dirname(path)
path_template = os.path.join(dir_path, 'jobtemplate/')
path_pytemplate = os.path.join(dir_path, 'pytemplate/')
template_slab_opt = os.path.join(
    path_template + '00_template_set_up_slab_opt.py')
template_ads = os.path.join(path_template + '01_template_set_up_ads.py')
template_set_up_ts_with_xtb = os.path.join(
    path_template + '02_template_set_up_ts_with_xtb.py')
template_set_up_ts = os.path.join(
    path_template + '03_template_checksym_xtb_runTS.py')
template_set_up_IRC = os.path.join(path_template + '04_template_set_up_irc.py')
template_set_up_optIRC = os.path.join(
    path_template + '05_template_set_up_opt_after_irc.py')
pytemplate_relax_ads = os.path.join(
    path_pytemplate + 'pytemplate_relax_Cu_111_ads.py')
pytemplate_xtb = os.path.join(path_pytemplate + 'pytemplate_set_up_xtb.py')
pytemplate_set_up_ts = os.path.join(
    path_pytemplate + 'pytemplate_set_up_ts.py')
pytemplate_f = os.path.join(path_pytemplate + 'pytemplate_set_up_irc_f.py')
pytemplate_r = os.path.join(path_pytemplate + 'pytemplate_set_up_irc_r.py')
pytemplate_optIRC = os.path.join(
    path_pytemplate + 'pytemplate_set_up_opt_irc.py')

slab_opt = inputR2S.slab_opt_script
SurfaceAdsorbate = inputR2S.SurfaceAdsorbateScript
TSxtb = inputR2S.TSxtbScript
TS = inputR2S.TSScript
IRC = inputR2S.IRCScript
IRCopt = inputR2S.IRCoptScript
##
currentDir = os.path.dirname(os.getcwd())
# sp1 = inputR2S.sp1
# sp2 = inputR2S.sp2
# facetpath = inputR2S.facetpath
optimize_slab = inputR2S.optimize_slab

####################################################
#################### Initialize ####################
####################################################


class WorkFlow:
    # def __init__(self, facetpath):
    #     self.facetpath = facetpath

    def gen_job_files(self):
        ''' Generate submt scripts for 6 stages of the workflow '''
        WorkFlow.set_up_slab(self, template_slab_opt, surface_type, symbol, a,
                             repeats_surface, vacuum, slab_name,
                             pseudopotentials, pseudo_dir)
        WorkFlow.set_up_ads(self, template_ads, facetpath, slabopt,
                            repeats, yamlfile, pytemplate_relax_ads,
                            pseudopotentials, pseudo_dir)
        WorkFlow.set_up_TS_with_xtb(self, template_set_up_ts_with_xtb, slabopt,
                                    repeats, yamlfile, facetpath, rotAngle,
                                    scfactor, scfactor_surface, pytemplate_xtb,
                                    species_list)
        WorkFlow.set_up_run_TS(self, template_set_up_ts, facetpath, slabopt,
                               repeats, yamlfile, pytemplate_set_up_ts,
                               pseudopotentials, pseudo_dir)
        WorkFlow.set_up_run_IRC(self, template_set_up_IRC, facetpath, slabopt,
                                repeats, pytemplate_f, pytemplate_r, yamlfile,
                                pseudopotentials, pseudo_dir)
        WorkFlow.set_up_opt_IRC(self, template_set_up_optIRC,
                                facetpath, slabopt, repeats,
                                pytemplate_optIRC,
                                pseudopotentials, pseudo_dir)

###########################
#   Create submit files   #
###########################

    def set_up_slab(self, template, surface_type, symbol, a, repeats_surface,
                    vacuum, slab_name, pseudopotentials, pseudo_dir):
        ''' Create 00_set_up_slab_opt.py file '''
        with open(template, 'r') as r:
            template = r.read()
            with open('00_set_up_slab_opt.py', 'w') as c:
                c.write(template.format(surface_type=surface_type,
                                        symbol=symbol, a=a,
                                        repeats_surface=repeats_surface,
                                        vacuum=vacuum, slab_name=slab_name,
                                        pseudopotentials=pseudopotentials,
                                        pseudo_dir=pseudo_dir))
            c.close()
        r.close()

    def set_up_ads(self, template, facetpath, slabopt, repeats, yamlfile,
                   pytemplate, pseudopotentials, pseudo_dir):
        ''' Create 01_set_up_ads.py file '''
        with open(template, 'r') as r:
            template = r.read()
            with open('01_set_up_ads.py', 'w') as c:
                c.write(template.format(facetpath=facetpath, slabopt=slabopt,
                                        yamlfile=yamlfile, repeats=repeats,
                                        pytemplate=pytemplate,
                                        pseudopotentials=pseudopotentials,
                                        pseudo_dir=pseudo_dir))
            c.close()
        r.close()

    def set_up_TS_with_xtb(self, template, slab,
                           repeats, yamlfile, facetpath, rotAngle,
                           scfactor, scfactor_surface,
                           pytemplate_xtb, species_list):
        ''' Create 02_set_up_TS_with_xtb.py file'''
        with open(template, 'r') as r:
            template = r.read()
            with open('02_set_up_TS_with_xtb.py', 'w') as c:
                c.write(template.format(facetpath=facetpath, slab=slab,
                                        repeats=repeats, yamlfile=yamlfile,
                                        rotAngle=rotAngle, scfactor=scfactor,
                                        scfactor_surface=scfactor_surface,
                                        pytemplate_xtb=pytemplate_xtb,
                                        species_list=species_list,
                                        scaled1=scaled1, scaled2=scaled2))
            c.close()
        r.close()

    def set_up_run_TS(self, template, facetpath, slab, repeats, yamlfile,
                      pytemplate, pseudopotentials, pseudo_dir):
        ''' Create 03_checksym_xtb_runTS.py file '''
        with open(template, 'r') as r:
            template = r.read()
            with open('03_checksym_xtb_runTS.py', 'w') as c:
                c.write(template.format(facetpath=facetpath, slab=slab,
                                        repeats=repeats, yamlfile=yamlfile,
                                        pytemplate=pytemplate,
                                        pseudo_dir=pseudo_dir,
                                        pseudopotentials=pseudopotentials))
            c.close()
        r.close()

    def set_up_run_IRC(self, template, facetpath, slab, repeats,
                       pytemplate_f, pytemplate_r, yamlfile,
                       pseudopotentials, pseudo_dir):
        ''' Create 04_set_up_irc.py file '''
        with open(template, 'r') as r:
            template = r.read()
            with open('04_set_up_irc.py', 'w') as c:
                c.write(template.format(facetpath=facetpath,
                                        slab=slab,
                                        repeats=repeats,
                                        pytemplate_f=pytemplate_f,
                                        pytemplate_r=pytemplate_r,
                                        yamlfile=yamlfile,
                                        pseudo_dir=pseudo_dir,
                                        pseudopotentials=pseudopotentials))
            c.close()
        r.close()

    def set_up_opt_IRC(self, template, facetpath, slab, repeats, pytemplate,
                       pseudopotentials, pseudo_dir):
        ''' Create 05_set_up_opt_after_irc.py file'''
        with open(template, 'r') as r:
            template = r.read()
            with open('05_set_up_opt_after_irc.py', 'w') as c:
                c.write(template.format(facetpath=facetpath,
                                        slab=slab,
                                        repeats=repeats,
                                        pytemplate=pytemplate,
                                        yamlfile=yamlfile,
                                        pseudo_dir=pseudo_dir,
                                        pseudopotentials=pseudopotentials))
            c.close()
        r.close()

##############################
# Submit jobs and execute it #
##############################

    def get_slurm_jobs_id(self, slurm_id_subm):
        ''' Get slurm IDs of just submitted jobs '''
        slurm_jobs_id = []
        with open(slurm_id_subm, 'r') as f:
            for line in f.readlines():
                line = line.split()[3]
                slurm_jobs_id.append(line)
        f.close()
        return slurm_jobs_id

    def gen_slurm_command(self, slurm_id_subm):
        ''' Prepare a bash command to submit jobs '''
        slurmID = WorkFlow.get_slurm_jobs_id(self, slurm_id_subm)
        slurmID = ",".join(["{}"] * len(slurmID)).format(*slurmID)
        # if not slurmID:
        #     print('Error')
        #     sys.exit('No submitted jobs, probably all files have been already generated')
        #     return command = False
        # else:
        command = os.path.join('sbatch --dependency=afterany:' + str(slurmID))
        return command

    def run(self, slurm_id_subm, job_script):
        ''' Submit slurm jobs '''
        command = WorkFlow.gen_slurm_command(self, slurm_id_subm)
        os.popen(str(os.path.join(command + ' ' + job_script)))

    def exe(self, prevSlurmID, job_script):
        ''' Check if the previous step of calculations terminated.
        If so, run the next step'''
        while not os.path.exists(prevSlurmID):
            time.sleep(60)
        WorkFlow.run(self, prevSlurmID, job_script)

    def check_if_path_to_mimina_exists(self, WorkFlowDir, species):
        ''' Check for the paths to previously calculated minima and return
            a list with all valid paths '''

        pathlist = Path(WorkFlowDir).glob('**/minima/' + species)
        paths = []
        for path in pathlist:
            # path = str(path)
            paths.append(str(path))
            return paths[0]
        if IndexError:
            return None

    def check_if_path_to_out_files_exists(self, work_flow_dir, species):
        ''' Check for the previously calculated *relax.out files for a given
            species in a WorkFlowDir '''

        keyphrase = os.path.join('minima/' + species + '*relax.out')
        outfile_lists = Path(work_flow_dir).glob(keyphrase)
        outfiles = []
        for outfile in outfile_lists:
            outfiles.append(str(outfile))
        if not outfiles:
            return(False, )
        else:
            return (True, outfiles)

    def check_if_minima_already_calculated(self, currentDir, species,
                                           facetpath):
        ''' Check for previously calculated minima '''
        WorkFlowDirs = []
        keyphrase = '**/{}*/'.format(facetpath)
        # keyphrase = '*{}*'.format(facetpath)
        WorkFlowDirsList = Path(str(currentDir)).glob(keyphrase)
        # find all dirs matching the keyphrase - should be something like
        # '*/01_Cu_111_methanol_OH_O+H_rot_angle_24_struc/Cu_111/'
        for WorkFlowDir in WorkFlowDirsList:
            WorkFlowDirs.append(WorkFlowDir)
        # go through all dirs and look for the match
        for WorkFlowDir in WorkFlowDirs:
            print(WorkFlowDir)
            try:
                check_out_files, path_to_outfiles = WorkFlow.check_if_path_to_out_files_exists(
                    self, WorkFlowDir, species)
                # if there is a match, break the loop
                if check_out_files:
                    break
            except ValueError:
                # if False, I have only one value to unpack, so a workaround
                continue
            
        # a directory to the DFT calculation (unique_minima_dir) for a given
        # species is generated by combining the first element of the splitted
        # path to outfiles,
        # i.e.['*/Cu_111/minima/','H_01_relax.out'] so the ('*/Cu_111/minima/'
        # part) with the name of the species. Finally the path is like:
        # '*/Cu_111/minima/H'
        unique_minima_dir = os.path.join(
            os.path.split(path_to_outfiles[0])[0], species)

        # If species were previously calculated, return True and paths
        if path_to_outfiles:
            return True, unique_minima_dir, path_to_outfiles
        else:
            (False, )

    def run_slab_optimization(self):
        ''' Submit slab_optimization_job '''
        # submit slab_optimization_job
        run_slab_command = os.path.join(
            'sbatch ' + slab_opt + ' > submitted_00.txt')
        run_slab_opt = os.popen(run_slab_command)
        print(run_slab_opt.read())

    def run_opt_surf_and_adsorbate(self):
        ''' Run optmization of adsorbates on the surface '''
        return WorkFlow.exe(self, 'submitted_00.txt', SurfaceAdsorbate)

    def run_opt_surf_and_adsorbate_no_depend(self):
        ''' Run optmization of adsorbates on the surface
            if there is no dependency on other jobs '''
        bash_command = os.popen(os.path.join(
            'sbatch ' + SurfaceAdsorbate))
        print(bash_command.read())

    def run_ts_estimate(self, submit_txt):
        ''' Run TS estimation calculations '''
        return WorkFlow.exe(self, submit_txt, TSxtb)

    def run_ts_estimate_no_depend(self):
        ''' Run TS estimate calculations if there is
            no dependency on other jobs '''
        bash_command = os.popen(os.path.join(
            'sbatch ' + TSxtb))
        print(bash_command.read())

    def check_all_species(self):
        ''' Check all species to find whether there are previous calculation
            the code can use

        Return:
        _______
        all_sp_checked : list(tuple(bool, str=None))
            a list of tuples with info whether a species were calculated
            (True, path_to_prev_calc)
            or not
            (False, )
        '''
        all_sp_checked = []
        for species in species_list:
            check_sp = WorkFlow.check_if_minima_already_calculated(
                self, currentDir, species, facetpath)
            all_sp_checked.append(check_sp)
        return all_sp_checked

    def check_if_slab_opt_exists(self):
        ''' Check whether slab has been already optimized

        Returns : tuple(bool, str=None):
            True if there are previous calculations
                (True, path_to_prev_calc)
            False otherwise
                (False, )

        '''
        slab_opt_path_str = []
        # the code will look for anything like Cu_111*.xyz starting from the
        # facetpath directory including all subdirectories.
        keyphrase = '**/*' + str(facetpath) + '*.xyz'
        slab_opt_path_posix = Path(str(currentDir)).glob(keyphrase)
        for slab_opt_path in slab_opt_path_posix:
            slab_opt_path_str.append(slab_opt_path)
        if len(slab_opt_path_str) >= 1:
            return True, slab_opt_path_str[0]
        else:
            return (False, )

    def copy_slab_opt_file(self):
        ''' Copy .xyz of previously optimized slab '''
        if WorkFlow.check_if_slab_opt_exists(self):
            src = WorkFlow.check_if_slab_opt_exists(self)[1]
            dst = os.getcwd()
            shutil.copy2(src, dst)

    def execute(self):
        ''' The main executable '''
        # checksp1, checksp2 = WorkFlow.check_all_species(self)
        # Below, I have a list of tuples with all
        all_species_checked = WorkFlow.check_all_species(self)
        # It more convenient to have a list of bools
        sp_check_list = [
            False for species in all_species_checked if not species[0]]

        if optimize_slab:
            # If the code cannot locate optimized slab .xyz file,
            # a slab optimization will be launched.
            # a = WorkFlow.check_if_slab_opt_exists(self)
            if not WorkFlow.check_if_slab_opt_exists(self):
                WorkFlow.run_slab_optimization(self)
                # wait a bit in case the file write process is too slow
                while not os.path.exists('submitted_00.txt'):
                    time.sleep(3)
            else:
                WorkFlow.copy_slab_opt_file(self)
            # check whether species were already cacluated)
            if all(sp_check_list):
                # If all are True, start by generating TS guesses and run
                # the penalty function minimization
                WorkFlow.run_ts_estimate_no_depend(self)
                # WorkFlow.run_ts_estimate(self, 'submitted_00.txt')
            else:
                # If any of these is False
                # run optimization of surface + reactants; surface + products
                if os.path.exists('submitted_00.txt'):
                    # this is executed when slab was optimized in the
                    # current run, because 'submitted_00.txt' was generated
                    WorkFlow.run_opt_surf_and_adsorbate(self)
                else:
                    # otherwise run no_depend version
                    # ('submitted_00.txt' not generated)
                    WorkFlow.run_opt_surf_and_adsorbate_no_depend(self)
                # run calculations to get TS guesses
                WorkFlow.run_ts_estimate(self, 'submitted_01.txt')

        else:
            # this is executed if user provide .xyz with the optimized slab
            # check whether sp1 and sp2 was already cacluated
            if WorkFlow.check_if_slab_opt_exists(self):
                pass
            else:
                raise FileNotFoundError(
                    'It appears that there is no slab_opt.xyz file')

            if all(sp_check_list):
                # If all minimas were calculated some time age for the other
                # reactions, rmgcat_to_sella will use that calculations.
                WorkFlow.run_ts_estimate_no_depend(self)
            else:
                # run optimization of surface + reactants; surface + products
                WorkFlow.run_opt_surf_and_adsorbate_no_depend(self)
                # wait until optimization of surface + reactants;
                # surface + products finish and submit calculations
                # to get TS guesses
                WorkFlow.exe(self, 'submitted_01.txt', TSxtb)

        # search for the 1st order saddle point
        WorkFlow.exe(self, 'submitted_02.txt', TS)
        # for each distinct TS, run IRC calculations
        WorkFlow.exe(self, 'submitted_03.txt', IRC)
        # run optimizataion of both IRC (forward, reverse) trajectory
        WorkFlow.exe(self, 'submitted_04.txt', IRCopt)
