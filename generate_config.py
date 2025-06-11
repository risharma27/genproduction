#!/usr/bin/env python3

import os
import subprocess
import argparse

# Argument parsing
parser = argparse.ArgumentParser()
parser.add_argument("--n", type=int, default=10,      help="Number of events (default: 10)")
parser.add_argument("--gensim", action="store_true",  help="Run GEN-SIM step")
parser.add_argument("--digiraw", action="store_true", help="Run DIGIRAW step")
parser.add_argument("--aod", action="store_true",     help ="Run AOD step")
parser.add_argument("--miniaod", action="store_true", help="Run MINIAOD step")
parser.add_argument("--nanoaod", action="store_true", help="Run NANOAOD step")
args = parser.parse_args()

#---------------------------------------------
## Setup for 2018_UL
logfile = "log_config_scripts.log"
global_tag = "106X_upgrade2018_realistic_v15"
beamspot = "Realistic25ns13TeVEarly2018Collision"
era = "Run2_2018"
nanoaod_era_extension = "run2_nanoAOD_106Xv1"
#---------------------------------------------

step_flags = [args.gensim, args.digiraw, args.aod, args.miniaod, args.nanoaod]
run_all = not any(step_flags)

common_args = [
    "--mc",
    "--geometry", "DB:Extended",
    "--no_exec",
    "--customise", "Configuration/DataProcessing/Utils.addMonitoring",
    "--conditions", global_tag,
    "-n", str(args.n)
]

steps = [
    {
        "name": "GEN-SIM",
        "flag": args.gensim,
        "cmd": [
            "cmsDriver.py", "Configuration/GenProduction/python/myfragment.py",
            "--filein", "file:../../cmsgrid_final.lhe",
            "--fileout", "file:VLLD_ele_M100_GENSIM.root",
            "--eventcontent", "RAWSIM",
            "--datatier", "GEN-SIM",
            "--beamspot", beamspot,
            "--step", "GEN,SIM",
            "--python_filename", "cfg_1_GENSIM.py",
            "--era", era
        ]
    },
    {
        "name": "DIGIRAW",
        "flag": args.digiraw,
        "cmd": [
            "cmsDriver.py", "step1",
            "--filein", "file:VLLD_ele_M100_GENSIM.root",
            "--fileout", "file:VLLD_ele_M100_DIGIRAW.root",
            #"--pileup_input", "dbs:/MinBias_TuneCP5_13TeV-pythia8/RunIIAutumn18GS-102X_upgrade2018_realistic_v9-v1/GEN-SIM",
            "--eventcontent", "FEVTDEBUGHLT",
            #"--pileup", "AVE_25_BX_25ns,{'N': 20}",
            "--datatier", "GEN-SIM-DIGI-RAW",
            "--step", "DIGI,L1,DIGI2RAW,HLT:@relval2018",
            "--nThreads", "8",
            "--python_filename", "cfg_2_DIGIRAW.py",
            "--era", era
        ]
    },
    {
        "name": "AOD",
        "flag": args.aod,
        "cmd": [
            "cmsDriver.py", "step2",
            "--filein", "file:VLLD_ele_M100_DIGIRAW.root",
            "--fileout", "file:VLLD_ele_M100_AOD.root",
            "--eventcontent", "AODSIM",
            "--runUnscheduled",
            "--datatier", "AODSIM",
            "--step", "RAW2DIGI,L1Reco,RECO,RECOSIM,EI",
            "--nThreads", "8",
            "--python_filename", "cfg_3_AOD.py",
            "--era", era
        ]
    },
    {
        "name": "MINIAOD",
        "flag": args.miniaod,
        "cmd": [
            "cmsDriver.py", "step1",
            "--filein", "file:VLLD_ele_M100_AOD.root",
            "--fileout", "file:VLLD_ele_M100_MINIAOD.root",
            "--eventcontent", "MINIAODSIM",
            "--runUnscheduled",
            "--datatier", "MINIAODSIM",
            "--step", "PAT",
            "--nThreads", "8",
            "--python_filename", "cfg_4_MINIAOD.py",
            "--era", era
        ]
    },
    {
        "name": "NANOAOD",
        "flag": args.nanoaod,
        "cmd": [
            "cmsDriver.py", "step1",
            "--filein", "file:VLLD_ele_M100_MINIAOD.root",
            "--fileout", "file:VLLD_ele_M100_NANOAOD.root",
            "--eventcontent", "NANOAODSIM",
            "--datatier", "NANOAODSIM",
            "--step", "NANO",
            "--nThreads", "8",
            "--python_filename", "cfg_5_NANOAOD.py",
            "--era", nanoaod_era_extension
        ]
    }
]

# Clear log file
open(logfile, "w").close()

for step in steps:
    if not run_all and not step["flag"]: continue

    full_cmd = step["cmd"] + common_args

    ## Debugging:
    formatted_cmd = []
    args = iter(full_cmd)
    for arg in args:
        if arg.startswith("-"):
            val = next(args, "")
            formatted_cmd.append(f"{arg} {val} \\")
        else: formatted_cmd.append(f"{arg} \\")
    cmd_string = "\n  ".join(formatted_cmd)
    
    print(f"\033[1;33m\n\n{step['name']}\033[0m")
    print(f"\033[0;33m{cmd_string}\033[0m")
    with open(logfile, "a") as f:
        f.write(f"\n\n### {step['name']} ###")
        f.write(cmd_string + "\n\n")

    try:   subprocess.run(full_cmd, check=True)
    except subprocess.CalledProcessError as e:  print(f"\n\033[91mError while generating {step['name']} config. Check log or stdout for details.\033[0m\n")

print("\nDone!")
