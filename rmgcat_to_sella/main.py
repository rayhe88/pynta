#!/usr/bin/env python3
import os
import shutil
from pathlib import Path
from warnings import warn
try:
    import inputR2S
    """
    User defined parameters.

    Here we only read them. They are set up in inputR2S.py (submit directory)
    """
except ImportError:
    warn(
        'Missing input file. You cannot run calculations '
        'but will be able to use most of the workflow.'
    )
else:
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
    executable = inputR2S.executable
    balsam_exe_settings = inputR2S.balsam_exe_settings
    calc_keywords = inputR2S.calc_keywords
    creation_dir = inputR2S.creation_dir
#    from pathlib import Path
#    creation_dir = Path.cwd().as_posix()


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
#                    Initialize                    #
####################################################


class WorkFlow:

    def __init__(self):
        """Setup the balsam application for this workflow run.

        Once we start using QE will want one app for QE,
        one for xtb most likely
        """
        from balsam.core.models import ApplicationDefinition
        self.myPython, self.app_created = \
            ApplicationDefinition.objects.get_or_create(
                name="Python", executable="python3"
            )
        self.myPython.save()
        self.slab_opt_job = ''
        # envscript="/path/to/setup-envs.sh",
        # postprocess="python /path/to/post.py"
    # def __init__(self, facetpath):
    #     self.facetpath = facetpath

    def gen_job_files(self):
        ''' Generate submt scripts for 6 stages of the workflow '''
        self.set_up_slab(template_slab_opt, surface_type, symbol, a,
                         repeats_surface, vacuum, slab_name,
                         pseudopotentials, pseudo_dir, executable,
                         balsam_exe_settings, calc_keywords, creation_dir)
        self.set_up_ads(template_ads, facetpath, slabopt,
                        repeats, yamlfile, pytemplate_relax_ads,
                        pseudopotentials, pseudo_dir, executable,
                        balsam_exe_settings, calc_keywords, creation_dir)
        self.set_up_TS_with_xtb(template_set_up_ts_with_xtb, slabopt,
                                repeats, yamlfile, facetpath, rotAngle,
                                scfactor, scfactor_surface, pytemplate_xtb,
                                species_list, creation_dir)
        self.set_up_run_TS(template_set_up_ts, facetpath, slabopt,
                           repeats, yamlfile, pytemplate_set_up_ts,
                           pseudopotentials, pseudo_dir, executable,
                           balsam_exe_settings, calc_keywords, creation_dir)
        self.set_up_run_IRC(template_set_up_IRC, facetpath, slabopt,
                            repeats, pytemplate_f, pytemplate_r, yamlfile,
                            pseudopotentials, pseudo_dir, executable,
                            balsam_exe_settings, calc_keywords, creation_dir)
        self.set_up_opt_IRC(template_set_up_optIRC,
                            facetpath, slabopt, repeats,
                            pytemplate_optIRC,
                            pseudopotentials, pseudo_dir, executable,
                            balsam_exe_settings, calc_keywords, creation_dir)

