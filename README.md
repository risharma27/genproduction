# MC generation in CMS

### ⚙️ Overview

MC generation in CMS follows a standard sequence:

**Gridpack → LHEGS → Premix → AODSIM → MINIAODSIM → NANOAODSIM**

These steps include event generation (e.g., MadGraph), parton showering and hadronization (Pythia), detector simulation (GEANT4 via CMSSW), and full reconstruction. Each step is configured through CMSSW fragments, and production is aligned with centrally defined campaign configurations.

### 🧑‍💻 User Workflow for new-physics samples

Users generate gridpacks using the `gridpack_generation.sh` script, specifying the model and process. For **central production**, the gridpack, Pythia fragment, number of events, and other metadata are provided to the NPS MC contact. For **local validation**, the gridpack is processed with `cmsDriver.py` to create GEN-SIM or full AOD workflows. Jobs are submitted using CRAB, with fragments and configs matching the target campaign.

## 📋 Prerequisites

- A CMSSW release aligned with the target campaign.
- Active grid proxy (`voms-proxy-init`).
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

-   **`cards/`**  
    This is where you create a new directory for your process (e.g., `VLLD_NLO_M1000`) and place the necessary MadGraph cards:    
    -   `*_proc_card.dat` – defines the process (e.g., `generate p p > ell ell`)
    -   `*_run_card.dat` – sets generator-level parameters (cuts, beam energy, etc.)
    -   `*_customizecards.dat` – used to override model parameters like masses and couplings
    -   `*_extramodels.dat` – **only needed if you're using a BSM model**, and should contain the name of your UFO model tarball (e.g., `VLLD_NLO.tar.gz`)
       
-   **`gridpack_generation.sh`**  
    Core script that runs MadGraph, applies patches, handles model import, and outputs the final gridpack (`.tar.xz`). You'll run this directly or via a wrapper.
    
-   **`submit_gridpack_generation_local.sh`**  
    Convenience script that wraps around `gridpack_generation.sh`. Automatically sets paths and handles environment setup for local generation.

### VLL models:

-   **Old Model**  
    🔗 [cms-project-generators.web.cern.ch](https://cms-project-generators.web.cern.ch/cms-project-generators/)  
    Both **VLL Doublet** and **VLL Singlet** are contained in a single `.tgz` UFO model archive.
    The distinction is made using the `isospin` parameter:
    
    -   VLLD: `isospin = -0.5` 
    -   VLLS: `isospin = 0.0` 
   
	   While defining decay modes of the particles, be very careful and explicit.
        
-   **New Model**  
    🔗 [github.com/prudhvibhattiprolu/VLL-UFOs](https://github.com/prudhvibhattiprolu/VLL-UFOs)  
    Provides **separate UFO models** for VLLD and VLLS.  Better clarity.

> ✅ **Recommendation**: Use the _new model_ from GitHub for current and future productions, unless there's a specific legacy reason to stick to the old model. However, becfore central production, make sure that it is kept in the [cms-project-generators](https://cms-project-generators.web.cern.ch/cms-project-generators/) directory.

## 📝 Step-by-step Gridpack Production

### 1. Specify the new-physics model

MadGraph needs the BSM model in UFO format to generate events for new-physics processes.
- For **local testing or development**, place the UFO archive (e.g. `VLLD_NLO.tar.gz`) in:
	```
	genproductions/bin/MadGraph5_aMCatNLO/models/
	```
- For **central production within CMS**, the UFO archive must be uploaded to https://cms-project-generators.web.cern.ch/cms-project-generators/. During gridpack generation, the script reads `extramodels.dat`, fetches the specified archive from this URL, and automatically unpacks and installs it in the appropriate location within the gridpack build environment.

### 2. Prepare the process cards
> Note: I automated the card production step.  You can directly run the automated python script described in the [automation](#automation) section below. The following contains instructions for working with one model.
> 
Create a new directory inside `genproductions/bin/MadGraph5_aMCatNLO/cards/` named, for example, `VLLD_ele_M100` and place your `proc_card.dat` inside this directory with the following content:
```python
import model VLL
define L = lp lp~
define N = vlp vlp~
define boson_L = z h
define boson_N = w+ w-
define lepton = e+ e- mu+ mu- ta+ ta- ve ve~ vm vm~ vt vt~
generate p p > L L, (L > boson_L lepton)    #Pair production of L
add process p p > N N, (N > boson_N lepton) #Pair production of N
add process p p > L N, (L > boson_L lepton), (N > boson_N lepton) #Associated production of L and N
output VLLD_ele_M100 -nojpeg
```
Also include the following files in the same directory.
- `*_run_card.dat`: defines generation settings (e.g. number of events, cuts).
- `*_customizecards.dat`: sets benchmark masses, couplings, etc.
- `*_extramodels.dat`: one line listing the model archive name without extensions. (For example, `VLL`.)

### 3. Configure parameter cards

-   **`*_run_card.dat`**  
    Defines generation-level settings such as the number of events, beam energies, kinematic cuts (like `pt` and `eta`), and matching or merging parameters. You can copy a template from similar MC campaigns and adjust it to your needs.
    
-   **`*_customizecards.dat`**  
    Sets benchmark-specific parameters. This includes the masses of new particles, coupling strengths, and isospin (e.g. `-0.5` for doublet and `0.0` for singlet). These values override those in the default `param_card`.
    
-   **`*_extramodels.dat`**  
    Contains a single line specifying the name of the UFO model archive (without the `.tar.gz` or `.tgz` extension).
    
Place these files inside the same card directory (`cards/VLLD_ele_M100/`) alongside your `proc_card.dat`.

---
### 🤖 Automation
All the necessary information regarding the models and their mass points is kept in the `modeldict.yaml` file. `generate_cards_old.py` takes the old VLL model, some template cards from `templates/`, and generates all the cards necessary for gridpack production

---

### 4. Generate the gridpack
#### ⚠️ <span style="color:red;">Warning: proper environment setup is needed.</span>
> Before running the gridpack generation, in case of Run2_UL samples, a proper SLC7 containter is needed. This shell can be loaded by logging into lxplus8 and running the following.
> ```
> source /cvmfs/cms.cern.ch/cmsset_default.sh
>cmssw-el7
>echo $SCRAM_ARCH
> ```

Once the working environment is ready, from the `MadGraph5_aMCatNLO` directory, run the following.
```bash
./gridpack_generation.sh VLLD_ele_M100 cards/VLLD_ele_M100
```
Here, `VLLD_ele_M100` corresponds to the name of the process card (without the `_proc_card.dat` suffix), and `cards/VLLD_ele_M100` is the relative path to the directory containing the cards. This script will set up MadGraph, apply necessary patches, import your model, generate events, and produce the gridpack tarball.

### 5. Verify the output

Once the process finishes, the gridpack will be available as follows.
```
genproductions/bin/MadGraph5_aMCatNLO/cards/VLLD_ele_M100/VLLD_ele_M100_gridpack.tar.xz
```

## 🧪 Local validation of the gridpack

![Under development](https://img.shields.io/badge/status-under%20development-yellow)
After successfully generating the gridpack, it's important to validate it locally before submitting large-scale production jobs. Follow these steps:

- Unpack the gridpack in a separate working directory to maintain a clean environment:
	```bash
	tar -xf cards/VLLD_ele_M100/VLLD_ele_M100_gridpack.tar.xz -C /path/to/validation/dir
	cd /path/to/validation/dir
	```

- Ensure that a compatible CMSSW environment is properly set up.

- **LHE generation:** Execute the embedded run script to generate LHE events locally.
	```bash
	./runcmsgrid_LO.sh <number_of_events>
	```
	This produces an LHE file (typically named `cmsgrid_final.lhe`). Inspect the initial lines of the file to verify correct event generation.
	
![Error: I am stuck here](https://img.shields.io/badge/Error-I%20am%20stuck%20here-red)

- **GEN-SIM step:** Use `cmsDriver.py` to configure and run the GEN-SIM step, which includes parton showering (e.g., with Pythia) and detector simulation (GEANT4). An example command is:
	```python
	cmsDriver.py Configuration/GenProduction/python/your_fragment.py \
	    --filein file:cmsgrid_final.lhe \
	    --fileout file:step1.root \
	    --mc \
	    --eventcontent RAWSIM \
	    --datatier GEN-SIM \
	    --conditions auto:phase1_2022_realistic \
	    --step GEN,SIM \
	    --nThreads 4 \
	    --geometry DB:Extended \
	    --era Run3 \
	    --no_exec \
	    --customise_commands "process.source.numberEventsInLuminosityBlock = cms.untracked.uint32(1000)"
	```
	The fragment, conditions, and era should be adapted to the target campaign. Run the resulting configuration with:
	```
	cmsRun step1.py
	```
- **Subsequent reconstruction steps:** The standard reconstruction chain (**AODSIM**, **MINIAODSIM**, **NANOAODSIM**) can be run in sequence by generating appropriate `cmsDriver.py` configurations and executing them with `cmsRun`. This verifies that the generated events are fully processable through the CMS software stack.

This complete local chain ensures your gridpack is not only producing events but that these events are fully compatible with CMS simulation and analysis workflows. It helps catch potential issues early, saving time and resources in large-scale productions.

## 🌏 Central Production
![Work pending](https://img.shields.io/badge/status-work%20pending-red)
After generating and validating the gridpack locally, submit it to the relevant NPS MC contact along with the model archive and cards. The central team will handle fragment preparation, validation, and submission to the grid.

## 📚 References and important links
1. N. Kumar and S. P. Martin, “Vectorlike Leptons at the Large Hadron Collider,” Phys. Rev. D 92, no.11, 115018 (2015) [arXiv:1510.03456](https://arxiv.org/abs/1510.03456)
2. P. N. Bhattiprolu and S. P. Martin, "Prospects for vectorlike leptons at future proton-proton colliders," Phys. Rev. D 100, no.1, 015033 (2019) [arXiv:1905.00498](https://arxiv.org/abs/1905.00498).