# MC generation in CMS

## ⚙️ Overview

MC generation in CMS follows a standard sequence:

**Gridpack → LHEGS → Premix → AODSIM → MINIAODSIM → NANOAODSIM**

These steps include event generation (e.g., MadGraph), parton showering and hadronization (Pythia), detector simulation (GEANT4 via CMSSW), and full reconstruction. Each step is configured through CMSSW fragments, and production is aligned with centrally defined campaign configurations.  Users generate gridpacks using the `gridpack_generation.sh` script, specifying the model and process. For **central production**, the gridpack, Pythia fragment, number of events, and other metadata are provided to the NPS MC contact. For **local validation**, the gridpack is processed with `cmsDriver.py` to create GEN-SIM or full AOD workflows.

Check out the [Working example](#working-example) section containing an example of production and local validation of one gridpack.

## 📋 Prerequisites

- Access to CMS computing grid (lxplus).
- Access to CRAB client and gridpack tools.
- A BSM model UFO file (contact a theorist for this).
- Required cards/fragments in correct format (discuss this with the NPS MC contact).

## 📖 TWikis to read beforehand
- Basic MadGraph tutorial: [TWiki> CMSPublic Web>WebPreferences>MadgraphTutorial](https://twiki.cern.ch/twiki/bin/view/CMSPublic/MadgraphTutorial)
- Gridpack production main page: [TWiki>CMS Web>GeneratorMain](https://twiki.cern.ch/twiki/bin/view/CMS/GeneratorMain#How_to_produce_gridpacks)
- MadGraph tutorial in CMSSW: [TWiki> CMS Web>GeneratorMain>QuickGuideMadGraph5aMCatNLO](https://twiki.cern.ch/twiki/bin/view/CMS/QuickGuideMadGraph5aMCatNLO)
- Instructions on how to use the fragments: [TWiki> CMS Web>GeneratorMain>GitRepositoryForGenProduction](https://twiki.cern.ch/twiki/bin/viewauth/CMS/GitRepositoryForGenProduction)

## 🛠️ Setting up
To begin, clone the `genproductions` repository corresponding to your target campaign. For Run-3 samples, use the following.
```
git clone https://github.com/cms-sw/genproductions.git --depth=1
```
For Run-2 Ultra Legacy (UL) samples, clone the `mg265UL` branch instead.
```
git clone https://github.com/cms-sw/genproductions.git --depth=1 -b mg265UL
```
It will create a `genproductions` directory organized in the following way.
```
genproductions
├── bin                  # Scripts for generating gridpacks
│   ├── Herwig7
│   ├── JHUGen
│   ├── MadGraph5_aMCatNLO
│   ├── Powheg
│   └── Sherpa
├── genfragments        # Campaign-specific CMSSW fragments for processing gridpacks
│   ├── FourteenTeV
│   └── ThirteenTeV
├── MetaData            # PDF lists and metadata for various campaigns
├── README.md
└── Utilities           # Cross section calculator and other helper scripts
```

We will be working with **MadGraph**, so let’s first understand the layout of the `MadGraph5_aMCatNLO` directory.
```
genproductions/bin/MadGraph5_aMCatNLO
├── cards
├── gridpack_generation.sh
├── macros
├── patches
├── PLUGIN
├── runcmsgrid_LO.sh
├── runcmsgrid_NLO.sh
├── submit_cmsconnect_gridpack_generation.sh
├── submit_cmsconnect_gridpack_generation_singlejob.sh
├── submit_condor_gridpack_generation.sh
├── submit_gridpack_generation_local.sh
├── submit_gridpack_generation.sh
└── Utilities
```
### 🔍 Key things to note

-  **`cards/`**  
    This is where you create a new directory for your process (e.g., `VLLD_NLO_M1000`) and place the necessary MadGraph cards:
    -   `*_proc_card.dat` – defines the process (e.g., `generate p p > ell ell`)
    -   `*_run_card.dat` – sets generator-level parameters (cuts, beam energy, etc.)
    -   `*_customizecards.dat` – used to override model parameters like masses and couplings
    -   `*_extramodels.dat` – **only needed if you're using a BSM model**, and should contain the name of your UFO model tarball (e.g., `VLLD_NLO.tar.gz`)
       
-  **`gridpack_generation.sh`**  
    Core script that runs MadGraph, applies patches, handles model import, and outputs the final gridpack (`.tar.xz`). You'll run this directly or via a wrapper.
    
-  **`submit_gridpack_generation_local.sh`**  
    Convenience script that wraps around `gridpack_generation.sh`. Automatically sets paths and handles environment setup for local generation.

### ⚛️ VLL models:

-   **Old Model**  
    🔗 [cms-project-generators.web.cern.ch](https://cms-project-generators.web.cern.ch/cms-project-generators/)  
    Both **VLL Doublet** and **VLL Singlet** are contained in a single `.tgz` UFO model archive.
    The distinction is made using the `isospin` parameter:
    
    -  VLLD: `isospin = -0.5` 
    -  VLLS: `isospin = 0.0` 
    
    While defining decay modes of the particles, be very careful and explicit.
	✅ This model is already available in the central repository and ready to use.
        
-   **New Model**  
    🔗 [github.com/prudhvibhattiprolu/VLL-UFOs](https://github.com/prudhvibhattiprolu/VLL-UFOs)  
    Provides **separate UFO models** for VLLD and VLLS. Better clarity.
    ⚠️ This model is not available in the central repository at the moment. It needs to be put there beforehand.

> ✅ **Recommendation**: Use the _new model_ from GitHub for current and future productions, unless there's a specific legacy reason to stick to the old model. However, becfore central production, make sure that it is kept in the [cms-project-generators](https://cms-project-generators.web.cern.ch/cms-project-generators/) directory.

## 📇Card generation:
Create a new directory inside `genproductions/bin/MadGraph5_aMCatNLO/cards/` named, for example, `VLLD_ele_M100` and place your `proc_card.dat` inside this directory with the following content:
```python
import model VLL
define L = lp lp~
define N = vlp vlp~
define lepton = e+ e- ve ve~ #Taken from JSON

generate p p > L L, (L > z lepton), (L > h lepton)      #Pair production
add process p p > N N, (N > w+ lepton), (N > w- lepton) #Pair production
add process p p > L N, (L > z lepton), (L > h lepton), (N > w+ lepton), (N > w- lepton) #Associated production

output VLLD_ele_M100 -nojpeg
```
Also include the following files in the same directory.
- `*_run_card.dat`: defines generation settings (e.g. number of events, cuts).
- `*_customizecards.dat`: sets benchmark masses, couplings, etc.
- `*_extramodels.dat`: one line listing the model archive name without extensions. (For example, `VLL`.)

### 🤖 Automation:
All the necessary information regarding the models and their mass points is kept in the `modeldict.yaml` file. `generate_cards_old.py` takes the old VLL model, some template cards from `templates/`, and generates all the cards necessary for gridpack production. After the cards are produced, they can be transferred to the  `genproductions/bin/MadGraph5_aMCatNLO/cards/` directory.

- Check the template cards before running this automated script.
- Template cards must contain all placeholder variables like `MASS`, `COUPLING`, etc., which are automatically replaced.
- The `modeldict.yaml` file should include the model name, coupling type, and a list of mass points.  
- Make sure to put the correct beam energy (6500 for Run-2, 6800 for Run-3) in the template `run_card.dat`.

##  🚀 Working example

In the following section, I am using the `VLLD_ele_M100` model as an example and producing and validating a gridpack from scratch for Run2-2018 campaign.

### 📦Gridpack Generation (Run-2 UL)

#### Step 1: Setting up the right environment
```bash
source /cvmfs/cms.cern.ch/cmsset_default.sh
cmssw-el7
echo $SCRAM_ARCH
```
⚠️ _Note_: The `lxplus7` container can be significantly slower than `lxplus8`

#### Step 2: Getting the correct `cms-sw/genproductions` repo
Make sure to clone the UL-specific branch,  **mg265UL**, which is tailored for Run-2 UL production using MadGraph 2.6.5. It automatically picks up the right CMSSW release.
```bash
git clone https://github.com/cms-sw/genproductions.git --depth=1 -b mg265UL
cd genproductions/bin/MadGraph5_aMCatNLO/
chmod +x gridpack_generation.sh
```

#### Step 3: Putting the right cards in the `genproductions/bin/MadGraph5_aMCatNLO/cards` directory
Copy your prepared card directory (which includes `proc_card.dat`, `run_card.dat`, `extramodels.dat`, and `customizecards.dat`) into the `cards/` subdirectory.
```bash
cp -r <path_to_automated_cards/VLLD_ele_M100> cards/.
```

#### Step 4: Running the gridpack production tool
Run the gridpack generation script with the process name and card path. This generates the gridpack in the present working directory.
```bash
./gridpack_generation.sh VLLD_ele_M100 cards/VLLD_ele_M100
```
---
### 🧪 Gridpack validation (locally)

Bring the test-gridpack to a work area and unpack it. It will produce the necessary scripts in the work area.
```bash
cp VLLD_ele_M100_slc7_amd64_gcc700_CMSSW_10_6_19_tarball.tar.xz <work-directory>
cd <work-directory>
mkdir VLLD_ele_M100
tar -xf VLLD_ele_M100_slc7_amd64_gcc700_CMSSW_10_6_19_tarball.tar.xz -C VLLD_ele_M100
```
After unpacking, the work directory should look like this.
```
├── VLLD_ele_M100                  → Unpacked gridpack directory
│   ├── InputCards                 → MadGraph input cards
│   ├── gridpack_generation.log    → Log from gridpack creation
│   ├── merge.pl                   → Script to merge event files
│   ├── mgbasedir                  → MadGraph base setup
│   ├── process                    → Matrix elements and process data
│   └── runcmsgrid.sh              → Script to generate events
└── VLLD_ele_M100_slc7_amd64_gcc700_CMSSW_10_6_19_tarball.tar.xz
```

#### Step 1: Producing LHE
Once the gridpack has been extracted, parton-level events in LHE (Les Houches Event) format can be produced using the `runcmsgrid.sh` script. This script is included inside the unpacked gridpack directory and serves as the interface to MadGraph, MadSpin (if applicable), and Pythia (if configured). It prepares the run environment, executes the event generation workflow, and writes out a `cmsgrid_final.lhe` file.

To run the script for a small test sample of events:
```bash
cd VLLD_ele_M100
./runcmsgrid.sh 100 12345 4
```
- First argument: number of events.
- Second argument: random seed.
- Third argument: number of threads or jobs.

This also produces a CMSSW directory and sets up the necessary environment for further processing.

#### Step 2: Producing GEN-SIM
This step takes the parton-level LHE events and runs hadronization and particle showering using Pythia8 to produce GEN-SIM files that simulate particles and their interactions with the detector. A CMSSW configuration is required for this step.
First, set up the CMSSW environment and directory structure as follows.
```bash
cd CMSSW_10_6_19/src/
cmsenv
mkdir -p Configuration/GenProduction/python
```
The `Configuration/GenProduction/python` directory is used to store the fragment (configuration script) describing how to hadronize the LHE events. The directory structure is important because `cmsDriver.py` (configuration maker tool) expects fragments to be in the Python path under this namespace. Here is an example of a hadronizer, **without using externalLHEProducer** (since we are testing a local LHE file).
```python
import FWCore.ParameterSet.Config as cms
from Configuration.Generator.Pythia8CommonSettings_cfi import *
from Configuration.Generator.MCTunes2017.PythiaCP5Settings_cfi import *
from Configuration.Generator.PSweightsPythia.PythiaPSweightsSettings_cfi import *

generator = cms.EDFilter("Pythia8ConcurrentHadronizerFilter",
    maxEventsToPrint = cms.untracked.int32(1),
    pythiaPylistVerbosity = cms.untracked.int32(1),

    pythiaHepMCVerbosity = cms.untracked.bool(False),
    comEnergy = cms.double(13000.),
    PythiaParameters = cms.PSet(
        pythia8CommonSettingsBlock,
        pythia8CP5SettingsBlock,
        pythia8PSweightsSettingsBlock,
        parameterSets = cms.vstring('pythia8CommonSettings',
                                    'pythia8CP5Settings',
                                    'pythia8PSweightsSettings',
                                    )
    )
)
```
Once the fragment is in place, compile the setup.
```bash
scram b -j8
which cmsDriver.py
```
Use `cmsDriver.py` to create a configuration file that prepares the GEN-level output from LHE input. Adjust filenames and settings as needed.
```bash
cmsDriver.py \
  Configuration/GenProduction/python/myfragment.py \
  --filein file:../../cmsgrid_final.lhe \
  --fileout file:VLLD_ele_M100_GENSIM.root \
  --eventcontent RAWSIM \
  --datatier GEN-SIM \
  --beamspot Realistic25ns13TeVEarly2018Collision \
  --step GEN,SIM \
  --python_filename cfg_1_GENSIM.py \
  --era Run2_2018 \
  --mc --geometry \
  DB:Extended \
  --no_exec --customise \
  Configuration/DataProcessing/Utils.addMonitoring \
  --conditions 106X_upgrade2018_realistic_v15 \
  -n 10
```
This generates a config file `cfg_1_GENSIM.py` without executing it (`--no_exec`). This is important for debugging purposes. Finally, run the generation step.
```bash
cmsRun cfg_1_GENSIM.py
```
This will produce a GEN-SIM ROOT file named `VLLD_ele_M100_GENSIM.root` from the LHE input, suitable for the next simulation steps.

#### Step 3: Producing DIGIRAW
In this step, the simulated detector hits are converted into raw detector data format, and this is where pileup interactions can be added by overlaying minimum bias events on top of the hard scattering. Access to pileup datasets from DBS requires a valid VOMS proxy. In this example, I am not providing a pileup dataset.
```bash
cmsDriver.py \
  step1 \
  --filein file:VLLD_ele_M100_GENSIM.root \
  --fileout file:VLLD_ele_M100_DIGIRAW.root \
  --eventcontent FEVTDEBUGHLT \
  --datatier GEN-SIM-DIGI-RAW \
  --step DIGI,L1,DIGI2RAW,HLT:@relval2018 \
  --nThreads 8 \
  --python_filename cfg_2_DIGIRAW.py \
  --era Run2_2018 \
  --mc --geometry \
  DB:Extended \
  --no_exec --customise \
  Configuration/DataProcessing/Utils.addMonitoring \
  --conditions 106X_upgrade2018_realistic_v15 \
  -n 10
```
```bash
cmsRun cfg_2_DIGIRAW.py
```

#### Step 4: Producing AOD
In this step, the full detector reconstruction is performed on the RAW or DIGIRAW data, producing reconstructed physics objects such as tracks, jets, electrons, and muons. This completes the previous digitization step and produces fully analysis-ready objects. That’s why the `step2` argument is specified in the `cmsDriver.py` command, indicating the reconstruction stage. **The configuration for `step2` should contain the same settings as `step1` to ensure consistency**.
```bash
cmsDriver.py \
  step2 \
  --filein file:VLLD_ele_M100_DIGIRAW.root \
  --fileout file:VLLD_ele_M100_AOD.root \
  --eventcontent AODSIM \
  --runUnscheduled --datatier \
  AODSIM \
  --step RAW2DIGI,L1Reco,RECO,RECOSIM,EI \
  --nThreads 8 \
  --python_filename cfg_3_AOD.py \
  --era Run2_2018 \
  --mc --geometry \
  DB:Extended \
  --no_exec --customise \
  Configuration/DataProcessing/Utils.addMonitoring \
  --conditions 106X_upgrade2018_realistic_v15 \
  -n 10
```
```bash 
cmsRun cfg_3_AOD.py
```

#### Step 5: Producing MINIAOD
MINIAOD is a reduced format derived from AOD where reconstruction is not redone but the data is skimmed and slimmed to contain only essential reconstructed objects and variables. Some high-level corrections and possibly DNN-based identification variables can be added at this stage.
```bash
cmsDriver.py \
  step1 \
  --filein file:VLLD_ele_M100_AOD.root \
  --fileout file:VLLD_ele_M100_MINIAOD.root \
  --eventcontent MINIAODSIM \
  --runUnscheduled --datatier \
  MINIAODSIM \
  --step PAT \
  --nThreads 8 \
  --python_filename cfg_4_MINIAOD.py \
  --era Run2_2018 \
  --mc --geometry \
  DB:Extended \
  --no_exec --customise \
  Configuration/DataProcessing/Utils.addMonitoring \
  --conditions 106X_upgrade2018_realistic_v15 \
  -n 10
```
```bash
cmsRun cfg_4_MINIAOD.py
```

#### Step 6: Producing NanoAOD
NanoAOD further reduces the data size for fast physics analysis, containing selected reconstructed objects and variables, often including DNN outputs for particle identification or event classification. No reconstruction is performed here; it uses the objects produced in previous steps.
```bash
cmsDriver.py \
  step1 \
  --filein file:VLLD_ele_M100_MINIAOD.root \
  --fileout file:VLLD_ele_M100_NANOAOD.root \
  --eventcontent NANOAODSIM \
  --datatier NANOAODSIM \
  --step NANO \
  --nThreads 8 \
  --python_filename cfg_5_NANOAOD.py \
  --era Run2_2018,run2_nanoAOD_106Xv1 \
  --mc --geometry \
  DB:Extended \
  --no_exec --customise \
  Configuration/DataProcessing/Utils.addMonitoring \
  --conditions 106X_upgrade2018_realistic_v15 \
  -n 10
```
```bash
cmsRun cfg_5_NANOAOD.py
```

---

### 🤖 Automation
Once the LHE file is generated, I have automated the subsequent steps using the python script `generate_config.py` This can be run as follows.
```bash
python3 generate_config.py
```
Available options:
- `--n`: _(optional)_ Number of events to process per step. Default is 10.
- `--gen`: _(optional)_ Run only the GEN step.  
- `--digiraw`: _(optional)_ Run only the DIGIRAW step.  
- `--hlt`: _(optional)_ Run only the HLT step.  
- `--reco`: _(optional)_ Run only the RECO step.   
- `--miniaod`: _(optional)_ Run only the MINIAOD step.
- `--nanoaod`: _(optional)_ Run only the NANOAOD step.

If no step options (`--nanoaod`, `--miniaod`, `--digiraw`) are specified, **all steps will be run** sequentially.

Example configuration files can be found in the [`example_configs/`](example_configs/) directory of this repository.

---

This complete local chain ensures that the gridpack is not only producing events but that these events are fully compatible with CMS simulation and analysis workflows. It helps catch potential issues early, saving time and resources in large-scale productions.

## 🌏 Central Production
![Work pending](https://img.shields.io/badge/status-work%20pending-red)  
After generating and validating the gridpack locally, submit it to the relevant NPS MC contact along with the model archive and cards. The central team will handle fragment preparation, validation, and submission to the grid.

## 📚 References and important links
1. N. Kumar and S. P. Martin, “Vectorlike Leptons at the Large Hadron Collider,” Phys. Rev. D 92, no.11, 115018 (2015) [arXiv:1510.03456](https://arxiv.org/abs/1510.03456)
2. P. N. Bhattiprolu and S. P. Martin, "Prospects for vectorlike leptons at future proton-proton colliders," Phys. Rev. D 100, no.1, 015033 (2019) [arXiv:1905.00498](https://arxiv.org/abs/1905.00498).