###########################
#   Create submit files   #
###########################

    def set_up_slab(self, template, surface_type, symbol, a, repeats_surface,
                    vacuum, slab_name, pseudopotentials, pseudo_dir,
                    executable, balsam_exe_settings, calc_keywords,
                    creation_dir):
        ''' Create 00_set_up_slab_opt.py file '''
        with open(template, 'r') as r:
            template_text = r.read()
            with open('00_set_up_slab_opt.py', 'w') as c:
                c.write(template_text.format(
                    surface_type=surface_type,
                    symbol=symbol, a=a,
                    repeats_surface=repeats_surface,
                    vacuum=vacuum, slab_name=slab_name,
                    pseudopotentials=pseudopotentials,
                    pseudo_dir=pseudo_dir,
                    executable=executable,
                    balsam_exe_settings=balsam_exe_settings,
                    calc_keywords=calc_keywords, creation_dir=creation_dir
                ))
            c.close()
        r.close()

    def set_up_ads(
        self, template, facetpath, slabopt, repeats, yamlfile,
        pytemplate, pseudopotentials, pseudo_dir, executable,
        balsam_exe_settings, calc_keywords, creation_dir
    ):
        ''' Create 01_set_up_ads.py file '''
        with open(template, 'r') as r:
            template_text = r.read()
            with open('01_set_up_ads.py', 'w') as c:
                c.write(template_text.format(
                    facetpath=facetpath, slabopt=slabopt,
                    yamlfile=yamlfile, repeats=repeats,
                    pytemplate=pytemplate,
                    pseudopotentials=pseudopotentials,
                    pseudo_dir=pseudo_dir,
                    executable=executable,
                    balsam_exe_settings=balsam_exe_settings,
                    calc_keywords=calc_keywords,
                    creation_dir=creation_dir
                ))
            c.close()
        r.close()

    def set_up_TS_with_xtb(self, template, slab,
                           repeats, yamlfile, facetpath, rotAngle,
                           scfactor, scfactor_surface,
                           pytemplate_xtb, species_list, creation_dir):
        ''' Create 02_set_up_TS_with_xtb.py file'''
        with open(template, 'r') as r:
            template_text = r.read()
            with open('02_set_up_TS_with_xtb.py', 'w') as c:
                c.write(template_text.format(
                    facetpath=facetpath, slab=slab,
                    repeats=repeats, yamlfile=yamlfile,
                    rotAngle=rotAngle, scfactor=scfactor,
                    scfactor_surface=scfactor_surface,
                    pytemplate_xtb=pytemplate_xtb,
                    species_list=species_list,
                    scaled1=scaled1, scaled2=scaled2, creation_dir=creation_dir
                ))
            c.close()
        r.close()

    def set_up_run_TS(
        self, template, facetpath, slab, repeats, yamlfile,
        pytemplate, pseudopotentials, pseudo_dir, executable,
        balsam_exe_settings, calc_keywords, creation_dir
    ):
        ''' Create 03_checksym_xtb_runTS.py file '''
        with open(template, 'r') as r:
            template_text = r.read()
            with open('03_checksym_xtb_runTS.py', 'w') as c:
                c.write(template_text.format(
                    facetpath=facetpath, slab=slab,
                    repeats=repeats, yamlfile=yamlfile,
                    pytemplate=pytemplate,
                    pseudo_dir=pseudo_dir,
                    pseudopotentials=pseudopotentials,
                    executable=executable,
                    balsam_exe_settings=balsam_exe_settings,
                    calc_keywords=calc_keywords, creation_dir=creation_dir
                ))
            c.close()
        r.close()

    def set_up_run_IRC(self, template, facetpath, slab, repeats,
                       pytemplate_f, pytemplate_r, yamlfile,
                       pseudopotentials, pseudo_dir, executable,
                       balsam_exe_setting, calc_keywords, creation_dir):
        ''' Create 04_set_up_irc.py file '''
        with open(template, 'r') as r:
            template_text = r.read()
            with open('04_set_up_irc.py', 'w') as c:
                c.write(template_text.format(
                    facetpath=facetpath,
                    slab=slab,
                    repeats=repeats,
                    pytemplate_f=pytemplate_f,
                    pytemplate_r=pytemplate_r,
                    yamlfile=yamlfile,
                    pseudo_dir=pseudo_dir,
                    pseudopotentials=pseudopotentials,
                    executable=executable,
                    balsam_exe_settings=balsam_exe_settings,
                    calc_keywords=calc_keywords, creation_dir=creation_dir
                ))
            c.close()
        r.close()

    def set_up_opt_IRC(
        self, template, facetpath, slab, repeats, pytemplate,
        pseudopotentials, pseudo_dir, executable, balsam_exe_setting,
        calc_keywords, creation_dir
    ):
        ''' Create 05_set_up_opt_after_irc.py file'''
        with open(template, 'r') as r:
            template_text = r.read()
            with open('05_set_up_opt_after_irc.py', 'w') as c:
                c.write(template_text.format(
                    facetpath=facetpath,
                    slab=slab,
                    repeats=repeats,
                    pytemplate=pytemplate,
                    yamlfile=yamlfile,
                    pseudo_dir=pseudo_dir,
                    pseudopotentials=pseudopotentials,
                    executable=executable,
                    balsam_exe_settings=balsam_exe_settings,
                    calc_keywords=calc_keywords,
                    creation_dir=creation_dir
                ))
            c.close()
        r.close()

