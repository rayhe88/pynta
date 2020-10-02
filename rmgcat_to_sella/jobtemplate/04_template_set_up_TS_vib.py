#!/usr/bin/env python3
import os

from pathlib import Path

from rmgcat_to_sella.vib import AfterTS

from balsam.launcher.dag import BalsamJob, add_dependency

facetpath = '{facetpath}'
slab = '{slab}'
repeats = {repeats}
yamlfile = '{yamlfile}'
pytemplate = '{pytemplate}'
pseudo_dir = '{pseudo_dir}'
pseudopotentials = {pseudopotentials}
balsam_exe_settings = {balsam_exe_settings}
calc_keywords = {calc_keywords}
creation_dir = '{creation_dir}'
rxn = {rxn}
rxn_name = '{rxn_name}'
cwd = Path.cwd().as_posix()
path_to_ts_vib = os.path.join(
    facetpath, rxn_name, 'TS_estimate_unique_vib')

after_ts = AfterTS(facetpath, yamlfile, slab, repeats)
after_ts.set_up_ts_vib(rxn, pytemplate, balsam_exe_settings,
                       calc_keywords, creation_dir, pseudopotentials,
                       pseudo_dir)

workflow_name = facetpath + '_04_' + rxn_name
dependency_workflow_name = facetpath + '_03_' + rxn_name

pending_simulations = BalsamJob.objects.filter(
    workflow__contains=dependency_workflow_name
).exclude(state="JOB_FINISHED")


for py_script in Path(path_to_ts_vib).glob('*.py'):
    job_dir, script_name = os.path.split(str(py_script))
    job_to_add = BalsamJob(
        name=script_name,
        workflow=workflow_name,
        application='python',
        args=cwd + '/' + str(py_script),
        input_files='',
        user_workdir=job_dir,
        node_packing_count=48,
        ranks_per_node=1,
    )
    job_to_add.save()
    # all job_to_add_ are childs of 02 job for a given reaction
    for job in pending_simulations:
        add_dependency(job, job_to_add)  # parent, child
