# MC generation in CMS

### ⚙️ Overview

MC generation in CMS follows a standard sequence:

**Gridpack → LHEGS → Premix → AODSIM → MINIAODSIM → NANOAODSIM**

These steps include event generation (e.g., MadGraph), parton showering and hadronization (Pythia), detector simulation (GEANT4 via CMSSW), and full reconstruction. Each step is configured through CMSSW fragments, and production is aligned with centrally defined campaign configurations.

### 🧑‍💻 User Workflow for new-physics samples

Users generate gridpacks using the `gridpack_generation.sh` script, specifying the model and process. For **central production**, the gridpack, Pythia fragment, number of events, and other metadata are provided to the NPS MC contact. For **local validation**, the gridpack is processed with `cmsDriver.py` to create GEN-SIM or full AOD workflows. Jobs are submitted using CRAB, with fragments and configs matching the target campaign.

For a new signal model (e.g. vector-like leptons), the corresponding UFO model must also be provided. This example uses the vector-like lepton model available in [GitHub/blah](#) .

## 📋 Prerequisites

- A CMSSW release aligned with the target campaign.
- Active grid proxy (`voms-proxy-init`).
- Access to CRAB client and gridpack tools.
-  Required cards/fragments in correct format (Dicuss this with the NPS MC contact)

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

## 📝 Step-by-step Gridpack Production

### Specify new-physics model

MadGraph needs the BSM model in UFO format to generate events for new-physics processes.
- For **local testing or development**, place the UFO archive (e.g. `VLLD_NLO.tar.gz`) in:
	```
	genproductions/bin/MadGraph5_aMCatNLO/models/
	```
- For **central production within CMS**, the UFO archive must be uploaded to https://cms-project-generators.web.cern.ch/cms-project-generators/. During gridpack generation, the script reads `extramodels.dat`, fetches the specified archive from this URL, and automatically unpacks and installs it in the appropriate location within the gridpack build environment.

### Prepare your process cards
Create a new directory inside `genproductions/bin/MadGraph5_aMCatNLO/cards/` named, for example, `VLLD_ele_M100` and place your `proc_card.dat` inside this directory with the following content:
```python
import model VLL
define tp = lp lp~
define vtp = vlp vlp~
define boson = w+ w- z h
define ele = e+ e- ve ve~
generate p p > tp tp, (tp > boson ele)
add process p p > vtp vtp, (vtp > boson ele)
add process p p > tp vtp, (tp > boson ele), (vtp > boson ele)
output VLLD_ele_M100 -nojpeg
```
Also include the following files in the same directory.
-  `run_card.dat`: defines generation settings (e.g. number of events, cuts).
-  `customizecards.dat`: sets benchmark masses, couplings, etc.
-  `extramodels.dat`: one line listing the model archive name without extensions. (For example, `VLL`.)

### Configure `run_card.dat` and `param_card.dat`

-   **`run_card.dat`**  
    Controls the overall run parameters like the number of events, beam energy, PDF sets, cuts, and matching settings. You can copy an existing `run_card.dat` from other samples and modify it to suit your needs.
    
-   **`param_card.dat`**  
    Contains model parameters such as masses, widths, and coupling constants. For BSM models, the param card is usually generated automatically from the UFO but can be customized if needed (e.g., to set the mass of the new particles).
    
Place these files inside the same card directory (`cards/VLLD_ele_M100/`) alongside your `proc_card.dat`.

### Generate the gridpack

From the `MadGraph5_aMCatNLO` directory, run:
```bash
./gridpack_generation.sh VLLD_ele_M100 cards/VLLD_ele_M100
```
Here, `VLLD_ele_M100` corresponds to the name of the process card (without the `_proc_card.dat` suffix), and `cards/VLLD_ele_M100` is the relative path to the directory containing the cards. This script will set up MadGraph, apply necessary patches, import your model, generate events, and produce the gridpack tarball.

### Verify the output

Once the process finishes, the gridpack will be available as follows.
```
genproductions/bin/MadGraph5_aMCatNLO/cards/VLLD_ele_M100/VLLD_ele_M100_gridpack.tar.xz
```
    
## 🧪 Local Validation of the Gridpack
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

## 📚 References
1. "Vectorlike leptons at the Large Hadron Collider", [arXiv:1510.03456](https://arxiv.org/abs/1510.03456)