##############################
# Submit jobs and execute it #
##############################
    def exe(self, parent_job, job_script, cores=1):
        ''' TODO Docstring to be written '''
        from balsam.launcher.dag import BalsamJob
        from os import getcwd
        cwd = getcwd()
        try:
            job_number = str(int(job_script[0:1]))
            workflow_name = yamlfile+facetpath+job_number
        except ValueError:
            workflow_name = yamlfile+facetpath
        job_to_add = BalsamJob(
                name=job_script,
                workflow=workflow_name,
                application=self.myPython.name,
                args=cwd+'/'+job_script,
                ranks_per_node=cores,
                input_files='',
                node_packing_count=64,
                user_workdir=cwd
        )
        job_to_add.save()
        if parent_job != '':
            from balsam.launcher.dag import add_dependency
            try:
                add_dependency(parent_job, job_to_add)  # parent, child
            except ValueError:
                dependency = str(int(parent_job[0:1]))
                dependency_workflow_name = yamlfile+facetpath+dependency
                # print(dependency_workflow_name)
                BalsamJob = BalsamJob
                pending_simulations = BalsamJob.objects.filter(
                    workflow__contains=dependency_workflow_name
                ).exclude(state='JOB_FINISHED')
                for job in pending_simulations:
                    add_dependency(job, job_to_add)  # parent, child
        return job_to_add

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
            WorkFlowDir = str(WorkFlowDir)
            WorkFlowDirs.append(WorkFlowDir)
        # check if there is a optimized slab in the WorkFlowDirs
        is_xyz = any('xyz' in WorkFlowDir for WorkFlowDir in WorkFlowDirs)
        # error handling if only slab and/or facetpath dir presented
        # and no previous calculations
        # e.g. ['.../Cu_100_slab_opt.xyz', '.../Cu_100']
        # return (False, ) in that case
        if len(WorkFlowDirs) <= 2 and is_xyz:
            print('only one element, probably .xyz of the slab. Yes')
            return (False, )
        # error handling if there is no previous minima calculations
        # and slab was not optimized
        if not WorkFlowDirs:
            return (False, )
        # go through all dirs and look for the match
        for WorkFlowDir in WorkFlowDirs:
            try:
                results = self.check_if_path_to_out_files_exists(
                    WorkFlowDir, species
                )
            except ValueError:
                # if False, I have only one value to unpack, so a workaround
                # check_out_files = ''
                continue
            else:
                check_out_files, path_to_outfiles = results
                # if there is a match, break the loop
                if check_out_files:
                    break
        # a directory to the DFT calculation (unique_minima_dir) for a given
        # species is generated by combining the first element of the splitted
        # path to outfiles,
        # i.e.['*/Cu_111/minima/','H_01_relax.out'] so the ('*/Cu_111/minima/'
        # part) with the name of the species.
        # Finally the path is like:
        # '*/Cu_111/minima/H'

        # If species were previously calculated, return True and paths
        try:
            if path_to_outfiles:
                unique_minima_dir = os.path.join(
                        os.path.split(path_to_outfiles[0])[0], species)
                return True, unique_minima_dir, path_to_outfiles
            else:
                return (False, )
        except UnboundLocalError:
            return (False, )

    def run_slab_optimization(self):
        ''' Submit slab_optimization_job '''
        self.slab_opt_job = self.exe('', slab_opt, cores=1)
        # submit slab_optimization_job 1 task probably, was 48 originally

    def run_opt_surf_and_adsorbate(self):
        ''' Run optmization of adsorbates on the surface '''
        return self.exe(self.slab_opt_job, SurfaceAdsorbate)

    def run_opt_surf_and_adsorbate_no_depend(self):
        ''' Run optmization of adsorbates on the surface
            if there is no dependency on other jobs '''
        return self.exe('', SurfaceAdsorbate)

    def run_ts_estimate(self, dependent_job):
        ''' Run TS estimation calculations '''
        TSxtb = inputR2S.TSxtbScript
        return self.exe(dependent_job, TSxtb)

    def run_ts_estimate_no_depend(self):
        ''' Run TS estimate calculations if there is
            no dependency on other jobs '''
        TSxtb = inputR2S.TSxtbScript
        return self.exe('', TSxtb)

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
            check_sp = self.check_if_minima_already_calculated(
                currentDir, species, facetpath)
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
        self.slab_exists = self.check_if_slab_opt_exists()
        if self.slab_exists[0]:
            src = self.slab_exists[1]
            dst = os.getcwd()
            try:
                shutil.copy2(src, dst)
                self.slab_opt_job = ''
            except shutil.SameFileError:
                pass

    def execute(self):
        ''' The main executable

        TODO DEBUG -- it could be a bit buggy
        '''
        # all_species_checked is a list of tuples (bool, path), if bool=True
        # otherwise (bool, )
        all_species_checked = self.check_all_species()
        # It more convenient to have a list of bools
        sp_check_list = [
            False for species in all_species_checked if not species[0]]

        if optimize_slab:
            # check for slab
            is_slab = self.check_if_slab_opt_exists()[0]
            # if slab found in previous calculation, copy it
            if is_slab:
                self.copy_slab_opt_file()
            else:
                # If the code cannot locate optimized slab .xyz file,
                # a slab optimization will be launched.
                self.run_slab_optimization()
            # check whether species were already calculated
            if all(sp_check_list):
                # If all are True, start by generating TS guesses and run
                # the penalty function minimization
                self.run_ts_estimate_no_depend()
            else:
                # If any of sp_check_list is False
                # run optimization of surface + reactants; surface + products
                #
                # TODO: To be debugged - I need to think about a method to run
                # run_opt_surf_and_adsorbate()
                # or
                # run_opt_surf_and_adsorbate_no_depend()
                # depending whether slab opt was done perform by the workflow
                # check if slab was calculated in this run.
                try:
                    self.run_opt_surf_and_adsorbate()
                except NameError:
                    self.run_opt_surf_and_adsorbate_no_depend()
                # if os.path.isfile('00_set_up_slab_opt.py.out'):
                #     self.run_opt_surf_and_adsorbate()
                #     print('depend')
                # else:
                #     # Otherwise run without dependencies
                #     self.run_opt_surf_and_adsorbate_no_depend()
                #     print('nodepend')
                # run calculations to get TS guesses
                self.run_ts_estimate('01')
        else:
            # this is executed if user provide .xyz with the optimized slab
            # check whether sp1 and sp2 was already calculated
            if self.check_if_slab_opt_exists()[0]:
                pass
            else:
                raise FileNotFoundError(
                    'It appears that there is no slab_opt.xyz file'
                )
            if all(sp_check_list):
                # If all minimas were calculated some time age for the other
                # reactions, rmgcat_to_sella will use that calculations.
                # The code can start from TSxtb
                self.exe('', TSxtb)
            else:
                # run optimization of surface + reactants; surface + products
                # May need to put a post process on surface adsorbate
                # to call the next step
                # wait until optimization of surface + reactants; surface
                # + products finish and submit calculations to get TS guesses
                self.exe('', SurfaceAdsorbate)
                # wait until optimization of surface + reactants;
                # surface + products finish and submit calculations
                # to get TS guesses
                self.exe('01', TSxtb)
        # search for the 1st order saddle point
        self.exe('02', TS)
        # for each distinct TS, run IRC calculations
        self.exe('03', IRC)
        # run optimizataion of both IRC (forward, reverse) trajectory
        self.exe('04', IRCopt)
